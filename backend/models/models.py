from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from backend.extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default='')
    currency = db.Column(db.String(10), default='INR')
    monthly_budget = db.Column(db.Float, default=30000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    receipts = db.relationship('Receipt', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_insights = db.relationship('AIInsight', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or self.username,
            'currency': self.currency,
            'monthly_budget': self.monthly_budget,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    merchant_name = db.Column(db.String(150), default='General Merchant')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    currency = db.Column(db.String(10), default='INR')
    subtotal = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    gst = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), default='Other')
    payment_method = db.Column(db.String(50), default='UPI / Card')
    split_strategy = db.Column(db.String(50), default='equal') # equal, percentage, custom, itemized
    payer_id = db.Column(db.String(80), default='me')
    payer_name = db.Column(db.String(100), default='Me')
    notes = db.Column(db.Text, default='')
    status = db.Column(db.String(30), default='saved') # draft, saved, settled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('ExpenseItem', backref='expense', lazy=True, cascade='all, delete-orphan')
    participants = db.relationship('Participant', backref='expense', lazy=True, cascade='all, delete-orphan')
    splits = db.relationship('Split', backref='expense', lazy=True, cascade='all, delete-orphan')
    settlements = db.relationship('Settlement', backref='expense', lazy=True, cascade='all, delete-orphan')
    receipt = db.relationship('Receipt', backref='expense', lazy=True, uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'merchant_name': self.merchant_name,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'currency': self.currency,
            'subtotal': self.subtotal,
            'tax': self.tax,
            'gst': self.gst,
            'total_amount': self.total_amount,
            'category': self.category,
            'payment_method': self.payment_method,
            'split_strategy': self.split_strategy,
            'payer_id': self.payer_id,
            'payer_name': self.payer_name,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'items': [item.to_dict() for item in self.items],
            'participants': [p.to_dict() for p in self.participants],
            'splits': [s.to_dict() for s in self.splits],
            'settlements': [st.to_dict() for st in self.settlements]
        }

class ExpenseItem(db.Model):
    __tablename__ = 'expense_items'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    total_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), default='Other')
    assigned_participants = db.Column(db.Text, default='[]') # JSON array of participant keys

    def to_dict(self):
        try:
            assigned = json.loads(self.assigned_participants or '[]')
        except Exception:
            assigned = []
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'category': self.category,
            'assigned_participants': assigned
        }

class Participant(db.Model):
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False, index=True)
    participant_key = db.Column(db.String(50), nullable=False) # 'me', 'p_1', etc.
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(30), default='')
    is_payer = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.participant_key,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_payer': self.is_payer
        }

class Split(db.Model):
    __tablename__ = 'splits'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False, index=True)
    participant_key = db.Column(db.String(50), nullable=False)
    participant_name = db.Column(db.String(100), nullable=False)
    share_amount = db.Column(db.Float, nullable=False)
    share_percentage = db.Column(db.Float, default=0.0)
    item_ids_json = db.Column(db.Text, default='[]')

    def to_dict(self):
        try:
            item_ids = json.loads(self.item_ids_json or '[]')
        except Exception:
            item_ids = []
        return {
            'id': self.id,
            'participant_id': self.participant_key,
            'participant_name': self.participant_name,
            'share_amount': self.share_amount,
            'share_percentage': self.share_percentage,
            'item_ids': item_ids
        }

class Settlement(db.Model):
    __tablename__ = 'settlements'

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False, index=True)
    from_participant_key = db.Column(db.String(50), nullable=False)
    from_name = db.Column(db.String(100), nullable=False)
    to_participant_key = db.Column(db.String(50), nullable=False)
    to_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    paid_at = db.Column(db.DateTime, nullable=True)
    payment_reference = db.Column(db.String(100), default='')

    def to_dict(self):
        return {
            'id': self.id,
            'expense_id': self.expense_id,
            'from_id': self.from_participant_key,
            'from_name': self.from_name,
            'to_id': self.to_participant_key,
            'to_name': self.to_name,
            'amount': self.amount,
            'is_paid': self.is_paid,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'payment_reference': self.payment_reference
        }

class Receipt(db.Model):
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=True, index=True)
    file_path = db.Column(db.String(300), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    mime_type = db.Column(db.String(50), default='image/jpeg')
    file_size = db.Column(db.Integer, default=0)
    raw_extracted_json = db.Column(db.Text, default='{}')
    ocr_confidence = db.Column(db.Float, default=0.95)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            parsed_data = json.loads(self.raw_extracted_json or '{}')
        except Exception:
            parsed_data = {}
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'ocr_confidence': self.ocr_confidence,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'extracted_data': parsed_data,
            'expense_id': self.expense_id
        }

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False) # 1-12
    year = db.Column(db.Integer, nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    category_budgets_json = db.Column(db.Text, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        try:
            cat_budgets = json.loads(self.category_budgets_json or '{}')
        except Exception:
            cat_budgets = {}
        return {
            'id': self.id,
            'month': self.month,
            'year': self.year,
            'total_budget': self.total_budget,
            'category_budgets': cat_budgets,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action_type = db.Column(db.String(80), nullable=False) # 'OCR_UPLOAD', 'SPLIT_SAVED', 'SETTLEMENT_PAID', 'BUDGET_UPDATED'
    description = db.Column(db.String(255), nullable=False)
    metadata_json = db.Column(db.Text, default='{}')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            meta = json.loads(self.metadata_json or '{}')
        except Exception:
            meta = {}
        return {
            'id': self.id,
            'action_type': self.action_type,
            'description': self.description,
            'metadata': meta,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AIInsight(db.Model):
    __tablename__ = 'ai_insights'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    insight_type = db.Column(db.String(80), default='spending_analysis') # 'budget_alert', 'savings_tip', 'anomaly'
    content = db.Column(db.Text, nullable=False)
    recommendations_json = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            recs = json.loads(self.recommendations_json or '[]')
        except Exception:
            recs = []
        return {
            'id': self.id,
            'insight_type': self.insight_type,
            'content': self.content,
            'recommendations': recs,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
