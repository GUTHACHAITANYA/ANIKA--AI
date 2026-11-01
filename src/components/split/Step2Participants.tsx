import React, { useState } from 'react';
import { UserPlus, Users, X, ArrowLeft, ArrowRight, Check, Sparkles } from 'lucide-react';
import { useExpenseWorkflowStore } from '../../store/expenseWorkflowStore';

export const Step2Participants: React.FC = () => {
  const {
    participants,
    addParticipant,
    addMultipleParticipants,
    removeParticipant,
    nextStep,
    prevStep
  } = useExpenseWorkflowStore();

  const [inputNames, setInputNames] = useState('');

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputNames.trim()) return;
    addMultipleParticipants(inputNames);
    setInputNames('');
  };

  const addPreset = (names: string) => {
    addMultipleParticipants(names);
  };

  return (
    <div className="space-y-6">
      {/* Participants Manager Box */}
      <div className="rounded-2xl border border-white/10 bg-[#111827] p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <Users className="h-4 w-4 text-purple-400" />
              Manage Participants ({participants.length})
            </h4>
            <p className="text-xs text-slate-400">
              Enter names separated by commas (e.g., <span className="text-purple-300">Chaitu, Ramu, Mohan, Lathi</span>)
            </p>
          </div>
          <span className="text-xs text-slate-400">
            Active: <span className="font-bold text-white">{participants.length} people</span>
          </span>
        </div>

        {/* Input Form */}
        <form onSubmit={handleAdd} className="flex gap-2">
          <input
            type="text"
            value={inputNames}
            onChange={(e) => setInputNames(e.target.value)}
            placeholder="Type names: e.g. Chaitu, Ramu, Mohan, Lathi"
            className="flex-1 rounded-xl border border-white/10 bg-slate-900 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            className="flex items-center gap-1.5 rounded-xl bg-purple-600 px-5 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:bg-purple-500 transition active:scale-95"
          >
            <UserPlus className="h-4 w-4" />
            ADD
          </button>
        </form>

        {/* Quick presets */}
        <div className="mt-3 flex items-center gap-2">
          <span className="text-[11px] text-slate-500">Quick suggestions:</span>
          <button
            type="button"
            onClick={() => addPreset("Chaitu, Ramu, Mohan, Lathi")}
            className="rounded-lg bg-slate-800/80 px-2.5 py-1 text-[11px] text-purple-300 hover:bg-slate-700 transition"
          >
            + Chaitu, Ramu, Mohan, Lathi
          </button>
          <button
            type="button"
            onClick={() => addPreset("Priya, Rahul, Ananya")}
            className="rounded-lg bg-slate-800/80 px-2.5 py-1 text-[11px] text-purple-300 hover:bg-slate-700 transition"
          >
            + Priya, Rahul, Ananya
          </button>
        </div>

        {/* Active Participant Chips Grid */}
        <div className="mt-6 pt-5 border-t border-white/5">
          <label className="text-xs font-bold text-slate-300 block mb-3">
            Active Bill Participants:
          </label>

          <div className="flex flex-wrap gap-2.5">
            {participants.map((p) => {
              const isMe = p.id === 'me';
              return (
                <div
                  key={p.id}
                  className={`flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold border transition-all ${
                    isMe
                      ? 'border-indigo-500/40 bg-indigo-950/40 text-indigo-200'
                      : 'border-purple-500/30 bg-purple-950/30 text-purple-200'
                  }`}
                >
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-purple-600/40 text-[10px] text-purple-200">
                    {p.name.charAt(0).toUpperCase()}
                  </span>
                  <span>{p.name}</span>
                  {isMe && <span className="text-[10px] text-indigo-400 font-normal">(Host)</span>}

                  {/* Remove Button */}
                  {!isMe && (
                    <button
                      type="button"
                      onClick={() => removeParticipant(p.id)}
                      className="ml-1 rounded p-0.5 text-slate-400 hover:bg-purple-900/50 hover:text-white transition"
                      title={`Remove ${p.name}`}
                    >
                      <X className="h-3 w-3" />
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          {participants.length === 0 && (
            <p className="text-xs text-amber-400 mt-2">
              Please add at least one participant to split this bill.
            </p>
          )}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={prevStep}
          className="flex items-center gap-2 rounded-xl border border-white/10 px-5 py-2.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 transition"
        >
          <ArrowLeft className="h-4 w-4" />
          Back: Preview
        </button>

        <button
          onClick={nextStep}
          disabled={participants.length < 1}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Next: Choose Split Strategy
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
