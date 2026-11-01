import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import { Expense } from '../types';
import { formatINR, formatDate } from '../utils/currency';

export const exportService = {
  downloadTXT(expenseId: number) {
    const url = `/api/export/expense/${expenseId}/txt`;
    window.open(url, '_blank');
  },

  downloadCSV() {
    const url = `/api/export/expenses/csv`;
    window.open(url, '_blank');
  },

  generatePDF(expense: Expense, userName: string = 'User') {
    const doc = new jsPDF();

    // 1. Header Banner
    doc.setFillColor(11, 15, 25); // Dark navy
    doc.rect(0, 0, 210, 35, 'F');

    doc.setTextColor(255, 255, 255);
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('ANIKA-AI', 14, 18);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(192, 132, 252); // Purple accent
    doc.text('AI-Powered OCR Expense Splitting & Financial Intelligence Platform', 14, 26);

    // 2. Metadata Grid
    doc.setTextColor(30, 41, 59);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text('EXPENSE & SETTLEMENT REPORT', 14, 46);

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    doc.text(`Report Prepared For : ${userName}`, 14, 53);
    doc.text(`Generated Date      : ${formatDate(new Date().toISOString())}`, 14, 59);
    doc.text(`Expense Title       : ${expense.title}`, 14, 65);

    doc.text(`Merchant / Store    : ${expense.merchant_name}`, 110, 53);
    doc.text(`Transaction Date    : ${formatDate(expense.transaction_date)}`, 110, 59);
    doc.text(`Primary Payer       : ${expense.payer_name}`, 110, 65);
    doc.text(`Split Strategy      : ${expense.split_strategy.toUpperCase()}`, 110, 71);

    // 3. Items Table
    let startY = 78;
    if (expense.items && expense.items.length > 0) {
      doc.setFont('helvetica', 'bold');
      doc.text('1. ITEMIZED EXPENSE BREAKDOWN', 14, startY);
      
      const itemRows = expense.items.map((it, idx) => [
        idx + 1,
        it.name,
        it.quantity,
        formatINR(it.unit_price),
        formatINR(it.total_price),
        it.category || 'General'
      ]);

      autoTable(doc, {
        startY: startY + 4,
        head: [['#', 'Item Name', 'Qty', 'Unit Price', 'Total', 'Category']],
        body: itemRows,
        theme: 'striped',
        headStyles: { fillColor: [99, 102, 241] }, // Indigo
        styles: { fontSize: 8 },
      });

      startY = (doc as any).lastAutoTable.finalY + 12;
    }

    // 4. Participant Allocations Table
    doc.setFont('helvetica', 'bold');
    doc.text('2. PARTICIPANT ALLOCATIONS & SHARES', 14, startY);

    const splitRows = (expense.splits || []).map((sp) => [
      sp.participant_name,
      formatINR(sp.amount),
      `${(sp.percentage || 0).toFixed(1)}%`
    ]);

    autoTable(doc, {
      startY: startY + 4,
      head: [['Participant', 'Assigned Share (INR)', 'Share %']],
      body: splitRows,
      theme: 'grid',
      headStyles: { fillColor: [139, 92, 246] }, // Purple
      styles: { fontSize: 8 },
    });

    startY = (doc as any).lastAutoTable.finalY + 12;

    // 5. Settlement Transactions (Who Owes Whom)
    doc.setFont('helvetica', 'bold');
    doc.text('3. OPTIMIZED SETTLEMENT TRANSFERS (WHO OWES WHOM)', 14, startY);

    const settlementRows = (expense.settlements || []).map((st) => [
      st.from_name,
      'OWES ->',
      st.to_name,
      formatINR(st.amount),
      st.is_paid ? 'SETTLED' : 'PENDING'
    ]);

    autoTable(doc, {
      startY: startY + 4,
      head: [['Debtor (From)', 'Transfer', 'Creditor (To)', 'Amount (INR)', 'Status']],
      body: settlementRows.length > 0 ? settlementRows : [['All participants are settled', '-', '-', '₹0.00', 'CLEAR']],
      theme: 'striped',
      headStyles: { fillColor: [16, 185, 129] }, // Emerald
      styles: { fontSize: 8 },
    });

    startY = (doc as any).lastAutoTable.finalY + 14;

    // 6. Summary Box
    doc.setFillColor(248, 250, 252);
    doc.roundedRect(14, startY, 182, 22, 3, 3, 'F');
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text(`Total Bill Amount: ${formatINR(expense.total_amount)}`, 20, startY + 14);

    // Save
    doc.save(`anika_settlement_${expense.merchant_name.replace(/\s+/g, '_')}_${expense.id}.pdf`);
  }
};
