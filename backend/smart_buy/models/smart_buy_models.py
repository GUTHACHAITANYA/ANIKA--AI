from datetime import datetime
import json
from backend.extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    brand = db.Column(db.String(100), index=True, default='')
    model_name = db.Column(db.String(150), index=True, default='')
    category = db.Column(db.String(100), index=True, default='General')
    image_url = db.Column(db.Text, default='')
    base_mrp = db.Column(db.Float, nullable=False, default=0.0)
    specs_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    offers = db.relationship('ProductOffer', backref='product', lazy=True, cascade='all, delete-orphan')
    price_history = db.relationship('PriceHistory', backref='product', lazy=True, cascade='all, delete-orphan')

    def get_specs(self) -> dict:
        try:
            return json.loads(self.specs_json or '{}')
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'brand': self.brand,
            'model_name': self.model_name,
            'category': self.category,
            'image_url': self.image_url,
            'base_mrp': self.base_mrp,
            'specs': self.get_specs(),
            'offers_count': len(self.offers) if self.offers else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProductOffer(db.Model):
    __tablename__ = 'product_offers'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    platform_id = db.Column(db.String(50), nullable=False, index=True)
    platform_name = db.Column(db.String(100), nullable=False)
    platform_logo = db.Column(db.String(255), default='')
    seller_name = db.Column(db.String(150), default='Authorized Seller')
    product_title = db.Column(db.String(255), nullable=False)
    product_url = db.Column(db.Text, nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False, index=True)
    coupon_discount = db.Column(db.Float, default=0.0)
    bank_discount = db.Column(db.Float, default=0.0)
    cashback = db.Column(db.Float, default=0.0)
    delivery_fee = db.Column(db.Float, default=0.0)
    final_payable_price = db.Column(db.Float, nullable=False, index=True)
    rating = db.Column(db.Float, default=4.2)
    reviews_count = db.Column(db.Integer, default=0)
    availability = db.Column(db.String(50), default='in_stock')
    offer_details = db.Column(db.Text, default='')
    variant_attributes_json = db.Column(db.Text, default='{}')
    is_verified = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)

    def get_variant_attributes(self) -> dict:
        try:
            return json.loads(self.variant_attributes_json or '{}')
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'platform_id': self.platform_id,
            'platform_name': self.platform_name,
            'platform_logo': self.platform_logo,
            'seller_name': self.seller_name,
            'product_title': self.product_title,
            'product_url': self.product_url,
            'original_price': self.original_price,
            'selling_price': self.selling_price,
            'discount_percentage': self.discount_percentage,
            'coupon_discount': self.coupon_discount,
            'bank_discount': self.bank_discount,
            'cashback': self.cashback,
            'delivery_fee': self.delivery_fee,
            'final_payable_price': self.final_payable_price,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'availability': self.availability,
            'offer_details': self.offer_details,
            'variant_attributes': self.get_variant_attributes(),
            'is_verified': self.is_verified,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None
        }

class SearchHistory(db.Model):
    __tablename__ = 'search_histories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    query = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default='All')
    filters_json = db.Column(db.Text, default='{}')
    results_count = db.Column(db.Integer, default=0)
    top_platform = db.Column(db.String(100), default='')
    top_discount_pct = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_filters(self) -> dict:
        try:
            return json.loads(self.filters_json or '{}')
        except Exception:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query': self.query,
            'category': self.category,
            'filters': self.get_filters(),
            'results_count': self.results_count,
            'top_platform': self.top_platform,
            'top_discount_pct': self.top_discount_pct,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PriceHistory(db.Model):
    __tablename__ = 'price_histories'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    platform_id = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'platform_id': self.platform_id,
            'price': self.price,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }

class ShoppingProvider(db.Model):
    __tablename__ = 'shopping_providers'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    website_url = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    requires_auth = db.Column(db.Boolean, default=False)
    status_message = db.Column(db.String(255), default='Active')

    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'website_url': self.website_url,
            'is_active': self.is_active,
            'requires_auth': self.requires_auth,
            'status_message': self.status_message
        }

