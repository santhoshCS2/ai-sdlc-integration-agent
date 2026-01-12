import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User, LoginData, RegisterData } from '../types';
import { AuthService } from '../api/services/authService';

interface AuthContextType {
  user: User | null;
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      AuthService.getCurrentUser()
        .then(setUser)
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (data: LoginData) => {
    const response = await AuthService.login(data);
    localStorage.setItem('token', response.access_token);
    // Fetch user details immediately after login to ensure state is updated
    const userData = await AuthService.getCurrentUser();
    setUser(userData);
  };

  const register = async (data: RegisterData) => {
    await AuthService.register(data);
    // Auto login after registration
    await login({ username: data.email, password: data.password });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};