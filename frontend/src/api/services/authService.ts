
import apiClient from '../client';
import { ENDPOINTS } from '../endpoints';
import { AuthResponse, LoginData, RegisterData, User } from '../../types';

export const AuthService = {
    login: async (data: LoginData): Promise<AuthResponse> => {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.LOGIN, formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data;
    },

    register: async (data: RegisterData): Promise<AuthResponse> => {
        const response = await apiClient.post<AuthResponse>(ENDPOINTS.AUTH.REGISTER, data);
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await apiClient.get<User>(ENDPOINTS.AUTH.ME);
        return response.data;
    }
};
