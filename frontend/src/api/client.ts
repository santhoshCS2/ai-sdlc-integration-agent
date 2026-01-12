
import axios from 'axios';
import { ENV } from '../config/env';

const apiClient = axios.create({
    baseURL: ENV.API_BASE_URL,
});

apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        // Optional: Handle 401 errors globally here
        if (error.response && error.response.status === 401) {
            // Dispatch logout event or similar if needed
        }
        return Promise.reject(error);
    }
);

export default apiClient;
