FROM python:3.12-slim as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -d /app app
COPY --from=builder /app/.venv /app/.venv
COPY wsgi.py gunicorn.conf.py ./
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi:app
USER app
EXPOSE 5000
CMD ["sh", "-c", "flask db upgrade && exec gunicorn -c gunicorn.conf.py wsgi:app"]
