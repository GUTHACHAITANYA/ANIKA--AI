import pytest
from backend.services.settlement_engine import SettlementEngine

def test_settlement_payer_chaitu_four_people():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"},
        {"id": "p4", "name": "Lathi"}
    ]
    splits = [
        {"participant_id": "p1", "amount": 1000.0},
        {"participant_id": "p2", "amount": 1000.0},
        {"participant_id": "p3", "amount": 1000.0},
        {"participant_id": "p4", "amount": 1000.0}
    ]
    # Chaitu paid 4000
    res = SettlementEngine.calculate_settlements(participants, "p1", 4000.0, splits)
    
    transactions = res['transactions']
    assert len(transactions) == 3
    
    # Ramu -> Chaitu 1000, Mohan -> Chaitu 1000, Lathi -> Chaitu 1000
    for t in transactions:
        assert t['to_id'] == "p1"
        assert t['amount'] == 1000.0
        assert t['from_id'] in ["p2", "p3", "p4"]

def test_settlement_payer_ramu_custom_amounts():
    participants = [
        {"id": "p1", "name": "Chaitu"},
        {"id": "p2", "name": "Ramu"},
        {"id": "p3", "name": "Mohan"},
        {"id": "p4", "name": "Lathi"}
    ]
    splits = [
        {"participant_id": "p1", "amount": 1500.0},
        {"participant_id": "p2", "amount": 1000.0},
        {"participant_id": "p3", "amount": 1000.0},
        {"participant_id": "p4", "amount": 500.0}
    ]
    # Ramu paid the entire bill of 4000
    res = SettlementEngine.calculate_settlements(participants, "p2", 4000.0, splits)
    
    transactions = res['transactions']
    # Ramu paid 4000, owes 1000 -> Net +3000
    # Chaitu owes 1500 -> Ramu
    # Mohan owes 1000 -> Ramu
    # Lathi owes 500 -> Ramu
    assert len(transactions) == 3
    for t in transactions:
        assert t['to_id'] == "p2"
    
    t_map = {t['from_id']: t['amount'] for t in transactions}
    assert t_map['p1'] == 1500.0
    assert t_map['p3'] == 1000.0
    assert t_map['p4'] == 500.0

def test_net_balance_conservation():
    participants = [
        {"id": "me", "name": "Me"},
        {"id": "p1", "name": "Alex"},
        {"id": "p2", "name": "Sam"}
    ]
    splits = [
        {"participant_id": "me", "amount": 400.0},
        {"participant_id": "p1", "amount": 500.0},
        {"participant_id": "p2", "amount": 300.0}
    ]
    res = SettlementEngine.calculate_settlements(participants, "me", 1200.0, splits)
    
    net_sum = sum(b['net_balance'] for b in res['net_balances'])
    assert round(net_sum, 2) == 0.0

def test_debt_minimization_reduces_transactions():
    # Example where 4 participants have varying debts and credits
    participants = [
        {"id": "p1", "name": "A"},
        {"id": "p2", "name": "B"},
        {"id": "p3", "name": "C"},
        {"id": "p4", "name": "D"}
    ]
    # A paid 2000
    splits = [
        {"participant_id": "p1", "amount": 500.0},
        {"participant_id": "p2", "amount": 500.0},
        {"participant_id": "p3", "amount": 500.0},
        {"participant_id": "p4", "amount": 500.0}
    ]
    res = SettlementEngine.calculate_settlements(participants, "p1", 2000.0, splits)
    # Greedy algorithm guarantees at most N-1 transactions
    assert len(res['transactions']) <= 3
