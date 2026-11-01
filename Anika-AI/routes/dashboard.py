from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import Expense
from database.db import db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    total_spent = sum(e.amount for e in expenses)
    total_budget = current_user.budget
    remaining_balance = total_budget - total_spent
    overspending = remaining_balance < 0
    
    categories = {}
    for e in expenses:
        categories[e.category] = categories.get(e.category, 0) + e.amount
        
    return render_template('dashboard/index.html', 
                           expenses=expenses, 
                           categories=categories,
                           total_spent=total_spent,
                           total_budget=total_budget,
                           remaining_balance=remaining_balance,
                           overspending=overspending)

@dashboard_bp.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    amount = float(request.form.get('amount'))
    category = request.form.get('category')
    description = request.form.get('description')
    
    new_expense = Expense(amount=amount, category=category, description=description, user_id=current_user.id)
    db.session.add(new_expense)
    db.session.commit()
    flash('Expense added successfully!', 'success')
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted.', 'success')
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/update_budget', methods=['POST'])
@login_required
def update_budget():
    new_budget = request.form.get('budget', type=float)
    if new_budget and new_budget > 0:
        current_user.budget = new_budget
        db.session.commit()
        flash('Budget updated successfully!', 'success')
    else:
        flash('Invalid budget amount.', 'danger')
    return redirect(url_for('dashboard.index'))
