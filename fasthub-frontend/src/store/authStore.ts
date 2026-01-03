import { create } from 'zustand';
import { User } from '../types/models';
import { authApi } from '../api/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string, rememberMe?: boolean) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authApi.login({ email, password });
      
      // Save tokens (use localStorage for remember_me, sessionStorage otherwise)
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('access_token', data.access_token);
      storage.setItem('refresh_token', data.refresh_token);
      
      // Also save remember_me preference
      if (rememberMe) {
        localStorage.setItem('remember_me', 'true');
      } else {
        localStorage.removeItem('remember_me');
      }
      
      // Fetch user data
      const { data: user } = await authApi.getCurrentUser();
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false 
      });
      throw error;
    }
  },

  register: async (data: any) => {
    set({ isLoading: true, error: null });
    try {
      const { data: response } = await authApi.register(data);
      
      // Save tokens
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      // Fetch user data
      const { data: user } = await authApi.getCurrentUser();
      
      set({ 
        user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false 
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens and state from both storages
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      set({ 
        user: null, 
        isAuthenticated: false 
      });
    }
  },

  fetchCurrentUser: async () => {
    console.error('[DEBUG] fetchCurrentUser called');
    // Check both localStorage and sessionStorage for token
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    console.error('[DEBUG] token exists:', !!token);
    if (!token) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }
    
    // GUARD: Prevent multiple simultaneous calls
    const currentState = get();
    if (currentState.isLoading) {
      console.error('[DEBUG] already loading, skipping');
      return;
    }

    console.error('[DEBUG] setting isLoading=true');
    set({ isLoading: true });
    try {
      console.error('[DEBUG] calling authApi.getCurrentUser()');
      const { data: user } = await authApi.getCurrentUser();
      console.error('[DEBUG] got user:', user);
      const currentUser = get().user;
      
      // Only update if user actually changed (prevent unnecessary re-renders)
      if (!currentUser || currentUser.id !== user.id) {
        console.error('[DEBUG] setting user, isAuthenticated=true, isLoading=false');
        set({ 
          user, 
          isAuthenticated: true, 
          isLoading: false 
        });
      } else {
        console.error('[DEBUG] user unchanged, setting isLoading=false');
        set({ isLoading: false });
      }
    } catch (error) {
      console.error('[DEBUG] fetchCurrentUser error:', error);
      // Token invalid, clear auth from both storages
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      set({ 
        user: null, 
        isAuthenticated: false, 
        isLoading: false 
      });
    }
  },

  clearError: () => set({ error: null }),
}));
