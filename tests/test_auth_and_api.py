import json
import pytest
from backend.app import create_app
from backend.config import Config
from backend.extensions import db
from backend.models.models import User, Expense, Settlement

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Check if testuser already exists
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="testuser@anika.ai",
                full_name="Test User",
                monthly_budget=50000.0
            )
            user.set_password("securepassword123")
            db.session.add(user)
            db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_password_hashing():
    u = User(username="hashcheck", email="hash@anika.ai")
    u.set_password("mySecretPass")
    assert u.password_hash != "mySecretPass"
    assert u.check_password("mySecretPass") is True
    assert u.check_password("wrongPass") is False

def test_api_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == "healthy"
    assert data['platform'] == "ANIKA-AI"

def test_auth_login_success(client):
    res = client.post('/api/auth/login', json={
        "identifier": "testuser",
        "password": "securepassword123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['username'] == "testuser"

def test_auth_login_invalid_password(client):
    res = client.post('/api/auth/login', json={
        "identifier": "testuser",
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False

def test_auth_register_new_user(client):
    res = client.post('/api/auth/register', json={
        "username": "brandnewuser",
        "email": "brandnew@anika.ai",
        "password": "password123",
        "full_name": "Brand New"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['username'] == "brandnewuser"

def test_create_expense_workflow(client):
    payload = {
        "title": "Team Dinner",
        "merchant_name": "Punjab Grill",
        "total_amount": 4000.0,
        "currency": "INR",
        "category": "Food & Dining",
        "split_strategy": "equal",
        "payer_id": "p1",
        "payer_name": "Chaitu",
        "participants": [
            {"id": "p1", "name": "Chaitu"},
            {"id": "p2", "name": "Ramu"},
            {"id": "p3", "name": "Mohan"},
            {"id": "p4", "name": "Lathi"}
        ],
        "items": [
            {"name": "Dinner Buffet x4", "quantity": 4, "unit_price": 1000.0, "total_price": 4000.0, "category": "Food & Dining"}
        ],
        "splits": [
            {"participant_id": "p1", "participant_name": "Chaitu", "amount": 1000.0, "percentage": 25.0},
            {"participant_id": "p2", "participant_name": "Ramu", "amount": 1000.0, "percentage": 25.0},
            {"participant_id": "p3", "participant_name": "Mohan", "amount": 1000.0, "percentage": 25.0},
            {"participant_id": "p4", "participant_name": "Lathi", "amount": 1000.0, "percentage": 25.0}
        ]
    }
    res = client.post('/api/expenses', json=payload, headers={"X-User-Id": "1"})
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['total_amount'] == 4000.0
    assert len(data['data']['participants']) == 4
    assert len(data['data']['settlements']) == 3

def test_dashboard_api(client):
    res = client.get('/api/dashboard', headers={"X-User-Id": "1"})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert "stats" in data['data']
    assert "daily_trends" in data['data']

def test_budget_api_get_and_post(client):
    # GET
    res_get = client.get('/api/budget', headers={"X-User-Id": "1"})
    assert res_get.status_code == 200
    
    # POST update
    res_post = client.post('/api/budget', json={
        "total_budget": 55000.0,
        "category_budgets": {"Food & Dining": 15000.0}
    }, headers={"X-User-Id": "1"})
    assert res_post.status_code == 200
    data = res_post.get_json()
    assert data['data']['total_budget'] == 55000.0

def test_smartbuy_api(client):
    res = client.post('/api/ai/smartbuy', json={
        "item_name": "Laptop",
        "price": 70000.0,
        "category": "Shopping"
    }, headers={"X-User-Id": "1"})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['item_name'] == "Laptop"
    assert "verdict" in data['data']
    assert "affordability_score" in data['data']
