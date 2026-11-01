from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple
from backend.services.settlement_engine import to_cents, from_cents

class SplitCalculator:
    """
    Deterministic calculation engine for all four split strategies:
    1. Equal Split
    2. Percentage Split
    3. Custom Amount Split
    4. Itemized Split
    """

    @staticmethod
    def calculate_equal_split(
        total_amount: float,
        participants: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Divide total equally among participants.
        Allocates remainder cents deterministically to ensure exact cent sum.
        """
        if not participants:
            raise ValueError("At least one participant is required")
        if total_amount <= 0:
            raise ValueError("Total amount must be greater than zero")

        total_cents = to_cents(total_amount)
        n = len(participants)
        base_share_cents = total_cents // n
        remainder_cents = total_cents % n

        splits = []
        for i, p in enumerate(participants):
            pid = p.get('id')
            pname = p.get('name', pid)
            # Give 1 extra cent to first 'remainder_cents' participants
            share_cents = base_share_cents + (1 if i < remainder_cents else 0)
            share_amount = from_cents(share_cents)
            percentage = round((share_cents / total_cents) * 100, 2)
            splits.append({
                'participant_id': pid,
                'participant_name': pname,
                'amount': share_amount,
                'percentage': percentage,
                'items': []
            })

        summary = {
            'strategy': 'equal',
            'total_amount': from_cents(total_cents),
            'participant_count': n,
            'per_person': from_cents(base_share_cents),
            'is_valid': True
        }
        return splits, summary

    @staticmethod
    def calculate_percentage_split(
        total_amount: float,
        participants: List[Dict[str, Any]],
        percentages: Dict[str, float]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Split total according to individual percentages.
        Requires sum of percentages to equal 100.0%.
        """
        if not participants:
            raise ValueError("At least one participant is required")
        if total_amount <= 0:
            raise ValueError("Total amount must be greater than zero")

        # Validate total percentage
        total_pct = sum(percentages.get(p['id'], 0.0) for p in participants)
        if abs(total_pct - 100.0) > 0.05:
            raise ValueError(f"Total percentage must equal 100%. Current sum: {total_pct:.2f}%")

        total_cents = to_cents(total_amount)
        splits = []
        allocated_cents = 0

        # Calculate base cents per person
        temp_shares = []
        for p in participants:
            pid = p['id']
            pct = percentages.get(pid, 0.0)
            share_cents = int((Decimal(str(total_cents)) * (Decimal(str(pct)) / Decimal(100))).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            temp_shares.append((p, pct, share_cents))
            allocated_cents += share_cents

        # Fix minor rounding discrepancy if any
        cents_diff = total_cents - allocated_cents
        for i, (p, pct, share_cents) in enumerate(temp_shares):
            if cents_diff != 0:
                adjustment = 1 if cents_diff > 0 else -1
                share_cents += adjustment
                cents_diff -= adjustment
            
            splits.append({
                'participant_id': p['id'],
                'participant_name': p.get('name', p['id']),
                'amount': from_cents(share_cents),
                'percentage': pct,
                'items': []
            })

        summary = {
            'strategy': 'percentage',
            'total_amount': from_cents(total_cents),
            'is_valid': True
        }
        return splits, summary

    @staticmethod
    def calculate_custom_split(
        total_amount: float,
        participants: List[Dict[str, Any]],
        custom_amounts: Dict[str, float]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validate and record custom fixed amounts.
        Sum of custom amounts must match bill total.
        """
        if not participants:
            raise ValueError("At least one participant is required")
        if total_amount <= 0:
            raise ValueError("Total amount must be greater than zero")

        total_cents = to_cents(total_amount)
        custom_cents_sum = sum(to_cents(custom_amounts.get(p['id'], 0.0)) for p in participants)

        if custom_cents_sum != total_cents:
            diff = from_cents(abs(total_cents - custom_cents_sum))
            msg = f"Custom amounts sum to ₹{from_cents(custom_cents_sum):,.2f}, but bill total is ₹{from_cents(total_cents):,.2f} (Difference: ₹{diff:,.2f})"
            raise ValueError(msg)

        splits = []
        for p in participants:
            pid = p['id']
            amt_cents = to_cents(custom_amounts.get(pid, 0.0))
            splits.append({
                'participant_id': pid,
                'participant_name': p.get('name', pid),
                'amount': from_cents(amt_cents),
                'percentage': round((amt_cents / total_cents) * 100, 2) if total_cents > 0 else 0.0,
                'items': []
            })

        summary = {
            'strategy': 'custom',
            'total_amount': from_cents(total_cents),
            'is_valid': True
        }
        return splits, summary

    @staticmethod
    def calculate_itemized_split(
        total_amount: float,
        participants: List[Dict[str, Any]],
        items: List[Dict[str, Any]],
        tax: float = 0.0,
        gst: float = 0.0
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Distribute item costs to assigned participants.
        Apportion taxes and fees proportionally to each participant's item subtotal.
        """
        if not participants:
            raise ValueError("At least one participant is required")
        if not items:
            raise ValueError("At least one item is required for itemized split")

        total_cents = to_cents(total_amount)
        participant_map = {p['id']: p.get('name', p['id']) for p in participants}
        
        # Track items and item shares in cents
        item_cents_per_p: Dict[str, int] = {p['id']: 0 for p in participants}
        assigned_items_per_p: Dict[str, List[Dict[str, Any]]] = {p['id']: [] for p in participants}

        items_subtotal_cents = 0

        for item in items:
            item_total = item.get('total_price')
            if item_total is None:
                item_total = float(item.get('quantity', 1.0)) * float(item.get('unit_price', 0.0))
            
            i_cents = to_cents(item_total)
            items_subtotal_cents += i_cents

            # Check assigned participants
            assigned_ids = item.get('assigned_participants', [])
            # Filter to valid participant IDs
            valid_assigned = [pid for pid in assigned_ids if pid in participant_map]
            if not valid_assigned:
                # If unassigned, divide among all participants equally
                valid_assigned = list(participant_map.keys())

            # Divide this item among assigned participants
            n_assigned = len(valid_assigned)
            item_base_cents = i_cents // n_assigned
            item_rem_cents = i_cents % n_assigned

            for idx, pid in enumerate(valid_assigned):
                share = item_base_cents + (1 if idx < item_rem_cents else 0)
                item_cents_per_p[pid] += share
                assigned_items_per_p[pid].append({
                    'name': item.get('name', 'Item'),
                    'share_amount': from_cents(share),
                    'quantity': item.get('quantity', 1)
                })

        # Calculate remaining tax/gst/charges cents to apportion
        # If total_cents > items_subtotal_cents, apportion the excess (taxes/fees)
        additional_cents = max(0, total_cents - items_subtotal_cents)
        allocated_additional_cents = 0
        p_additional_cents: Dict[str, int] = {p['id']: 0 for p in participants}

        if additional_cents > 0 and items_subtotal_cents > 0:
            for p in participants:
                pid = p['id']
                p_item_share = item_cents_per_p[pid]
                # Proportionate tax share
                add_cents = int((Decimal(str(additional_cents)) * (Decimal(str(p_item_share)) / Decimal(str(items_subtotal_cents)))).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
                p_additional_cents[pid] = add_cents
                allocated_additional_cents += add_cents

            # Balance any 1-cent discrepancy
            diff = additional_cents - allocated_additional_cents
            if diff != 0:
                first_pid = participants[0]['id']
                p_additional_cents[first_pid] += diff

        # Build final splits
        splits = []
        for p in participants:
            pid = p['id']
            p_final_cents = item_cents_per_p[pid] + p_additional_cents[pid]
            splits.append({
                'participant_id': pid,
                'participant_name': participant_map[pid],
                'amount': from_cents(p_final_cents),
                'item_subtotal': from_cents(item_cents_per_p[pid]),
                'tax_share': from_cents(p_additional_cents[pid]),
                'percentage': round((p_final_cents / total_cents) * 100, 2) if total_cents > 0 else 0.0,
                'items': assigned_items_per_p[pid]
            })

        summary = {
            'strategy': 'itemized',
            'items_subtotal': from_cents(items_subtotal_cents),
            'taxes_fees': from_cents(additional_cents),
            'total_amount': from_cents(total_cents),
            'is_valid': True
        }
        return splits, summary
