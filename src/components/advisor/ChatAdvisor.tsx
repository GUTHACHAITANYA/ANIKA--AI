import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../../services/api';
import { ChatMessage } from '../../types';

export const ChatAdvisor: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I am **ANIKA**, your AI Financial Intelligence Advisor. I have real-time access to your verified expenses, budgets, and pending settlements. How can I help you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    "How much did I spend this month?",
    "What is my highest spending category?",
    "How much does Ramu owe me?",
    "Where can I reduce spending?",
    "Analyze my recent expenses.",
    "Suggest a budget."
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const res = await api.post('/ai/chat', { message: query.trim() });
      const reply = res.data?.data?.reply || "I analyzed your query based on current financial records.";

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I encountered an issue connecting to the financial intelligence server. Please ensure the backend is active and retry.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] flex-col rounded-2xl border border-white/10 bg-[#111827] shadow-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/5 bg-slate-900/60 px-6 py-3.5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/40">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              ANIKA AI Financial Advisor
              <span className="rounded-full bg-emerald-950/80 px-2 py-0.5 text-[9px] font-bold text-emerald-300 border border-emerald-800/40">
                Grounded Core
              </span>
            </h4>
            <p className="text-[11px] text-slate-400">Deterministic context • Zero financial hallucinations</p>
          </div>
        </div>
      </div>

      {/* Message History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  isUser
                    ? 'bg-indigo-600 text-white'
                    : 'bg-purple-900/50 text-purple-300 border border-purple-700/50'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              <div
                className={`max-w-xl rounded-2xl p-4 text-xs leading-relaxed shadow-sm ${
                  isUser
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-900/90 text-slate-200 border border-white/5 rounded-tl-none'
                }`}
              >
                <div className="prose prose-invert prose-xs max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
                <span className="mt-2 block text-[9px] text-slate-400 text-right">
                  {m.timestamp}
                </span>
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-purple-900/50 text-purple-300 border border-purple-700/50">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-2xl bg-slate-900/90 p-4 border border-white/5 text-xs text-purple-300 flex items-center gap-2">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
              <span>Analyzing your financial data...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Chips */}
      <div className="border-t border-white/5 bg-slate-900/40 px-6 py-2.5 overflow-x-auto">
        <div className="flex items-center gap-2 min-w-max">
          <Sparkles className="h-3.5 w-3.5 text-purple-400 shrink-0" />
          <span className="text-[10px] font-semibold text-slate-400 shrink-0">Try asking:</span>
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSendMessage(prompt)}
              className="rounded-lg border border-white/5 bg-slate-800/60 px-2.5 py-1 text-[11px] text-slate-300 hover:border-purple-500/40 hover:text-purple-300 transition"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Field */}
      <div className="border-t border-white/5 bg-slate-900/80 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask about your monthly expenses, debts, budget, or spending advice..."
            className="flex-1 rounded-xl border border-white/10 bg-slate-950 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-glow-purple hover:opacity-95 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
