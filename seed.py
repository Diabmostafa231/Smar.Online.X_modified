"""Run once to create tables and populate sample products:
    python seed.py
"""
from app import app
from models import db, Product

SAMPLE_PRODUCTS = [
    dict(
        name="Aether Wireless Earbuds",
        slug="aether-wireless-earbuds",
        description="Active noise cancelling earbuds with 30-hour battery life and touch controls.",
        category="audio",
        price_cents=12999,
        image_url="https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600",
        stock=40,
        spec_tag="ANC / 30HR",
    ),
    dict(
        name="Pulse Smartwatch Pro",
        slug="pulse-smartwatch-pro",
        description="Fitness smartwatch with heart-rate, SpO2, and 10-day battery.",
        category="wearables",
        price_cents=18999,
        image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600",
        stock=25,
        spec_tag="10-DAY BATT",
    ),
    dict(
        name="Nomad 65W GaN Charger",
        slug="nomad-65w-gan-charger",
        description="Compact 3-port GaN fast charger for laptops, phones, and tablets.",
        category="accessories",
        price_cents=4999,
        image_url="https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600",
        stock=100,
        spec_tag="65W GaN",
    ),
    dict(
        name="Orbit Smart Home Hub",
        slug="orbit-smart-home-hub",
        description="Matter-compatible smart home hub for lights, locks, and sensors.",
        category="smart-home",
        price_cents=8999,
        image_url="https://images.unsplash.com/photo-1558002038-1055907df827?w=600",
        stock=30,
        spec_tag="MATTER",
    ),
    dict(
        name="Vector Mechanical Keyboard",
        slug="vector-mechanical-keyboard",
        description="75% hot-swappable mechanical keyboard with per-key RGB.",
        category="accessories",
        price_cents=10999,
        image_url="https://images.unsplash.com/photo-1595225476474-63038da0473d?w=600",
        stock=18,
        spec_tag="HOT-SWAP",
    ),
    dict(
        name="Halo 4K Webcam",
        slug="halo-4k-webcam",
        description="4K UHD webcam with auto-framing and dual noise-cancelling mics.",
        category="video",
        price_cents=8499,
        image_url="https://images.unsplash.com/photo-1587826080692-f439465ec27a?w=600",
        stock=22,
        spec_tag="4K / 60FPS",
    ),
]

with app.app_context():
    db.create_all()
    for data in SAMPLE_PRODUCTS:
        if not Product.query.filter_by(slug=data["slug"]).first():
            db.session.add(Product(**data))
    db.session.commit()
    print(f"Seeded {Product.query.count()} products.")
