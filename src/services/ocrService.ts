import { api } from './api';
import { MultiBillSummary, UploadedReceiptResult } from '../types';

export const ocrService = {
  async uploadReceipts(files: File[]): Promise<{ summary: MultiBillSummary; receipts: UploadedReceiptResult[] }> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });

    const res = await api.post('/ocr/upload', formData);
    if (!res.data.success || !res.data.data) {
      throw new Error(res.data.error || 'Unable to process receipts.');
    }
    return {
      summary: res.data.data.summary,
      receipts: res.data.data.receipts,
    };
  },

  async analyzeText(text: string) {
    const res = await api.post('/ocr/analyze', { text });
    return res.data.data;
  },

  async getHistory() {
    const res = await api.get('/ocr/history');
    return res.data.data || [];
  }
};
