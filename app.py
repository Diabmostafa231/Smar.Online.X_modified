from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from config import Config
from models import db, bcrypt, User, Product, CartItem, Order, OrderItem

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}}, supports_credentials=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def current_user():
    user_id = get_jwt_identity()
    return User.query.get(int(user_id)) if user_id else None


def error(message, status=400):
    return jsonify({"error": message}), status


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/api/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    address = (data.get("address") or "").strip()

    if not full_name or not email or not password:
        return error("full_name, email and password are required")
    if len(password) < 6:
        return error("password must be at least 6 characters")
    if User.query.filter_by(email=email).first():
        return error("an account with this email already exists", 409)

    user = User(full_name=full_name, email=email, address=address)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error("invalid email or password", 401)

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})


@app.get("/api/auth/me")
@jwt_required()
def me():
    user = current_user()
    if not user:
        return error("user not found", 404)
    return jsonify({"user": user.to_dict()})


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@app.get("/api/products")
def list_products():
    category = request.args.get("category")
    search = request.args.get("q")

    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if search:
        like = f"%{search}%"
        query = query.filter(Product.name.ilike(like))

    products = query.order_by(Product.created_at.desc()).all()
    return jsonify({"products": [p.to_dict() for p in products]})


@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return error("product not found", 404)
    return jsonify({"product": product.to_dict()})


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------

@app.get("/api/cart")
@jwt_required()
def get_cart():
    user = current_user()
    items = CartItem.query.filter_by(user_id=user.id).all()
    total = sum(item.product.price_cents * item.quantity for item in items)
    return jsonify({"items": [i.to_dict() for i in items], "total": round(total / 100, 2)})


@app.post("/api/cart")
@jwt_required()
def add_to_cart():
    user = current_user()
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = Product.query.get(product_id)
    if not product:
        return error("product not found", 404)
    if quantity < 1:
        return error("quantity must be at least 1")

    item = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({"item": item.to_dict()}), 201


@app.put("/api/cart/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    user = current_user()
    item = CartItem.query.filter_by(id=item_id, user_id=user.id).first()
    if not item:
        return error("cart item not found", 404)

    data = request.get_json(silent=True) or {}
    quantity = int(data.get("quantity", item.quantity))
    if quantity < 1:
        return error("quantity must be at least 1")

    item.quantity = quantity
    db.session.commit()
    return jsonify({"item": item.to_dict()})


@app.delete("/api/cart/<int:item_id>")
@jwt_required()
def delete_cart_item(item_id):
    user = current_user()
    item = CartItem.query.filter_by(id=item_id, user_id=user.id).first()
    if not item:
        return error("cart item not found", 404)

    db.session.delete(item)
    db.session.commit()
    return jsonify({"deleted": True})


# ---------------------------------------------------------------------------
# Checkout / Orders
# ---------------------------------------------------------------------------

@app.post("/api/checkout")
@jwt_required()
def checkout():
    user = current_user()
    data = request.get_json(silent=True) or {}
    shipping_address = (data.get("shipping_address") or user.address or "").strip()

    cart_items = CartItem.query.filter_by(user_id=user.id).all()
    if not cart_items:
        return error("your cart is empty")
    if not shipping_address:
        return error("shipping_address is required")

    for item in cart_items:
        if item.quantity > item.product.stock:
            return error(f"not enough stock for {item.product.name}")

    order = Order(user_id=user.id, shipping_address=shipping_address, status="placed")
    total_cents = 0
    for item in cart_items:
        order_item = OrderItem(
            product_id=item.product.id,
            product_name=item.product.name,
            unit_price_cents=item.product.price_cents,
            quantity=item.quantity,
        )
        item.product.stock -= item.quantity
        total_cents += item.product.price_cents * item.quantity
        order.items.append(order_item)
        db.session.delete(item)

    order.total_cents = total_cents
    db.session.add(order)
    db.session.commit()

    return jsonify({"order": order.to_dict()}), 201


@app.get("/api/orders")
@jwt_required()
def list_orders():
    user = current_user()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return jsonify({"orders": [o.to_dict() for o in orders]})


@app.get("/api/orders/<int:order_id>")
@jwt_required()
def get_order(order_id):
    user = current_user()
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()
    if not order:
        return error("order not found", 404)
    return jsonify({"order": order.to_dict()})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
