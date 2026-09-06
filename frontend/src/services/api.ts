import { 
  DashboardStats, Camera, Adapter, Vehicle, VehicleRoute, 
  Watchlist, Alert, EvidenceItem, AuthUser
} from '../types';

const API_BASE = '/api';

function getAuthHeaders(customHeaders: Record<string, string> = {}): Record<string, string> {
  const headers: Record<string, string> = { ...customHeaders };
  const token = localStorage.getItem('sentinel_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  async login(username: string, password: string): Promise<AuthUser> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(err.detail || 'Authentication failed');
    }
    const data = await res.json();
    return data;
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  },

  async getDepartments(): Promise<{ id: string; name: string; code: string }[]> {
    const res = await fetch(`${API_BASE}/cameras/departments/list`, { headers: getAuthHeaders() });
    if (!res.ok) return [];
    return res.json();
  },

  async getCameras(departmentId?: string, status?: string): Promise<Camera[]> {
    let url = `${API_BASE}/cameras`;
    const params = new URLSearchParams();
    if (departmentId && departmentId !== 'ALL') params.append('department_id', departmentId);
    if (status && status !== 'ALL') params.append('status', status);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch cameras');
    return res.json();
  },

  async createCamera(cameraData: any): Promise<Camera> {
    const res = await fetch(`${API_BASE}/cameras`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(cameraData),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create camera');
    }
    return res.json();
  },

  async deleteCamera(cameraId: string): Promise<{ status: string; message: string; camera_id: string }> {
    const res = await fetch(`${API_BASE}/cameras/${cameraId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to delete camera' }));
      throw new Error(err.detail || 'Failed to delete camera');
    }
    return res.json();
  },

  async purgeAllCameras(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/cameras/purge/all`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to purge cameras' }));
      throw new Error(err.detail || 'Failed to purge cameras');
    }
    return res.json();
  },

  async ingestCatalogue(): Promise<{ total_discovered: number; newly_registered: number; updated: number; items: Camera[] }> {
    const res = await fetch(`${API_BASE}/ingest`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to synchronize government catalogue');
    return res.json();
  },

  async getAdapters(): Promise<Adapter[]> {
    const res = await fetch(`${API_BASE}/federation/adapters`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch adapters');
    return res.json();
  },

  async searchVehicles(plate?: string): Promise<Vehicle[]> {
    let url = `${API_BASE}/vehicles/search`;
    if (plate) url += `?plate=${encodeURIComponent(plate)}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to search vehicles');
    return res.json();
  },

  async getVehicleRoute(plate: string): Promise<VehicleRoute> {
    const res = await fetch(`${API_BASE}/vehicles/${encodeURIComponent(plate)}/route`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to reconstruct vehicle route');
    return res.json();
  },

  async getWatchlists(): Promise<Watchlist[]> {
    const res = await fetch(`${API_BASE}/watchlists`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch watchlists');
    return res.json();
  },

  async addWatchlistEntry(watchlistId: string, entry: { plate_number: string; reason: string; priority?: string; case_reference?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/watchlists/${watchlistId}/entries`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(entry),
    });
    if (!res.ok) throw new Error('Failed to add plate to watchlist');
    return res.json();
  },

  async getAlerts(status?: string, priority?: string): Promise<Alert[]> {
    let url = `${API_BASE}/alerts`;
    const params = new URLSearchParams();
    if (status && status !== 'ALL') params.append('status', status);
    if (priority && priority !== 'ALL') params.append('priority', priority);
    if (params.toString()) url += `?${params.toString()}`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async acknowledgeAlert(alertId: string): Promise<Alert> {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to acknowledge alert');
    return res.json();
  },

  async getEvidence(): Promise<EvidenceItem[]> {
    const res = await fetch(`${API_BASE}/evidence`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error('Failed to fetch evidence');
    return res.json();
  },

  async simulateLiveANPR(eventData: { camera_id: string; plate_number: string; confidence?: number; speed_kmh?: number; pts_ms: number; vehicle_type?: string; make_model?: string; color?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/events/simulate_anpr`, {
      method: 'POST',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(eventData),
    });
    if (!res.ok) throw new Error('Failed to simulate ANPR event');
    return res.json();
  }
};