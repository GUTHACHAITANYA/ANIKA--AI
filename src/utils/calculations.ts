import { Participant, ReceiptItem, SplitStrategy } from '../types';

export const validateSplitStrategy = (
  strategy: SplitStrategy,
  totalAmount: number,
  participants: Participant[],
  values: {
    percentages?: Record<string, number>;
    customAmounts?: Record<string, number>;
    items?: ReceiptItem[];
  }
): { valid: boolean; error?: string } => {
  if (totalAmount <= 0) {
    return { valid: false, error: 'Total amount must be greater than zero.' };
  }
  if (!participants || participants.length === 0) {
    return { valid: false, error: 'Please add at least one participant.' };
  }

  if (strategy === 'percentage') {
    const percentages = values.percentages || {};
    const sumPct = participants.reduce((acc, p) => acc + (percentages[p.id] || 0), 0);
    if (Math.abs(sumPct - 100) > 0.05) {
      return { valid: false, error: `Total percentage must equal 100%. Current sum: ${sumPct.toFixed(1)}%` };
    }
  } else if (strategy === 'custom') {
    const customAmounts = values.customAmounts || {};
    const sumCustom = participants.reduce((acc, p) => acc + (customAmounts[p.id] || 0), 0);
    if (Math.abs(sumCustom - totalAmount) > 0.05) {
      return {
        valid: false,
        error: `Custom amounts sum to ₹${sumCustom.toFixed(2)}, which does not match total ₹${totalAmount.toFixed(2)}.`
      };
    }
  } else if (strategy === 'itemized') {
    const items = values.items || [];
    if (items.length === 0) {
      return { valid: false, error: 'At least one item is required for an itemized split.' };
    }
  }

  return { valid: true };
};
