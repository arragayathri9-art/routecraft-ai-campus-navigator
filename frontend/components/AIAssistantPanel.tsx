'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  Send,
  Sparkles,
  X,
  Trash2,
  AlertCircle,
  HelpCircle,
  ArrowRight
} from 'lucide-react';
import { ChatMessage, HealthResponse, Location } from '../types/campus';
import { api } from '../services/api';

interface AIAssistantPanelProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthResponse | null;
  selectedLocation: Location | null;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
  isOpen,
  onClose,
  health,
  selectedLocation,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "Hello! I'm RouteCraft AI, your campus assistant for Aurora University. How can I help you navigate buildings, study spaces, or dining commons today?",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([
    'Where can I find a quiet place to study?',
    'What dining options are available on campus?',
    'Where is Turing Engineering & Robotics Hall?',
    'What facilities are in Spartan Athletic Center?',
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (queryText?: string) => {
    const text = (queryText || input).trim();
    if (!text || loading) return;

    const newMessages: ChatMessage[] = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await api.sendChatMessage(
        text,
        newMessages.slice(-6),
        selectedLocation?.id
      );

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.reply },
      ]);

      if (res.suggestions && res.suggestions.length > 0) {
        setSuggestions(res.suggestions);
      }
    } catch (err: unknown) {
      const errMsg =
        err instanceof Error ? err.message : 'Error communicating with campus assistant.';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ ${errMsg}. Please ensure the RouteCraft backend is running.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        role: 'assistant',
        content:
          "Conversation cleared. What would you like to know about the Aurora University campus?",
      },
    ]);
  };

  if (!isOpen) return null;

  return (
    <aside className="w-full md:w-96 bg-white border-l border-slate-200 flex flex-col h-[calc(100vh-6rem)] shadow-lg z-30 shrink-0">
      {/* Panel Header */}
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800 leading-tight flex items-center gap-1.5">
              Campus AI Assistant
              <span className="text-[10px] font-normal bg-blue-100 text-blue-700 px-1.5 py-0.2 rounded font-mono">
                {health?.ollama_model || 'llama3.2'}
              </span>
            </h3>
            <p className="text-[11px] text-slate-500">
              {health?.ollama_status === 'ready'
                ? '🟢 Ollama Local Assistant Active'
                : '🟡 Fallback Knowledge Active'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleClear}
            title="Clear Chat"
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            title="Close Assistant"
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Selected Location Context Badge */}
      {selectedLocation && (
        <div className="bg-blue-50/70 border-b border-blue-100 px-4 py-1.5 text-[11px] text-blue-800 flex items-center justify-between">
          <span className="truncate">
            Focusing on: <strong>{selectedLocation.name}</strong>
          </span>
          <span className="text-[10px] text-blue-500 font-medium">Context active</span>
        </div>
      )}

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/40">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed shadow-2xs whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-xs'
                  : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-xs p-3 shadow-2xs flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-bounce" />
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.15s]" />
              <span className="w-2 h-2 rounded-full bg-blue-600 animate-bounce [animation-delay:0.3s]" />
              <span className="text-[11px] text-slate-400 ml-1">Consulting campus dataset...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions Section */}
      <div className="p-3 border-t border-slate-200 bg-white">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-blue-500" /> Suggested questions
        </span>
        <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
          {suggestions.slice(0, 3).map((sug, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(sug)}
              disabled={loading}
              className="text-[11px] bg-slate-100 hover:bg-blue-50 hover:text-blue-700 text-slate-700 border border-slate-200/80 px-2.5 py-1 rounded-full text-left transition-colors flex items-center gap-1"
            >
              <span>{sug}</span>
              <ArrowRight className="w-2.5 h-2.5 opacity-50 shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Chat Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 border-t border-slate-200 bg-white flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask campus navigator anything..."
          disabled={loading}
          className="flex-1 text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-800 placeholder-slate-400 focus:outline-hidden focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white p-2.5 rounded-xl shadow-xs transition-colors shrink-0 cursor-pointer disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </aside>
  );
};
