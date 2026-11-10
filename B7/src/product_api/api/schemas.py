from marshmallow import Schema, fields, validate

price = validate.Range(min=0)
stock = validate.Range(min=0)


class ProductOut(Schema):
    id = fields.Int()
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


class ProductIn(Schema):
    sku = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(required=True, validate=price)
    qty_in_stock = fields.Int(load_default=0, validate=stock)


class ProductPatch(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    price_cents = fields.Int(validate=price)
    qty_in_stock = fields.Int(validate=stock)


class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))
