import { create } from 'zustand';
import { User } from '../types';
import { api } from '../services/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  fetchCurrentUser: () => Promise<void>;
  login: (credentials: { identifier: string; password: string }) => Promise<boolean>;
  register: (data: { username: string; email: string; password: string; full_name?: string }) => Promise<boolean>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  fetchCurrentUser: async () => {
    try {
      set({ isLoading: true, error: null });
      const res = await api.get('/auth/me');
      if (res.data?.success && res.data?.data) {
        set({ user: res.data.data, isAuthenticated: true, isLoading: false });
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false });
      }
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (credentials) => {
    try {
      set({ isLoading: true, error: null });
      const res = await api.post('/auth/login', credentials);
      if (res.data?.success) {
        set({ user: res.data.data, isAuthenticated: true, isLoading: false });
        return true;
      }
      set({ error: res.data?.error || 'Login failed', isLoading: false });
      return false;
    } catch (err: any) {
      set({
        error: err.response?.data?.error || 'Unable to connect to server. Please check your credentials.',
        isLoading: false
      });
      return false;
    }
  },

  register: async (userData) => {
    try {
      set({ isLoading: true, error: null });
      const res = await api.post('/auth/register', userData);
      if (res.data?.success) {
        set({ user: res.data.data, isAuthenticated: true, isLoading: false });
        return true;
      }
      set({ error: res.data?.error || 'Registration failed', isLoading: false });
      return false;
    } catch (err: any) {
      set({
        error: err.response?.data?.error || 'Registration failed. Please check input values.',
        isLoading: false
      });
      return false;
    }
  },

  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      set({ user: null, isAuthenticated: false });
    }
  },

  clearError: () => set({ error: null })
}));
