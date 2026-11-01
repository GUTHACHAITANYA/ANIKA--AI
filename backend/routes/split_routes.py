from flask import Blueprint, request, jsonify
from backend.services.split_calculator import SplitCalculator
from backend.utils.helpers import success_response, error_response
from backend.utils.logger import logger

split_bp = Blueprint('splits', __name__, url_prefix='/api/splits')

@split_bp.route('/calculate', methods=['POST'])
def calculate_split():
    """
    Calculates expense shares based on selected split strategy:
    'equal', 'percentage', 'custom', or 'itemized'.
    """
    data = request.get_json() or {}
    total_amount = float(data.get('total_amount') or 0.0)
    participants = data.get('participants') or []
    strategy = (data.get('strategy') or 'equal').lower()

    if total_amount <= 0:
        return error_response("Total amount must be greater than zero.", 400)

    if not participants or len(participants) < 1:
        return error_response("At least one participant is required to split a bill.", 400)

    try:
        if strategy == 'equal':
            splits, summary = SplitCalculator.calculate_equal_split(total_amount, participants)
        elif strategy == 'percentage':
            percentages = data.get('percentages') or {}
            splits, summary = SplitCalculator.calculate_percentage_split(total_amount, participants, percentages)
        elif strategy == 'custom':
            custom_amounts = data.get('custom_amounts') or {}
            splits, summary = SplitCalculator.calculate_custom_split(total_amount, participants, custom_amounts)
        elif strategy == 'itemized':
            items = data.get('items') or []
            tax = float(data.get('tax') or 0.0)
            gst = float(data.get('gst') or 0.0)
            splits, summary = SplitCalculator.calculate_itemized_split(total_amount, participants, items, tax, gst)
        else:
            return error_response(f"Unsupported split strategy '{strategy}'. Supported: equal, percentage, custom, itemized.", 400)

        return success_response({
            'strategy': strategy,
            'splits': splits,
            'summary': summary
        }, "Split calculation completed successfully.")

    except ValueError as ve:
        return error_response(str(ve), 400)
    except Exception as e:
        logger.error(f"Error in split calculation: {e}")
        return error_response("Unable to calculate split. Please verify participant allocations.", 500)
