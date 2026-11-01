from flask import Blueprint, render_template, request
# pyrefly: ignore [missing-import]
from flask_login import login_required, current_user
from services.ai_service import analyze_product
from models.models import ProductAnalysis
from database.db import db

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@analysis_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    result = None
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        rating = float(request.form.get('rating', 3.0))
        
        recommendation, score, insights = analyze_product(price, rating, category, current_user.budget)
        
        analysis = ProductAnalysis(
            product_name=product_name, 
            category=category, 
            price=price, 
            recommendation=recommendation, 
            score=score, 
            user_id=current_user.id
        )
        db.session.add(analysis)
        db.session.commit()
        
        result = {
            'product_name': product_name,
            'recommendation': recommendation,
            'score': score,
            'insights': insights
        }
        
    history = ProductAnalysis.query.filter_by(user_id=current_user.id).order_by(ProductAnalysis.date.desc()).all()
    return render_template('dashboard/analyze.html', result=result, history=history)
