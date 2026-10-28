'use client';

import React from 'react';
import { Compass, Bot, Activity, AlertTriangle, RefreshCw } from 'lucide-react';
import { HealthResponse } from '../types/campus';

interface HeaderProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
  isAiOpen: boolean;
  onToggleAi: () => void;
  onResetView: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  healthLoading,
  onRefreshHealth,
  isAiOpen,
  onToggleAi,
  onResetView,
}) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      {/* Explicit Synthetic Demo Notice Bar */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-1.5 text-xs text-amber-900 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-4xl">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong className="font-semibold">Demo Notice:</strong> Fictional synthetic layout for Aurora University navigation testing. Building coordinates and path measurements are for prototyping and pending campus survey verification.
          </span>
        </div>
        <span className="hidden md:inline-block font-mono bg-amber-100 text-amber-800 px-2 py-0.5 rounded text-[10px] uppercase tracking-wide font-medium">
          Synthetic Demo
        </span>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Compass className="w-5 h-5 animate-spin-slow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-slate-900">
                RouteCraft <span className="text-blue-600">AI</span>
              </h1>
              <span className="bg-blue-50 text-blue-700 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-blue-200">
                Aurora Campus
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Intelligent Campus Navigation & Dijkstra Shortest Path Finder
            </p>
          </div>
        </div>

        {/* Status Indicators & Controls */}
        <div className="flex items-center gap-3">
          {/* Backend / Ollama Status Pill */}
          <div className="hidden sm:flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs">
            <Activity className="w-3.5 h-3.5 text-slate-400" />
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  health?.status === 'healthy' ? 'bg-emerald-500' : 'bg-rose-500'
                }`}
              />
              <span className="text-slate-600 font-medium">
                {healthLoading
                  ? 'Checking...'
                  : health?.status === 'healthy'
                  ? 'API Online'
                  : 'API Disconnected'}
              </span>
            </div>

            <div className="h-3 w-px bg-slate-200 mx-1" />

            <div className="flex items-center gap-1 text-[11px]">
              <span className="text-slate-400">Ollama:</span>
              <span
                className={`font-mono font-medium ${
                  health?.ollama_status === 'ready'
                    ? 'text-emerald-700'
                    : 'text-amber-700'
                }`}
              >
                {health?.ollama_status === 'ready'
                  ? 'llama3.2 Ready'
                  : health?.ollama_status || 'Offline'}
              </span>
            </div>

            <button
              onClick={onRefreshHealth}
              title="Refresh backend status"
              className="text-slate-400 hover:text-slate-600 transition-colors ml-1 p-0.5 rounded hover:bg-slate-200"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>

          {/* Reset Map View */}
          <button
            onClick={onResetView}
            className="hidden md:flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg px-3 py-2 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reset Map
          </button>

          {/* AI Assistant Toggle Button */}
          <button
            onClick={onToggleAi}
            className={`flex items-center gap-2 text-xs font-semibold px-3.5 py-2 rounded-lg border transition-all ${
              isAiOpen
                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                : 'bg-white text-blue-700 border-blue-200 hover:bg-blue-50'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>AI Assistant</span>
            <span
              className={`w-2 h-2 rounded-full ${
                health?.ollama_status === 'ready'
                  ? 'bg-emerald-400'
                  : 'bg-amber-400'
              }`}
            />
          </button>
        </div>
      </div>
    </header>
  );
};
