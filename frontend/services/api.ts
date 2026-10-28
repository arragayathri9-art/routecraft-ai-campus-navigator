import {
  CampusGraphData,
  ChatResponse,
  HealthResponse,
  Location,
  RouteResponse,
  ChatMessage
} from '../types/campus';

const DEFAULT_API_BASE = 'https://routecraft-ai-campus-navigator-1.onrender.com/api';
const API_BASE = (process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_BASE).replace(/\/+$/, '');

async function safeFetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
      try {
        const errJson = await res.json();
        if (errJson.detail) {
          errorDetail = errJson.detail;
        }
      } catch {
        // ignore JSON parse error on non-json error responses
      }
      throw new Error(errorDetail);
    }

    return await res.json();
  } catch (err: unknown) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error('Network error connecting to RouteCraft backend.');
  }
}

export const api = {
  getHealth: async (): Promise<HealthResponse> => {
    return safeFetch<HealthResponse>('/health');
  },

  getLocations: async (query?: string, category?: string): Promise<Location[]> => {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (category && category !== 'All') params.set('category', category);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return safeFetch<Location[]>(`/locations${qs}`);
  },

  getLocationById: async (id: string): Promise<Location> => {
    return safeFetch<Location>(`/locations/${encodeURIComponent(id)}`);
  },

  getCategories: async (): Promise<string[]> => {
    return safeFetch<string[]>('/categories');
  },

  getCampusGraph: async (): Promise<CampusGraphData> => {
    return safeFetch<CampusGraphData>('/graph');
  },

  calculateRoute: async (
    startId: string,
    destinationId: string,
    preference: string = 'shortest'
  ): Promise<RouteResponse> => {
    return safeFetch<RouteResponse>('/route', {
      method: 'POST',
      body: JSON.stringify({
        start_id: startId,
        destination_id: destinationId,
        preference,
      }),
    });
  },

  sendChatMessage: async (
    message: string,
    history: ChatMessage[] = [],
    currentLocationId?: string
  ): Promise<ChatResponse> => {
    return safeFetch<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        history,
        current_location_id: currentLocationId || null,
      }),
    });
  },
};
