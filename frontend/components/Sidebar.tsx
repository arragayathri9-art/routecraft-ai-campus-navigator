'use client';

import React from 'react';
import {
  Search,
  MapPin,
  ArrowRightLeft,
  Navigation,
  Clock,
  Footprints,
  X,
  Layers,
  ChevronRight,
  Info,
  CheckCircle2,
  AlertCircle,
  Accessibility,
  AlertTriangle,
  ShieldCheck
} from 'lucide-react';
import { Location, RouteResponse, RoutePreference } from '../types/campus';

interface SidebarProps {
  locations: Location[];
  allLocations?: Location[];
  categories: string[];
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedLocation: Location | null;
  onSelectLocation: (loc: Location | null) => void;

  startId: string;
  onStartChange: (id: string) => void;
  destId: string;
  onDestChange: (id: string) => void;
  onSwapPoints: () => void;

  routePreference: RoutePreference;
  onRouteChangePreference: (pref: RoutePreference) => void;

  routeResult: RouteResponse | null;
  routeLoading: boolean;
  routeError: string | null;
  onCalculateRoute: () => void;
  onClearRoute: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  locations,
  allLocations,
  categories,
  selectedCategory,
  onSelectCategory,
  searchQuery,
  onSearchChange,
  selectedLocation,
  onSelectLocation,
  startId,
  onStartChange,
  destId,
  onDestChange,
  onSwapPoints,
  routePreference,
  onRouteChangePreference,
  routeResult,
  routeLoading,
  routeError,
  onCalculateRoute,
  onClearRoute,
}) => {
  // Estimated walking speed: ~75 meters per minute
  const estimatedMins = routeResult?.total_distance
    ? Math.max(1, Math.round(routeResult.total_distance / 75))
    : 0;

  const plannerLocations = allLocations && allLocations.length > 0 ? allLocations : locations;

  return (
    <aside className="w-full lg:w-96 bg-white border-r border-slate-200 flex flex-col h-[calc(100vh-6rem)] overflow-y-auto shrink-0 shadow-xs">
      <div className="p-4 space-y-4">
        {/* Route Planner Card */}
        <div className="bg-slate-50/80 border border-slate-200/90 rounded-2xl p-4 shadow-2xs">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Navigation className="w-4 h-4 text-blue-600" />
              <h2 className="text-sm font-bold text-slate-800 tracking-tight">
                Campus Route Finder
              </h2>
            </div>
            <span className="text-[10px] font-mono font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
              Dijkstra
            </span>
          </div>

          {/* Selectors */}
          <div className="space-y-2.5 relative">
            {/* Start Node */}
            <div className="relative">
              <label className="text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                Starting Point
              </label>
              <select
                value={startId}
                onChange={(e) => onStartChange(e.target.value)}
                className="w-full text-xs font-medium bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-2xs"
              >
                <option value="">Select origin landmark...</option>
                {plannerLocations.map((loc) => (
                  <option key={`start-${loc.id}`} value={loc.id}>
                    {loc.name} ({loc.category})
                  </option>
                ))}
              </select>
            </div>

            {/* Swap Button */}
            <div className="flex justify-center -my-1 relative z-10">
              <button
                type="button"
                onClick={onSwapPoints}
                title="Swap Start and Destination"
                className="bg-white hover:bg-slate-100 border border-slate-200 p-1.5 rounded-full text-slate-600 hover:text-blue-600 shadow-xs transition-colors cursor-pointer"
              >
                <ArrowRightLeft className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Destination Node */}
            <div className="relative">
              <label className="text-[11px] font-medium text-slate-500 mb-1 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
                Destination Point
              </label>
              <select
                value={destId}
                onChange={(e) => onDestChange(e.target.value)}
                className="w-full text-xs font-medium bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-2xs"
              >
                <option value="">Select destination landmark...</option>
                {plannerLocations.map((loc) => (
                  <option key={`dest-${loc.id}`} value={loc.id}>
                    {loc.name} ({loc.category})
                  </option>
                ))}
              </select>
            </div>

            {/* Accessibility Route Preference Selector */}
            <div className="pt-1.5">
              <label className="text-[11px] font-semibold text-slate-600 mb-1.5 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Accessibility className="w-3.5 h-3.5 text-blue-600" />
                  Routing Preference
                </span>
                {routePreference === 'wheelchair' && (
                  <span className="text-[9px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.2 rounded-full">
                    Barrier-Free
                  </span>
                )}
              </label>
              <div className="grid grid-cols-3 gap-1 bg-slate-200/70 p-1 rounded-xl">
                <button
                  type="button"
                  onClick={() => onRouteChangePreference('shortest')}
                  className={`text-[11px] py-1.5 px-1.5 rounded-lg font-medium transition-all text-center cursor-pointer ${
                    routePreference === 'shortest'
                      ? 'bg-white text-blue-700 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Direct shortest walking path across all campus walkways"
                >
                  Shortest
                </button>
                <button
                  type="button"
                  onClick={() => onRouteChangePreference('wheelchair')}
                  className={`text-[11px] py-1.5 px-1.5 rounded-lg font-medium transition-all text-center cursor-pointer ${
                    routePreference === 'wheelchair'
                      ? 'bg-white text-emerald-700 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Wheelchair-friendly: barrier-free pathways, verified ramps, avoids stairs"
                >
                  Wheelchair
                </button>
                <button
                  type="button"
                  onClick={() => onRouteChangePreference('avoid_stairs')}
                  className={`text-[11px] py-1.5 px-1.5 rounded-lg font-medium transition-all text-center cursor-pointer ${
                    routePreference === 'avoid_stairs'
                      ? 'bg-white text-indigo-700 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Avoid stairs: selects level walkways or ramp-equipped pathways"
                >
                  Avoid Stairs
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 flex gap-2">
              <button
                type="button"
                onClick={onCalculateRoute}
                disabled={!startId || !destId || routeLoading}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-medium text-xs py-2.5 px-3 rounded-xl shadow-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer disabled:cursor-not-allowed"
              >
                {routeLoading ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Computing Route...
                  </>
                ) : (
                  <>
                    <Navigation className="w-3.5 h-3.5" />
                    Calculate Route
                  </>
                )}
              </button>

              {routeResult && (
                <button
                  type="button"
                  onClick={onClearRoute}
                  className="bg-white hover:bg-slate-100 border border-slate-200 text-slate-600 text-xs px-3 py-2.5 rounded-xl font-medium transition-colors cursor-pointer"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Route Error Notice (Safe Handling) */}
          {routeError && (
            <div className="mt-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs p-3 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold mb-0.5">No Suitable Route Found</p>
                <p className="text-[11px] leading-relaxed text-rose-700">{routeError}</p>
              </div>
            </div>
          )}
        </div>

        {/* Route Summary & Turn-by-Turn Directions */}
        {routeResult && (
          <div className="bg-white border border-blue-200 rounded-2xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                {routeResult.preference === 'wheelchair'
                  ? 'Wheelchair-Friendly Route'
                  : routeResult.preference === 'avoid_stairs'
                  ? 'Stair-Free Route'
                  : 'Shortest Route'} Found
              </h3>
              <span className="text-[11px] text-blue-600 font-medium">
                {routeResult.steps.length} segments
              </span>
            </div>

            {/* Why This Route Was Chosen (Requirement 5) */}
            {routeResult.preference_explanation && (
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-700 space-y-1">
                <div className="flex items-center gap-1.5 font-semibold text-slate-900">
                  <Info className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                  <span>Route Selection Rationale</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed pl-5">
                  {routeResult.preference_explanation}
                </p>
              </div>
            )}

            {/* Accessibility Verification Status Badge (Requirement 7) */}
            <div className="flex items-center justify-between text-[11px] px-1 py-0.5">
              <span className="text-slate-500 font-medium">Accessibility:</span>
              {routeResult.is_accessible_verified ? (
                <span className="font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-600" />
                  Verified Barrier-Free
                </span>
              ) : (
                <span className="font-medium text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-amber-600" />
                  General / Survey Pending
                </span>
              )}
            </div>

            {/* Quick Metrics */}
            <div className="grid grid-cols-2 gap-2 bg-blue-50/60 p-3 rounded-xl border border-blue-100">
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wide block font-medium">
                  Total Distance
                </span>
                <span className="text-base font-bold text-slate-900">
                  {routeResult.total_distance}{' '}
                  <span className="text-xs font-normal text-slate-600">
                    {routeResult.distance_unit}
                  </span>
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 uppercase tracking-wide block font-medium flex items-center gap-1">
                  <Clock className="w-3 h-3 text-blue-600" />
                  Est. Walk Time
                </span>
                <span className="text-base font-bold text-slate-900">
                  ~{estimatedMins}{' '}
                  <span className="text-xs font-normal text-slate-600">min</span>
                </span>
              </div>
            </div>

            {/* Turn-by-Turn Steps */}
            <div>
              <span className="text-[11px] font-semibold text-slate-600 mb-2 block flex items-center gap-1">
                <Footprints className="w-3.5 h-3.5 text-blue-600" />
                Turn-by-Turn Instructions
              </span>
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {routeResult.steps.map((step, idx) => (
                  <div
                    key={`step-${idx}`}
                    className="text-xs bg-slate-50 hover:bg-slate-100/80 p-2.5 rounded-lg border border-slate-100 transition-colors space-y-1"
                  >
                    <div className="flex items-start gap-2">
                      <span className="w-5 h-5 rounded-full bg-blue-600 text-white font-bold text-[10px] flex items-center justify-center shrink-0 mt-0.5">
                        {step.step_number}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-slate-800 leading-snug">{step.instruction}</p>
                        <div className="flex flex-wrap items-center gap-1.5 mt-1.5 text-[10px]">
                          <span className="text-slate-400 font-medium">
                            {step.distance} {routeResult.distance_unit}
                          </span>
                          <span className="text-slate-300">•</span>
                          {step.has_stairs && !step.ramp_available && (
                            <span className="text-rose-700 bg-rose-50 border border-rose-200 px-1.5 py-0.2 rounded font-medium">
                              Stairs
                            </span>
                          )}
                          {step.has_stairs && step.ramp_available && (
                            <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.2 rounded font-medium">
                              Ramp Equipped
                            </span>
                          )}
                          {step.accessibility_verified && (
                            <span className="text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.2 rounded font-medium">
                              Survey Verified
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Selected Landmark Detail Card */}
        {selectedLocation && (
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm relative space-y-2.5">
            <button
              onClick={() => onSelectLocation(null)}
              className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 cursor-pointer"
              title="Close details"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-start gap-2.5 pr-6">
              <div className="w-8 h-8 rounded-xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center shrink-0">
                <MapPin className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 leading-tight">
                  {selectedLocation.name}
                </h3>
                <span className="text-[11px] font-medium text-blue-600">
                  {selectedLocation.category} • Floor {selectedLocation.floor || '1'}
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {selectedLocation.description}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-1 pt-1">
              {selectedLocation.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium"
                >
                  #{tag}
                </span>
              ))}
            </div>

            {/* Quick Set Start/Dest buttons */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => onStartChange(selectedLocation.id)}
                className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 py-1.5 px-2.5 rounded-lg font-medium transition-colors cursor-pointer"
              >
                Set as Start
              </button>
              <button
                type="button"
                onClick={() => onDestChange(selectedLocation.id)}
                className="text-xs bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 py-1.5 px-2.5 rounded-lg font-medium transition-colors cursor-pointer"
              >
                Set as Dest
              </button>
            </div>
          </div>
        )}

        {/* Campus Directory Search & Filter */}
        <div className="space-y-3 pt-1">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-500" />
              Campus Directory ({locations.length})
            </h3>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search buildings, labs, food..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl pl-9 pr-8 py-2 text-slate-800 placeholder-slate-400 focus:outline-hidden focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => onSearchChange('')}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-1.5 pb-1">
            <button
              onClick={() => onSelectCategory('All')}
              className={`text-[11px] px-2.5 py-1 rounded-full font-medium transition-colors cursor-pointer ${
                selectedCategory === 'All'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
              }`}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => onSelectCategory(cat)}
                className={`text-[11px] px-2.5 py-1 rounded-full font-medium transition-colors cursor-pointer ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Locations List */}
          <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
            {locations.length === 0 ? (
              <div className="text-center py-6 text-slate-400 text-xs">
                No campus locations match your query.
              </div>
            ) : (
              locations.map((loc) => {
                const isSelected = selectedLocation?.id === loc.id;
                const isStart = startId === loc.id;
                const isDest = destId === loc.id;

                return (
                  <button
                    key={loc.id}
                    onClick={() => onSelectLocation(loc)}
                    className={`w-full text-left p-2.5 rounded-xl border transition-all flex items-center justify-between group cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50/70 border-blue-300 shadow-xs'
                        : 'bg-white hover:bg-slate-50 border-slate-200/80'
                    }`}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-xs text-slate-900 group-hover:text-blue-600 truncate">
                          {loc.name}
                        </span>
                        {isStart && (
                          <span className="text-[9px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded">
                            START
                          </span>
                        )}
                        {isDest && (
                          <span className="text-[9px] bg-rose-100 text-rose-800 font-bold px-1.5 py-0.2 rounded">
                            DEST
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-400 block truncate">
                        {loc.category}
                      </span>
                    </div>
                    <ChevronRight className="w-3.5 h-3.5 text-slate-300 group-hover:text-slate-500 shrink-0 ml-2" />
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>
    </aside>
  );
};
