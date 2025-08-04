import axios from 'axios';
import { 
  SimulationCreateRequest, 
  SimulationResponse,
  SimulationResult 
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Simulations
  createSimulation: async (data: SimulationCreateRequest): Promise<SimulationResponse> => {
    const response = await apiClient.post('/api/simulations', data);
    return response.data;
  },

  getSimulation: async (id: string): Promise<SimulationResponse> => {
    const response = await apiClient.get(`/api/simulations/${id}`);
    return response.data;
  },

  getSimulationStatus: async (id: string) => {
    const response = await apiClient.get(`/api/simulations/${id}/status`);
    return response.data;
  },

  getSimulationResults: async (id: string): Promise<{ id: string; result: SimulationResult; completed_at: string }> => {
    const response = await apiClient.get(`/api/simulations/${id}/results`);
    return response.data;
  },
};

// WebSocket connection helper
export const createWebSocketConnection = (simulationId: string, onMessage: (data: any) => void) => {
  const wsUrl = `${API_BASE_URL.replace('http', 'ws')}/ws/simulations/${simulationId}`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket connected');
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };

  return ws;
};