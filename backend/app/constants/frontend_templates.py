
"""
Templates for generating frontend code files.
"""

HTTP_CLIENT_TEMPLATE = '''import axios from 'axios';
import { ENV } from '../config/env';

const httpClient = axios.create({
  baseURL: ENV.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: ENV.API_TIMEOUT || 10000,
});

httpClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

httpClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
       // Handle unauthorized
    }
    return Promise.reject(error);
  }
);

export default httpClient;
'''

ENV_TS_TEMPLATE = '''export const ENV = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
  API_TIMEOUT: Number(import.meta.env.VITE_API_TIMEOUT) || 10000,
};
'''

ENDPOINTS_TS_TEMPLATE = '''export const ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        ME: '/auth/me',
    },
    // Add feature specific endpoints here
} as const;
'''

ROUTES_TS_TEMPLATE = '''export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
    NOT_FOUND: '*',
} as const;
'''

APP_TSX_TEMPLATE = '''import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from './constants/routes';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Home from './pages/Home';

function App() {
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-accent/30">
        <Routes>
           <Route path={ROUTES.HOME} element={<Home />} />
           <Route path={ROUTES.LOGIN} element={<Login />} />
           <Route 
             path={ROUTES.DASHBOARD} 
             element={isAuthenticated ? <Dashboard /> : <Navigate to={ROUTES.LOGIN} />} 
           />
           <Route path={ROUTES.NOT_FOUND} element={<Navigate to={ROUTES.HOME} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
'''
