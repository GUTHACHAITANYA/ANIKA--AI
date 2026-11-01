import pytest
from backend.services.split_calculator import SplitCalculator

def test_equal_split_even_division():
    participants = [{"id": "p1", "name": "Chaitu"}, {"id": "p2", "name": "Ramu"}]
    total = 2000.0
    splits, summary = SplitCalculator.calculate_equal_split(total, participants)
    
    assert len(splits) == 2
    assert splits[0]['amount'] == 1000.0
    assert splits[1]['amount'] == 1000.0
    assert sum(s['amount'] for s in splits) == 2000.0

def test_equal_split_odd_cent_remainder_balanced():
    # 100 / 3 = 33.33333333333333... Must sum to exactly 100.00
    participants = [{"id": "p1", "name": "A"}, {"id": "p2", "name": "B"}, {"id": "p3", "name": "C"}]
    total = 100.00
    splits, summary = SplitCalculator.calculate_equal_split(total, participants)
    
    total_split = sum(s['amount'] for s in splits)
    assert round(total_split, 2) == 100.00
    assert splits[0]['amount'] == 33.34
    assert splits[1]['amount'] == 33.33
    assert splits[2]['amount'] == 33.33

def test_equal_split_four_participants():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"},
        {"id": "p4", "name": "Lathi"}
    ]
    total = 4000.00
    splits, summary = SplitCalculator.calculate_equal_split(total, participants)
    
    assert len(splits) == 4
    for s in splits:
        assert s['amount'] == 1000.00
    assert sum(s['amount'] for s in splits) == 4000.00

def test_equal_split_invalid_inputs():
    participants = [{"id": "p1", "name": "Chaitu"}]
    with pytest.raises(ValueError, match="greater than zero"):
        SplitCalculator.calculate_equal_split(0.0, participants)
        
    with pytest.raises(ValueError, match="participant is required"):
        SplitCalculator.calculate_equal_split(500.0, [])

def test_percentage_split_valid():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"},
        {"id": "p4", "name": "Lathi"}
    ]
    total = 5000.00
    percentages = {"p1": 40.0, "p2": 30.0, "p3": 20.0, "p4": 10.0}
    
    splits, summary = SplitCalculator.calculate_percentage_split(total, participants, percentages)
    assert sum(s['amount'] for s in splits) == 5000.00
    assert splits[0]['amount'] == 2000.00
    assert splits[1]['amount'] == 1500.00
    assert splits[2]['amount'] == 1000.00
    assert splits[3]['amount'] == 500.00

def test_percentage_split_invalid_sum():
    participants = [{"id": "p1", "name": "Chaitu"}, {"id": "p2", "name": "Ramu"}]
    percentages = {"p1": 50.0, "p2": 45.0} # 95% != 100%
    
    with pytest.raises(ValueError, match="must equal 100%"):
        SplitCalculator.calculate_percentage_split(1000.0, participants, percentages)

def test_custom_split_valid():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"},
        {"id": "p4", "name": "Lathi"}
    ]
    total = 4000.00
    custom_amounts = {"p1": 1500.0, "p2": 1000.0, "p3": 1000.0, "p4": 500.0}
    
    splits, summary = SplitCalculator.calculate_custom_split(total, participants, custom_amounts)
    assert sum(s['amount'] for s in splits) == 4000.00
    assert splits[0]['amount'] == 1500.00
    assert splits[3]['amount'] == 500.00

def test_custom_split_mismatch_rejection():
    participants = [{"id": "p1", "name": "Chaitu"}, {"id": "p2", "name": "Ramu"}]
    custom_amounts = {"p1": 600.0, "p2": 300.0} # 900 != 1000
    
    with pytest.raises(ValueError, match="Difference"):
        SplitCalculator.calculate_custom_split(1000.0, participants, custom_amounts)

def test_itemized_split_with_proportional_tax():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"}
    ]
    items = [
        {"name": "Pizza", "total_price": 600.0, "assigned_participants": ["p1", "p2"]}, # 300 each
        {"name": "Burger", "total_price": 300.0, "assigned_participants": ["p3"]},       # 300 for p3
        {"name": "Beverage", "total_price": 100.0, "assigned_participants": ["p1"]}     # 100 for p1
    ]
    # Subtotal = 1000. Tax = 100. Total = 1100.
    # Chaitu: items 400 (40% of subtotal) -> tax 40 -> total 440
    # Ramu: items 300 (30% of subtotal) -> tax 30 -> total 330
    # Mohan: items 300 (30% of subtotal) -> tax 30 -> total 330
    splits, summary = SplitCalculator.calculate_itemized_split(1100.0, participants, items, tax=50.0, gst=50.0)
    
    assert sum(s['amount'] for s in splits) == 1100.00
    p_map = {s['participant_id']: s['amount'] for s in splits}
    assert p_map['p1'] == 440.00
    assert p_map['p2'] == 330.00
    assert p_map['p3'] == 330.00
