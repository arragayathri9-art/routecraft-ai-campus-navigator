'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  FlaskConical,
  Cpu,
  Utensils,
  Dumbbell,
  Landmark,
  Palette,
  DoorOpen,
  Trees,
  MapPin,
  Eye,
  EyeOff
} from 'lucide-react';
import { Location, Edge, RouteResponse, MapBounds } from '../types/campus';

interface CampusMapProps {
  locations: Location[];
  edges: Edge[];
  mapBounds: MapBounds;
  selectedLocation: Location | null;
  onSelectLocation: (loc: Location) => void;
  startId: string;
  destId: string;
  routeResult: RouteResponse | null;
  loading: boolean;
}

export const CampusMap: React.FC<CampusMapProps> = ({
  locations,
  edges,
  mapBounds,
  selectedLocation,
  onSelectLocation,
  startId,
  destId,
  routeResult,
  loading,
}) => {
  // Transform state for pan & zoom
  const [scale, setScale] = useState(1);
  const [translate, setTranslate] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showDistances, setShowDistances] = useState(true);

  const containerRef = useRef<HTMLDivElement>(null);

  // Zoom handlers
  const handleZoomIn = () => setScale((prev) => Math.min(prev * 1.25, 3.0));
  const handleZoomOut = () => setScale((prev) => Math.max(prev * 0.8, 0.6));
  const handleReset = () => {
    setScale(1);
    setTranslate({ x: 0, y: 0 });
  };

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    setScale((prev) => Math.min(Math.max(prev * factor, 0.6), 3.0));
  };

  // Pan handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Left click only
    setIsDragging(true);
    setDragStart({ x: e.clientX - translate.x, y: e.clientY - translate.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setTranslate({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  // Map category to icon
  const getCategoryIcon = (category: string, id: string) => {
    if (id === 'lib') return <BookOpen className="w-3.5 h-3.5" />;
    if (id === 'sci') return <FlaskConical className="w-3.5 h-3.5" />;
    if (id === 'eng') return <Cpu className="w-3.5 h-3.5" />;
    if (id === 'cafe') return <Utensils className="w-3.5 h-3.5" />;
    if (id === 'gym') return <Dumbbell className="w-3.5 h-3.5" />;
    if (id === 'adm') return <Landmark className="w-3.5 h-3.5" />;
    if (id === 'arts') return <Palette className="w-3.5 h-3.5" />;
    if (id === 'quad') return <Trees className="w-3.5 h-3.5" />;
    if (id.includes('gate')) return <DoorOpen className="w-3.5 h-3.5" />;
    return <MapPin className="w-3.5 h-3.5" />;
  };

  // Node lookup
  const locMap = new Map<string, Location>();
  locations.forEach((loc) => locMap.set(loc.id, loc));

  // Determine which edges belong to active route
  const activeRoutePairs = new Set<string>();
  if (routeResult && routeResult.path_node_ids.length > 1) {
    const ids = routeResult.path_node_ids;
    for (let i = 0; i < ids.length - 1; i++) {
      activeRoutePairs.add(`${ids[i]}->${ids[i + 1]}`);
      activeRoutePairs.add(`${ids[i + 1]}->${ids[i]}`);
    }
  }

  // Dynamic route colors based on accessibility preference
  const isWheelchair = routeResult?.preference === 'wheelchair';
  const isAvoidStairs = routeResult?.preference === 'avoid_stairs';

  const routeStrokeColor = isWheelchair
    ? '#059669' // Emerald
    : isAvoidStairs
    ? '#4f46e5' // Indigo
    : '#2563eb'; // Blue

  const routeGlowColor = isWheelchair
    ? '#a7f3d0'
    : isAvoidStairs
    ? '#c7d2fe'
    : '#bfdbfe';

  const routePillColor = isWheelchair
    ? '#047857'
    : isAvoidStairs
    ? '#4338ca'
    : '#1d4ed8';

  return (
    <div
      ref={containerRef}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      className={`relative flex-1 h-[calc(100vh-6rem)] bg-slate-100 overflow-hidden select-none cursor-${
        isDragging ? 'grabbing' : 'grab'
      }`}
    >
      {/* Schematic Notice Tag on Map */}
      <div className="absolute top-4 left-4 z-20 bg-white/90 backdrop-blur-xs border border-slate-200/90 rounded-xl px-3 py-1.5 shadow-xs flex items-center gap-2 text-xs">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        <span className="font-semibold text-slate-700">Schematic 2D Campus Layout</span>
        <span className="text-[10px] text-slate-400 font-mono hidden sm:inline">
          ({mapBounds.width} x {mapBounds.height} canvas)
        </span>
      </div>

      {/* Map Control Buttons */}
      <div className="absolute top-4 right-4 z-20 flex flex-col gap-1.5 bg-white/95 backdrop-blur-xs border border-slate-200 rounded-xl p-1.5 shadow-sm">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-2 hover:bg-slate-100 text-slate-700 rounded-lg transition-colors cursor-pointer"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-2 hover:bg-slate-100 text-slate-700 rounded-lg transition-colors cursor-pointer"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <div className="h-px bg-slate-200 my-0.5" />
        <button
          onClick={handleReset}
          title="Reset View"
          className="p-2 hover:bg-slate-100 text-slate-700 rounded-lg transition-colors cursor-pointer"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button
          onClick={() => setShowDistances(!showDistances)}
          title={showDistances ? 'Hide path distances' : 'Show path distances'}
          className={`p-2 rounded-lg transition-colors cursor-pointer ${
            showDistances ? 'text-blue-600 bg-blue-50' : 'text-slate-400 hover:bg-slate-100'
          }`}
        >
          {showDistances ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
        </button>
      </div>

      {/* SVG Map Canvas */}
      <div
        className="w-full h-full flex items-center justify-center transition-transform duration-75 ease-out"
        style={{
          transform: `translate(${translate.x}px, ${translate.y}px) scale(${scale})`,
          transformOrigin: 'center center',
        }}
      >
        <svg
          viewBox={`0 0 ${mapBounds.width || 900} ${mapBounds.height || 850}`}
          className="w-[880px] h-[830px] filter drop-shadow-md rounded-2xl overflow-visible"
        >
          {/* Base Campus Terrain */}
          <rect
            x="40"
            y="20"
            width="820"
            height="800"
            rx="32"
            fill="#f8fafc"
            stroke="#e2e8f0"
            strokeWidth="3"
          />

          {/* Landscaped Quad Greenspace */}
          <rect
            x="330"
            y="310"
            width="240"
            height="180"
            rx="24"
            fill="#ecfdf5"
            stroke="#a7f3d0"
            strokeWidth="2"
            strokeDasharray="4 4"
          />
          <text
            x="450"
            y="335"
            textAnchor="middle"
            fill="#059669"
            fontSize="10"
            fontWeight="bold"
            letterSpacing="1"
          >
            SPARTAN CENTRAL GREEN
          </text>

          {/* Academic North Meadow */}
          <rect
            x="130"
            y="130"
            width="220"
            height="110"
            rx="16"
            fill="#f0fdf4"
            stroke="#bbf7d0"
            strokeWidth="1.5"
            opacity="0.6"
          />

          {/* Student Hub East Plaza */}
          <rect
            x="590"
            y="170"
            width="220"
            height="130"
            rx="16"
            fill="#eff6ff"
            stroke="#bfdbfe"
            strokeWidth="1.5"
            opacity="0.6"
          />

          {/* South Athletic Fields Zone */}
          <rect
            x="350"
            y="690"
            width="200"
            height="100"
            rx="20"
            fill="#f0fdf4"
            stroke="#86efac"
            strokeWidth="2"
            opacity="0.7"
          />

          {/* EDGES: Campus Walkways */}
          <g id="campus-pathways">
            {edges.map((edge, idx) => {
              const u = locMap.get(edge.from);
              const v = locMap.get(edge.to);
              if (!u || !v) return null;

              const isRouteSegment = activeRoutePairs.has(`${edge.from}->${edge.to}`);
              const midX = (u.coordinates.x + v.coordinates.x) / 2;
              const midY = (u.coordinates.y + v.coordinates.y) / 2;

              return (
                <g key={`edge-${idx}`}>
                  {/* Subtle shadow line */}
                  <line
                    x1={u.coordinates.x}
                    y1={u.coordinates.y}
                    x2={v.coordinates.x}
                    y2={v.coordinates.y}
                    stroke={isRouteSegment ? routeGlowColor : '#e2e8f0'}
                    strokeWidth={isRouteSegment ? '10' : '4'}
                    strokeLinecap="round"
                    opacity={isRouteSegment ? '0.7' : '0.8'}
                  />

                  {/* Primary walkway line */}
                  <line
                    x1={u.coordinates.x}
                    y1={u.coordinates.y}
                    x2={v.coordinates.x}
                    y2={v.coordinates.y}
                    stroke={
                      isRouteSegment
                        ? routeStrokeColor
                        : edge.has_stairs && !edge.ramp_available
                        ? '#cbd5e1'
                        : '#cbd5e1'
                    }
                    strokeWidth={isRouteSegment ? '4.5' : '2'}
                    strokeDasharray={
                      isRouteSegment
                        ? '6 4'
                        : edge.has_stairs && !edge.ramp_available
                        ? '4 3'
                        : 'none'
                    }
                    strokeLinecap="round"
                    className={isRouteSegment ? 'animate-route-flow' : ''}
                  />

                  {/* Distance label pill */}
                  {showDistances && (
                    <g transform={`translate(${midX}, ${midY})`}>
                      <rect
                        x="-20"
                        y="-8"
                        width="40"
                        height="16"
                        rx="8"
                        fill={isRouteSegment ? routePillColor : '#ffffff'}
                        stroke={isRouteSegment ? routeGlowColor : '#e2e8f0'}
                        strokeWidth="1"
                        filter="drop-shadow(0 1px 1px rgb(0 0 0 / 0.05))"
                      />
                      <text
                        x="0"
                        y="3.5"
                        textAnchor="middle"
                        fill={isRouteSegment ? '#ffffff' : '#64748b'}
                        fontSize="9"
                        fontFamily="monospace"
                        fontWeight={isRouteSegment ? 'bold' : 'normal'}
                      >
                        {Math.round(edge.distance)}m{edge.has_stairs && !edge.ramp_available ? ' ⚠️' : ''}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </g>

          {/* NODES: Campus Buildings & Gates */}
          <g id="campus-nodes">
            {locations.map((loc) => {
              const isSelected = selectedLocation?.id === loc.id;
              const isStart = startId === loc.id;
              const isDest = destId === loc.id;
              const isWaypoint =
                routeResult?.path_node_ids.includes(loc.id) && !isStart && !isDest;

              // Node card dimensions
              const cardWidth = 130;
              const cardHeight = 44;
              const cx = loc.coordinates.x;
              const cy = loc.coordinates.y;

              return (
                <g
                  key={loc.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectLocation(loc);
                  }}
                  className="cursor-pointer group"
                >
                  {/* Selection glow aura */}
                  {(isSelected || isStart || isDest) && (
                    <rect
                      x={cx - cardWidth / 2 - 4}
                      y={cy - cardHeight / 2 - 4}
                      width={cardWidth + 8}
                      height={cardHeight + 8}
                      rx="16"
                      fill={
                        isStart
                          ? 'rgba(16, 185, 129, 0.2)'
                          : isDest
                          ? 'rgba(239, 68, 68, 0.2)'
                          : 'rgba(59, 130, 246, 0.25)'
                      }
                      className="animate-pulse"
                    />
                  )}

                  {/* Main Building Card */}
                  <rect
                    x={cx - cardWidth / 2}
                    y={cy - cardHeight / 2}
                    width={cardWidth}
                    height={cardHeight}
                    rx="12"
                    fill={
                      isStart
                        ? '#059669'
                        : isDest
                        ? '#dc2626'
                        : isWaypoint
                        ? '#1d4ed8'
                        : isSelected
                        ? '#2563eb'
                        : '#ffffff'
                    }
                    stroke={
                      isStart
                        ? '#047857'
                        : isDest
                        ? '#b91c1c'
                        : isWaypoint || isSelected
                        ? '#1e40af'
                        : '#cbd5e1'
                    }
                    strokeWidth={isSelected || isStart || isDest ? '2.5' : '1.5'}
                    filter="drop-shadow(0 2px 4px rgb(0 0 0 / 0.08))"
                  />

                  {/* Icon Circle */}
                  <circle
                    cx={cx - cardWidth / 2 + 18}
                    cy={cy}
                    r="12"
                    fill={
                      isStart || isDest || isWaypoint || isSelected
                        ? 'rgba(255, 255, 255, 0.2)'
                        : '#f1f5f9'
                    }
                  />

                  {/* Node Name */}
                  <text
                    x={cx - cardWidth / 2 + 36}
                    y={cy - 2}
                    fill={
                      isStart || isDest || isWaypoint || isSelected
                        ? '#ffffff'
                        : '#1e293b'
                    }
                    fontSize="10"
                    fontWeight="bold"
                  >
                    {loc.name.length > 15 ? loc.name.substring(0, 14) + '…' : loc.name}
                  </text>

                  {/* Category Subtitle */}
                  <text
                    x={cx - cardWidth / 2 + 36}
                    y={cy + 11}
                    fill={
                      isStart || isDest || isWaypoint || isSelected
                        ? 'rgba(255, 255, 255, 0.8)'
                        : '#64748b'
                    }
                    fontSize="8.5"
                  >
                    {loc.category.length > 17
                      ? loc.category.substring(0, 16) + '…'
                      : loc.category}
                  </text>

                  {/* Start / Dest Status Badges */}
                  {isStart && (
                    <g transform={`translate(${cx + cardWidth / 2 - 22}, ${cy - cardHeight / 2 - 6})`}>
                      <rect width="32" height="15" rx="7.5" fill="#10b981" />
                      <text x="16" y="10.5" textAnchor="middle" fill="#ffffff" fontSize="8" fontWeight="bold">
                        START
                      </text>
                    </g>
                  )}

                  {isDest && (
                    <g transform={`translate(${cx + cardWidth / 2 - 20}, ${cy - cardHeight / 2 - 6})`}>
                      <rect width="28" height="15" rx="7.5" fill="#ef4444" />
                      <text x="14" y="10.5" textAnchor="middle" fill="#ffffff" fontSize="8" fontWeight="bold">
                        DEST
                      </text>
                    </g>
                  )}

                  {isWaypoint && (
                    <g transform={`translate(${cx + cardWidth / 2 - 12}, ${cy - cardHeight / 2 - 6})`}>
                      <circle cx="8" cy="8" r="8" fill="#3b82f6" />
                      <text x="8" y="11" textAnchor="middle" fill="#ffffff" fontSize="8" fontWeight="bold">
                        •
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-20 bg-white/95 backdrop-blur-xs border border-slate-200 rounded-xl p-3 shadow-sm text-xs hidden sm:block">
        <span className="font-bold text-slate-800 text-[11px] uppercase tracking-wider block mb-2">
          Map Legend
        </span>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px] text-slate-600">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />
            <span>Start Landmark</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500 inline-block" />
            <span>Destination Landmark</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 bg-blue-600 rounded inline-block" />
            <span>Shortest Route</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 bg-emerald-600 rounded inline-block" />
            <span>Barrier-Free Path</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 border-b-2 border-slate-400 border-dashed inline-block" />
            <span>Stairs / Unramped</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 bg-slate-300 rounded inline-block" />
            <span>Paved Walkway</span>
          </div>
        </div>
      </div>

      {/* Floating Route Selection Rationale & Preference Callout (Requirement 5) */}
      {routeResult && (
        <div className="absolute bottom-4 right-4 z-20 bg-white/95 backdrop-blur-xs border border-slate-200 rounded-2xl p-3.5 shadow-md max-w-xs sm:max-w-md pointer-events-auto transition-all">
          <div className="flex items-center justify-between gap-2 mb-1.5">
            <div className="flex items-center gap-2">
              <span
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: routeStrokeColor }}
              />
              <span className="text-xs font-bold text-slate-800">
                {routeResult.preference === 'wheelchair'
                  ? 'Wheelchair-Friendly Route'
                  : routeResult.preference === 'avoid_stairs'
                  ? 'Stair-Free Route'
                  : 'Direct Shortest Route'}
              </span>
            </div>
            <span className="text-[11px] font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded-lg border border-slate-200">
              {routeResult.total_distance}m
            </span>
          </div>
          {routeResult.preference_explanation && (
            <p className="text-[11px] text-slate-600 leading-relaxed">
              {routeResult.preference_explanation}
            </p>
          )}
        </div>
      )}
    </div>
  );
};
