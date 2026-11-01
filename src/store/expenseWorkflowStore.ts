import { create } from 'zustand';
import { Participant, ReceiptItem, SplitShare, SettlementTransaction, SplitStrategy } from '../types';

interface ExpenseWorkflowState {
  // Step navigation (1: Preview, 2: Participants, 3: Strategy & Payer, 4: Final Save)
  currentStep: number;
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;

  // Receipt & Bill Data
  merchantName: string;
  transactionDate: string;
  totalAmount: number;
  subtotal: number;
  tax: number;
  gst: number;
  category: string;
  items: ReceiptItem[];
  currency: string;
  notes: string;

  setBillData: (data: {
    merchantName?: string;
    transactionDate?: string;
    totalAmount?: number;
    subtotal?: number;
    tax?: number;
    gst?: number;
    category?: string;
    items?: ReceiptItem[];
    currency?: string;
    notes?: string;
  }) => void;

  addItem: (item: ReceiptItem) => void;
  updateItem: (index: number, updated: Partial<ReceiptItem>) => void;
  removeItem: (index: number) => void;

  // Participants
  participants: Participant[];
  addParticipant: (name: string) => void;
  addMultipleParticipants: (namesText: string) => void;
  removeParticipant: (id: string) => void;
  setParticipants: (list: Participant[]) => void;

  // Payer
  payerId: string;
  payerName: string;
  setPayer: (id: string) => void;

  // Split Strategy & Allocations
  splitStrategy: SplitStrategy;
  setSplitStrategy: (strategy: SplitStrategy) => void;
  percentages: Record<string, number>;
  setPercentages: (p: Record<string, number>) => void;
  setParticipantPercentage: (id: string, pct: number) => void;
  customAmounts: Record<string, number>;
  setCustomAmounts: (c: Record<string, number>) => void;
  setParticipantCustomAmount: (id: string, amt: number) => void;

  // Calculated Results
  splits: SplitShare[];
  setSplits: (s: SplitShare[]) => void;
  settlements: SettlementTransaction[];
  setSettlements: (st: SettlementTransaction[]) => void;

  // Load from OCR Extraction
  loadFromOCR: (data: any) => void;
  resetWorkflow: () => void;
}

const DEFAULT_PARTICIPANTS: Participant[] = [
  { id: 'me', name: 'Me', is_payer: true, active: true },
  { id: 'p_1', name: 'Chaitu', is_payer: false, active: true },
  { id: 'p_2', name: 'Ramu', is_payer: false, active: true },
  { id: 'p_3', name: 'Mohan', is_payer: false, active: true }
];

export const useExpenseWorkflowStore = create<ExpenseWorkflowState>((set, get) => ({
  currentStep: 1,
  setCurrentStep: (step) => set({ currentStep: Math.min(Math.max(step, 1), 4) }),
  nextStep: () => set((state) => ({ currentStep: Math.min(state.currentStep + 1, 4) })),
  prevStep: () => set((state) => ({ currentStep: Math.max(state.currentStep - 1, 1) })),

  merchantName: "The Urban Bistro & Grill",
  transactionDate: new Date().toISOString().split('T')[0],
  totalAmount: 4000.0,
  subtotal: 3500.0,
  tax: 250.0,
  gst: 250.0,
  category: "Food & Dining",
  currency: "INR",
  notes: "",
  items: [
    { name: "Woodfired Pizza", quantity: 2, unit_price: 600, total_price: 1200, category: "Food & Dining", assigned_participants: [] },
    { name: "Pasta Alfredo & Garlic Bread", quantity: 2, unit_price: 450, total_price: 900, category: "Food & Dining", assigned_participants: [] },
    { name: "Artisanal Mocktails", quantity: 4, unit_price: 175, total_price: 700, category: "Food & Dining", assigned_participants: [] },
    { name: "Lava Cake Platter", quantity: 2, unit_price: 350, total_price: 700, category: "Food & Dining", assigned_participants: [] }
  ],

  setBillData: (data) => set((state) => ({
    merchantName: data.merchantName ?? state.merchantName,
    transactionDate: data.transactionDate ?? state.transactionDate,
    totalAmount: data.totalAmount !== undefined ? Number(data.totalAmount) : state.totalAmount,
    subtotal: data.subtotal !== undefined ? Number(data.subtotal) : state.subtotal,
    tax: data.tax !== undefined ? Number(data.tax) : state.tax,
    gst: data.gst !== undefined ? Number(data.gst) : state.gst,
    category: data.category ?? state.category,
    items: data.items ?? state.items,
    currency: data.currency ?? state.currency,
    notes: data.notes ?? state.notes,
  })),

  addItem: (item) => set((state) => {
    const newItems = [...state.items, item];
    const subtotal = newItems.reduce((acc, i) => acc + (i.total_price || 0), 0);
    const total = subtotal + state.tax + state.gst;
    return { items: newItems, subtotal, totalAmount: total };
  }),

  updateItem: (index, updated) => set((state) => {
    const newItems = [...state.items];
    if (newItems[index]) {
      newItems[index] = { ...newItems[index], ...updated };
      if (updated.quantity !== undefined || updated.unit_price !== undefined) {
        newItems[index].total_price = Number(newItems[index].quantity) * Number(newItems[index].unit_price);
      }
    }
    const subtotal = newItems.reduce((acc, i) => acc + (i.total_price || 0), 0);
    const total = subtotal + state.tax + state.gst;
    return { items: newItems, subtotal, totalAmount: total };
  }),

  removeItem: (index) => set((state) => {
    const newItems = state.items.filter((_, i) => i !== index);
    const subtotal = newItems.reduce((acc, i) => acc + (i.total_price || 0), 0);
    const total = subtotal + state.tax + state.gst;
    return { items: newItems, subtotal, totalAmount: total };
  }),

  // Participants
  participants: DEFAULT_PARTICIPANTS,

  addParticipant: (name) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    set((state) => {
      // Check if already exists
      if (state.participants.some((p) => p.name.toLowerCase() === trimmed.toLowerCase())) {
        return state;
      }
      const newId = `p_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
      const newP: Participant = { id: newId, name: trimmed, is_payer: false, active: true };
      return { participants: [...state.participants, newP] };
    });
  },

  addMultipleParticipants: (namesText) => {
    if (!namesText || !namesText.trim()) return;
    const parts = namesText.split(/[,;\n]+/).map((s) => s.trim()).filter(Boolean);
    set((state) => {
      let current = [...state.participants];
      parts.forEach((name) => {
        if (!current.some((p) => p.name.toLowerCase() === name.toLowerCase())) {
          const newId = `p_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
          current.push({ id: newId, name, is_payer: false, active: true });
        }
      });
      return { participants: current };
    });
  },

  removeParticipant: (id) => {
    if (id === 'me' && get().participants.length <= 1) return; // keep at least one
    set((state) => {
      const remaining = state.participants.filter((p) => p.id !== id);
      let newPayerId = state.payerId;
      let newPayerName = state.payerName;
      if (state.payerId === id && remaining.length > 0) {
        newPayerId = remaining[0].id;
        newPayerName = remaining[0].name;
      }
      return {
        participants: remaining,
        payerId: newPayerId,
        payerName: newPayerName
      };
    });
  },

  setParticipants: (list) => set({ participants: list }),

  // Payer
  payerId: 'me',
  payerName: 'Me',
  setPayer: (id) => {
    const p = get().participants.find((item) => item.id === id);
    if (p) {
      set({ payerId: id, payerName: p.name });
    }
  },

  // Strategy
  splitStrategy: 'equal',
  setSplitStrategy: (strategy) => set({ splitStrategy: strategy }),
  percentages: {},
  setPercentages: (p) => set({ percentages: p }),
  setParticipantPercentage: (id, pct) => set((state) => ({
    percentages: { ...state.percentages, [id]: pct }
  })),
  customAmounts: {},
  setCustomAmounts: (c) => set({ customAmounts: c }),
  setParticipantCustomAmount: (id, amt) => set((state) => ({
    customAmounts: { ...state.customAmounts, [id]: amt }
  })),

  // Calculation outputs
  splits: [],
  setSplits: (splits) => set({ splits }),
  settlements: [],
  setSettlements: (settlements) => set({ settlements }),

  loadFromOCR: (extracted) => {
    const subtotal = Number(extracted.subtotal) || 0;
    const tax = Number(extracted.tax) || 0;
    const gst = Number(extracted.gst) || 0;
    const total = Number(extracted.total) || (subtotal + tax + gst);
    
    set({
      merchantName: extracted.merchant_name || "General Merchant",
      transactionDate: extracted.transaction_date || new Date().toISOString().split('T')[0],
      totalAmount: total,
      subtotal: subtotal || total,
      tax: tax,
      gst: gst,
      category: extracted.category || "Other",
      currency: extracted.currency || "INR",
      items: (extracted.items && extracted.items.length > 0) ? extracted.items : [
        { name: "Receipt Total Items", quantity: 1, unit_price: total, total_price: total, category: extracted.category || "Other" }
      ],
      currentStep: 1 // Start at step 1 for review
    });
  },

  resetWorkflow: () => set({
    currentStep: 1,
    merchantName: "",
    transactionDate: new Date().toISOString().split('T')[0],
    totalAmount: 0,
    subtotal: 0,
    tax: 0,
    gst: 0,
    category: "Other",
    notes: "",
    items: [],
    splits: [],
    settlements: [],
    percentages: {},
    customAmounts: {}
  })
}));
