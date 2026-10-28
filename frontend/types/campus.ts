export interface Coordinates {
  x: number;
  y: number;
  lat?: number;
  lng?: number;
}

export interface Location {
  id: string;
  name: string;
  category: string;
  description: string;
  floor?: string;
  coordinates: Coordinates;
  tags: string[];
}

export interface Edge {
  from: string;
  to: string;
  distance: number;
  path_type?: string;
  accessible?: boolean;
  has_stairs?: boolean;
  ramp_available?: boolean;
  accessibility_verified?: boolean;
}

export interface MapBounds {
  width: number;
  height: number;
}

export interface CampusGraphData {
  campus_name: string;
  is_demo_data: boolean;
  notice: string;
  distance_unit: string;
  map_bounds: MapBounds;
  locations: Location[];
  edges: Edge[];
}

export type RoutePreference = 'shortest' | 'wheelchair' | 'avoid_stairs';

export interface RouteStep {
  step_number: number;
  from_node_id: string;
  from_node_name: string;
  to_node_id: string;
  to_node_name: string;
  distance: number;
  cumulative_distance: number;
  instruction: string;
  path_type: string;
  has_stairs?: boolean;
  ramp_available?: boolean;
  accessibility_verified?: boolean;
}

export interface RouteResponse {
  found: boolean;
  start_id: string;
  destination_id: string;
  preference?: RoutePreference;
  total_distance: number;
  distance_unit: string;
  path_node_ids: string[];
  waypoints: Location[];
  steps: RouteStep[];
  preference_explanation?: string;
  is_accessible_verified?: boolean;
  message?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  reply: string;
  model: string;
  grounded_in_campus_data: boolean;
  ollama_online: boolean;
  suggestions: string[];
}

export interface HealthResponse {
  status: string;
  campus_data_loaded: boolean;
  total_locations: number;
  total_connections: number;
  is_demo_data: boolean;
  ollama_status: string;
  ollama_model: string;
}
