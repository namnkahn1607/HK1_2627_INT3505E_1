"""Pagination (offset + keyset/cursor).
Using the requested keys + a unique tie-breaker (id), and resume with
    (k1, k2, id) > (v1, v2, vid)   ==   k1 > v1 OR (k1 = v1 AND k2 > v2) OR (k1 = v1 AND k2 = v2 AND id > vid)
"""
import base64
import json

from sqlalchemy import and_, func, or_, select

from errors import ApiError

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def parse_int(raw, name, minimum=None):
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ApiError(400, "invalid_parameter", f"'{name}' must be an integer", field=name)
    if minimum is not None and value < minimum:
        raise ApiError(400, "invalid_parameter", f"'{name}' must be >= {minimum}", field=name)
    return value


def parse_sort(raw, allowed, default="-id"):
    spec = []
    for part in (raw or default).split(","):
        part = part.strip()
        desc = part.startswith("-")
        name = part[1:] if desc else part
        if name not in allowed:
            raise ApiError(400, "invalid_sort", f"cannot sort by '{name}'", allowed=sorted(allowed))
        if name in [n for n, _ in spec]:
            raise ApiError(400, "invalid_sort", f"duplicate sort key '{name}'")
        spec.append((name, desc))
    if "id" not in [n for n, _ in spec]:
        spec.append(("id", spec[-1][1]))
    return spec


def sort_string(spec):
    return ",".join(("-" if desc else "") + name for name, desc in spec)


def encode_cursor(payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def read_cursor(token, spec, scope):
    try:
        payload = json.loads(base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)))
    except ValueError:  # bad base64, bad UTF-8 and bad JSON are all ValueErrors
        payload = None
    if not isinstance(payload, dict) or not {"s", "f", "v"} <= payload.keys():
        raise ApiError(400, "invalid_cursor", "cursor is malformed")

    if payload.get("s") != sort_string(spec):
        raise ApiError(400, "cursor_sort_mismatch", "cursor was issued for a different sort; restart without cursor")
    if payload.get("f") != scope:
        raise ApiError(400, "cursor_filter_mismatch", "cursor was issued for different filters; restart without cursor")
    values = payload.get("v")
    if not isinstance(values, list) or len(values) != len(spec) or any(type(v) not in (int, str) for v in values):
        raise ApiError(400, "invalid_cursor", "cursor is malformed")
    return values


def keyset_condition(spec, sorts, values):
    branches = []
    for i, (name, desc) in enumerate(spec):
        equal = [sorts[n] == v for (n, _), v in zip(spec[:i], values)]
        col = sorts[name]
        branches.append(and_(*equal, col < values[i] if desc else col > values[i]))
    return or_(*branches)


def paginate(session, stmt, sorts, args, serialize, *, scope=None, default_sort="-id", options=()):
    scope = scope or {}
    strategy = args.get("strategy", "cursor")
    if strategy not in ("cursor", "offset"):
        raise ApiError(400, "invalid_parameter", "'strategy' must be 'cursor' or 'offset'", field="strategy")
    limit = min(parse_int(args.get("limit"), "limit", minimum=1) or DEFAULT_LIMIT, MAX_LIMIT)
    spec = parse_sort(args.get("sort"), sorts, default_sort)
    query = stmt.order_by(*(sorts[n].desc() if d else sorts[n].asc() for n, d in spec))
    page = {"strategy": strategy, "limit": limit}

    if strategy == "offset":
        if "cursor" in args:
            raise ApiError(400, "invalid_parameter", "'cursor' cannot be used with strategy=offset", field="cursor")
        offset = parse_int(args.get("offset"), "offset", minimum=0) or 0
        page["offset"] = offset
        page["total"] = session.scalar(select(func.count()).select_from(stmt.subquery()))
        query = query.offset(offset)
    else:
        if "offset" in args:
            raise ApiError(400, "invalid_parameter", "'offset' cannot be used with strategy=cursor", field="offset")
        if args.get("cursor"):
            values = read_cursor(args["cursor"], spec, scope)
            query = query.where(keyset_condition(spec, sorts, values))

    rows = session.scalars(query.options(*options).limit(limit + 1)).all()  # +1 row tells us hasMore
    has_more = len(rows) > limit
    rows = rows[:limit]
    page["hasMore"] = has_more

    if strategy == "cursor":
        page["nextCursor"] = None
        if has_more:
            last = rows[-1]
            page["nextCursor"] = encode_cursor(
                {"s": sort_string(spec), "f": scope, "v": [getattr(last, sorts[n].key) for n, _ in spec]}
            )
    return {"data": [serialize(r) for r in rows], "pagination": page}
