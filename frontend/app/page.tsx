'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';
import { CampusMap } from '../components/CampusMap';
import { AIAssistantPanel } from '../components/AIAssistantPanel';
import { api } from '../services/api';
import {
  Location,
  Edge,
  MapBounds,
  RouteResponse,
  HealthResponse,
  RoutePreference,
} from '../types/campus';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function CampusNavigatorPage() {
  // Application Data States
  const [locations, setLocations] = useState<Location[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [mapBounds, setMapBounds] = useState<MapBounds>({ width: 900, height: 850 });
  const [categories, setCategories] = useState<string[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // UI Interactive States
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [isAiOpen, setIsAiOpen] = useState(true);

  // Search & Filtering
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);

  // Route Planning States
  const [startId, setStartId] = useState('');
  const [destId, setDestId] = useState('');
  const [routePreference, setRoutePreference] = useState<RoutePreference>('shortest');
  const [routeResult, setRouteResult] = useState<RouteResponse | null>(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);

  // Load initial health status
  const loadHealth = useCallback(async () => {
    setHealthLoading(true);
    try {
      const h = await api.getHealth();
      setHealth(h);
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  }, []);

  // Load full campus topology
  const loadCampusData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [graphData, cats] = await Promise.all([
        api.getCampusGraph(),
        api.getCategories(),
      ]);

      setLocations(graphData.locations);
      setEdges(graphData.edges);
      setMapBounds(graphData.map_bounds || { width: 900, height: 850 });
      setCategories(cats);

      // Pre-select first 2 distinct buildings for route ease
      if (graphData.locations.length >= 2) {
        setStartId(graphData.locations[0].id); // North Gate
        setDestId(graphData.locations[1].id); // Library
      }
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : 'Could not connect to RouteCraft API server.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHealth();
    loadCampusData();
  }, [loadHealth, loadCampusData]);

  // Handle route calculation
  const handleCalculateRoute = async (prefOverride?: RoutePreference) => {
    if (!startId || !destId) {
      setRouteError('Please select both a starting point and a destination.');
      return;
    }

    const prefToUse = prefOverride || routePreference;
    setRouteLoading(true);
    setRouteError(null);

    try {
      const res = await api.calculateRoute(startId, destId, prefToUse);
      setRouteResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Route calculation failed.';
      setRouteError(msg);
      setRouteResult(null);
    } finally {
      setRouteLoading(false);
    }
  };

  // Change routing preference and re-calculate if a route was active
  const handleChangePreference = (pref: RoutePreference) => {
    setRoutePreference(pref);
    if (startId && destId && routeResult) {
      handleCalculateRoute(pref);
    }
  };

  // Swap start and destination
  const handleSwapPoints = () => {
    setStartId(destId);
    setDestId(startId);
    if (routeResult) {
      // Re-trigger calculation with swapped points
      setTimeout(() => {
        handleCalculateRoute();
      }, 50);
    }
  };

  // Clear current route
  const handleClearRoute = () => {
    setRouteResult(null);
    setRouteError(null);
  };

  // Reset map view
  const handleResetView = () => {
    setSelectedLocation(null);
    handleClearRoute();
  };

  // Filter locations based on search query and category
  const filteredLocations = locations.filter((loc) => {
    const matchesCategory =
      selectedCategory === 'All' || loc.category === selectedCategory;

    if (!matchesCategory) return false;

    if (!searchQuery.trim()) return true;

    const q = searchQuery.toLowerCase();
    return (
      loc.name.toLowerCase().includes(q) ||
      loc.description.toLowerCase().includes(q) ||
      loc.category.toLowerCase().includes(q) ||
      loc.tags.some((tag) => tag.toLowerCase().includes(q))
    );
  });

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50">
      {/* Top Header */}
      <Header
        health={health}
        healthLoading={healthLoading}
        onRefreshHealth={loadHealth}
        isAiOpen={isAiOpen}
        onToggleAi={() => setIsAiOpen(!isAiOpen)}
        onResetView={handleResetView}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Loading Overlay */}
        {loading && (
          <div className="absolute inset-0 z-50 bg-white/80 backdrop-blur-xs flex flex-col items-center justify-center gap-3">
            <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm font-semibold text-slate-700">
              Loading RouteCraft campus topology...
            </p>
          </div>
        )}

        {/* Global Error Banner */}
        {error && !loading && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-50 bg-rose-50 border border-rose-200 text-rose-800 px-4 py-3 rounded-2xl shadow-lg max-w-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <div className="flex-1 text-xs">
              <p className="font-bold">Backend Connection Failed</p>
              <p>{error}</p>
            </div>
            <button
              onClick={() => {
                loadHealth();
                loadCampusData();
              }}
              className="bg-rose-600 hover:bg-rose-700 text-white text-xs px-3 py-1.5 rounded-xl font-medium transition-colors flex items-center gap-1"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          </div>
        )}

        {/* Left Sidebar (Directory, Planner, Steps) */}
        <Sidebar
          locations={filteredLocations}
          allLocations={locations}
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={setSelectedCategory}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedLocation={selectedLocation}
          onSelectLocation={setSelectedLocation}
          startId={startId}
          onStartChange={setStartId}
          destId={destId}
          onDestChange={setDestId}
          onSwapPoints={handleSwapPoints}
          routePreference={routePreference}
          onRouteChangePreference={handleChangePreference}
          routeResult={routeResult}
          routeLoading={routeLoading}
          routeError={routeError}
          onCalculateRoute={handleCalculateRoute}
          onClearRoute={handleClearRoute}
        />

        {/* Center Interactive 2D Campus Map */}
        <CampusMap
          locations={locations}
          edges={edges}
          mapBounds={mapBounds}
          selectedLocation={selectedLocation}
          onSelectLocation={setSelectedLocation}
          startId={startId}
          destId={destId}
          routeResult={routeResult}
          loading={loading}
        />

        {/* Right Collapsible Grounded AI Assistant Panel */}
        <AIAssistantPanel
          isOpen={isAiOpen}
          onClose={() => setIsAiOpen(false)}
          health={health}
          selectedLocation={selectedLocation}
        />
      </div>
    </div>
  );
}
