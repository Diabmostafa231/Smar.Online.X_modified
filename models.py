from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship("CartItem", backref="user", cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.String(80), nullable=False, default="general")
    price_cents = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False, default="")
    stock = db.Column(db.Integer, nullable=False, default=0)
    spec_tag = db.Column(db.String(60), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            "price": round(self.price_cents / 100, 2),
            "image_url": self.image_url,
            "stock": self.stock,
            "spec_tag": self.spec_tag,
        }


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship("Product")

    def to_dict(self):
        return {
            "id": self.id,
            "product": self.product.to_dict(),
            "quantity": self.quantity,
            "line_total": round(self.product.price_cents * self.quantity / 100, 2),
        }


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(40), nullable=False, default="placed")
    shipping_address = db.Column(db.String(255), nullable=False, default="")
    total_cents = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "shipping_address": self.shipping_address,
            "total": round(self.total_cents / 100, 2),
            "created_at": self.created_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    product_name = db.Column(db.String(160), nullable=False)
    unit_price_cents = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "unit_price": round(self.unit_price_cents / 100, 2),
            "quantity": self.quantity,
            "line_total": round(self.unit_price_cents * self.quantity / 100, 2),
        }
