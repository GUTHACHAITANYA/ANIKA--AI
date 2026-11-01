from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any

def to_cents(amount: float) -> int:
    """Convert float currency to integer cents safely."""
    d = Decimal(str(amount))
    return int((d * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def from_cents(cents: int) -> float:
    """Convert integer cents back to float with 2 decimal places."""
    return float(Decimal(cents) / Decimal(100))

class SettlementEngine:
    """
    Deterministic settlement and debt-simplification engine.
    Computes exact net balances and generates minimum cash transfers.
    AI is strictly prohibited from performing financial arithmetic.
    """

    @staticmethod
    def calculate_settlements(
        participants: List[Dict[str, Any]],
        payer_id: str,
        total_amount: float,
        splits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate who owes whom using greedy debt minimization.
        
        Args:
            participants: List of participant dicts [{'id': 'p1', 'name': 'Chaitu'}, ...]
            payer_id: ID of the participant who paid the bill
            total_amount: Total bill amount in currency units
            splits: List of individual shares [{'participant_id': 'p1', 'amount': 1000.0}, ...]
            
        Returns:
            Dict containing:
                - net_balances: [{'participant_id', 'name', 'paid', 'owed', 'net_balance'}]
                - transactions: [{'from_id', 'from_name', 'to_id', 'to_name', 'amount'}]
                - total_settlement_amount: Sum of all settlement transfers
        """
        participant_map = {p['id']: p.get('name', p['id']) for p in participants}
        total_cents = to_cents(total_amount)
        
        # Track paid amounts in cents
        paid_cents: Dict[str, int] = {p['id']: 0 for p in participants}
        if payer_id in paid_cents:
            paid_cents[payer_id] = total_cents
        else:
            # Fallback if payer_id not found directly
            paid_cents[participants[0]['id']] = total_cents

        # Track owed amounts (shares) in cents
        owed_cents: Dict[str, int] = {p['id']: 0 for p in participants}
        for split in splits:
            pid = split.get('participant_id') or split.get('id')
            if pid in owed_cents:
                owed_cents[pid] += to_cents(split.get('amount', split.get('share_amount', 0.0)))

        # Calculate Net Balances: net = paid - owed
        # Positive: participant is owed money (creditor)
        # Negative: participant owes money (debtor)
        net_cents: Dict[str, int] = {}
        net_balances_output = []
        for p in participants:
            pid = p['id']
            p_paid = paid_cents.get(pid, 0)
            p_owed = owed_cents.get(pid, 0)
            p_net = p_paid - p_owed
            net_cents[pid] = p_net
            net_balances_output.append({
                'participant_id': pid,
                'name': participant_map[pid],
                'paid': from_cents(p_paid),
                'owed': from_cents(p_owed),
                'net_balance': from_cents(p_net)
            })

        # Greedily match maximum debtor with maximum creditor
        # Creditors: positive net balance (descending)
        creditors = [[pid, net_cents[pid]] for pid in net_cents if net_cents[pid] > 0]
        # Debtors: negative net balance (stored as positive debt, descending)
        debtors = [[pid, -net_cents[pid]] for pid in net_cents if net_cents[pid] < 0]

        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)

        transactions = []
        total_transfer_cents = 0

        c_idx = 0
        d_idx = 0

        while c_idx < len(creditors) and d_idx < len(debtors):
            c_id, c_amount = creditors[c_idx]
            d_id, d_amount = debtors[d_idx]

            transfer_cents = min(c_amount, d_amount)
            if transfer_cents > 0:
                transactions.append({
                    'from_id': d_id,
                    'from_name': participant_map[d_id],
                    'to_id': c_id,
                    'to_name': participant_map[c_id],
                    'amount': from_cents(transfer_cents),
                    'status': 'pending'
                })
                total_transfer_cents += transfer_cents

                creditors[c_idx][1] -= transfer_cents
                debtors[d_idx][1] -= transfer_cents

            if creditors[c_idx][1] == 0:
                c_idx += 1
            if debtors[d_idx][1] == 0:
                d_idx += 1

        return {
            'net_balances': net_balances_output,
            'transactions': transactions,
            'total_settlement_amount': from_cents(total_transfer_cents),
            'currency': 'INR'
        }
