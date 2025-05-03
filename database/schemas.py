# database/schemas.py
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    """Schema for User model validation and serialization"""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    name = fields.Str(required=True)
    phone = fields.Str()
    date_registered = fields.DateTime(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    is_admin = fields.Bool(dump_only=True)

class AddressSchema(Schema):
    """Schema for Address model validation and serialization"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    label = fields.Str(required=True)
    address_line1 = fields.Str(required=True)
    address_line2 = fields.Str()
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    postal_code = fields.Str(required=True)
    phone = fields.Str()
    is_default = fields.Bool()

class CategorySchema(Schema):
    """Schema for Category model validation and serialization"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    description = fields.Str()

class ProductSchema(Schema):
    """Schema for Product model validation and serialization"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    description = fields.Str()
    price = fields.Decimal(required=True, places=2)
    image_path = fields.Str()
    is_available = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    categories = fields.List(fields.Nested(lambda: CategorySchema(only=('id', 'name', 'slug'))))

class CartItemSchema(Schema):
    """Schema for CartItem model validation and serialization"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1, max=10))
    date_added = fields.DateTime(dump_only=True)
    product = fields.Nested(lambda: ProductSchema(only=('id', 'name', 'slug', 'price', 'image_path')))

class OrderItemSchema(Schema):
    """Schema for OrderItem model validation and serialization"""
    id = fields.Int(dump_only=True)
    order_id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(required=True, places=2)
    product = fields.Nested(lambda: ProductSchema(only=('id', 'name', 'slug', 'image_path')))

class OrderSchema(Schema):
    """Schema for Order model validation and serialization"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    status = fields.Str(dump_only=True)
    total_amount = fields.Decimal(required=True, places=2)
    created_at = fields.DateTime(dump_only=True)
    shipping_address_id = fields.Int(required=True)
    delivery_date = fields.Date()
    payment_method = fields.Str()
    payment_status = fields.Str(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema))
    shipping_address = fields.Nested(lambda: AddressSchema())

class DiscountSchema(Schema):
    """Schema for Discount model validation and serialization"""
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    description = fields.Str()
    amount = fields.Decimal(required=True, places=2)
    is_percentage = fields.Bool()
    min_purchase = fields.Decimal(places=2)
    start_date = fields.DateTime()
    end_date = fields.DateTime()
    is_active = fields.Bool()