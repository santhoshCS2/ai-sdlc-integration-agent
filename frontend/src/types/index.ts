export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}