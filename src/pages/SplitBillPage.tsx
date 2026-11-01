import React from 'react';
import { useExpenseWorkflowStore } from '../store/expenseWorkflowStore';
import { Step1PreviewItems } from '../components/split/Step1PreviewItems';
import { Step2Participants } from '../components/split/Step2Participants';
import { Step3Strategy } from '../components/split/Step3Strategy';
import { Step4FinalSave } from '../components/split/Step4FinalSave';
import { Check, Receipt, Users, Calculator, ShieldCheck } from 'lucide-react';
import { Expense } from '../types';

interface SplitBillPageProps {
  onSavedSuccess: (expense: Expense) => void;
  onNavigateToChat: () => void;
}

export const SplitBillPage: React.FC<SplitBillPageProps> = ({
  onSavedSuccess,
  onNavigateToChat
}) => {
  const { currentStep, setCurrentStep } = useExpenseWorkflowStore();

  const steps = [
    { number: 1, label: 'Preview & Items', icon: Receipt },
    { number: 2, label: 'Participants', icon: Users },
    { number: 3, label: 'Split Strategy', icon: Calculator },
    { number: 4, label: 'Final Settlement', icon: ShieldCheck }
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Title */}
      <div>
        <h2 className="text-xl font-extrabold text-white">Split Bill & Settle Debts</h2>
        <p className="text-xs text-slate-400">
          Review extracted items, add participants, choose your split strategy, and compute deterministic settlements.
        </p>
      </div>

      {/* Stepper Navigation */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-4">
        <div className="flex items-center justify-between">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.number;
            const isCurrent = currentStep === step.number;

            return (
              <React.Fragment key={step.number}>
                <button
                  onClick={() => setCurrentStep(step.number)}
                  className="flex items-center gap-2 group text-left focus:outline-none"
                >
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-xl text-xs font-bold transition-all ${
                      isCompleted
                        ? 'bg-emerald-600 text-white'
                        : isCurrent
                        ? 'bg-purple-600 text-white shadow-glow-purple ring-2 ring-purple-400/50'
                        : 'bg-slate-800 text-slate-400 border border-white/5'
                    }`}
                  >
                    {isCompleted ? <Check className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                  </div>
                  <div className="hidden sm:block">
                    <p className={`text-[10px] font-bold uppercase tracking-wider ${isCurrent ? 'text-purple-400' : 'text-slate-500'}`}>
                      Step {step.number}
                    </p>
                    <p className={`text-xs font-bold ${isCurrent ? 'text-white' : 'text-slate-400'}`}>
                      {step.label}
                    </p>
                  </div>
                </button>

                {idx < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-2 sm:mx-4 rounded-full transition-all ${
                      currentStep > idx + 1 ? 'bg-emerald-600' : 'bg-slate-800'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Wizard Content Panes */}
      <div className="transition-all">
        {currentStep === 1 && <Step1PreviewItems />}
        {currentStep === 2 && <Step2Participants />}
        {currentStep === 3 && <Step3Strategy />}
        {currentStep === 4 && (
          <Step4FinalSave
            onSavedSuccess={onSavedSuccess}
            onNavigateToChat={onNavigateToChat}
          />
        )}
      </div>
    </div>
  );
};
