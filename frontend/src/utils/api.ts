import axios from 'axios';
import { AuthResponse, LoginData, RegisterData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (data: LoginData): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }).then(res => res.data);
  },

  register: (data: RegisterData): Promise<AuthResponse> =>
    api.post('/auth/register', data).then(res => res.data),

  me: () => api.get('/auth/me').then(res => res.data),
};

export const agentAPI = {
  getAgents: () => api.get('/agents/').then(res => res.data),
  chat: (query: string, agentId: number, conversationId?: number, files?: File[]) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('agent_id', agentId.toString());
    if (conversationId) {
      formData.append('conversation_id', conversationId.toString());
    }
    if (files) {
      files.forEach(file => formData.append('files', file));
    }
    return api.post('/agents/chat', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then(res => res.data);
  },
  getStatus: () => api.get('/agents/status').then(res => res.data),
};

export default api;