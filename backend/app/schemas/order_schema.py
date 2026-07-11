from marshmallow import Schema, fields

class StatusHistorySchema(Schema):
    status = fields.Str(required=True)
    note = fields.Str(allow_none=True)
    updated_by = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)

class CustomerSnapshotSchema(Schema):
    name = fields.Str(required=True)
    phone = fields.Str(required=True)

class OrderSchema(Schema):
    id = fields.Method("get_id", dump_only=True)
    order_number = fields.Str(required=True)
    estimated_total = fields.Int(required=True)
    final_quoted_price = fields.Int(allow_none=True)
    status = fields.Str(required=True)
    status_history = fields.List(fields.Nested(StatusHistorySchema), dump_only=True)
    admin_notes = fields.Str(allow_none=True)
    customer_visible_note = fields.Str(allow_none=True)
    customer_snapshot = fields.Nested(CustomerSnapshotSchema, required=True)
    user_id = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    def get_id(self, obj):
        if isinstance(obj, dict):
            return str(obj.get("_id"))
        return str(getattr(obj, "id", None))

class CustomerOrderSchema(OrderSchema):
    class Meta:
        exclude = ("admin_notes",)
