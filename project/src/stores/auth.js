import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000, // 5 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login/', {
          username,
          password
        });
        
        this.token = response.data.token;
        localStorage.setItem('token', this.token);
        api.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        this.error = null;
        
        router.push('/chats');
      } catch (err) {
        if (!err.response) {
          this.error = 'Unable to connect to server. Please check if the server is running.';
        } else if (err.response.status === 401) {
          this.error = 'Invalid username or password';
        } else {
          this.error = 'Login failed. Please try again later.';
        }
        console.error('Login failed:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      }
    },
    
    logout() {
      this.token = null;
      this.user = null;
      this.error = null;
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      delete axios.defaults.headers.common['Authorization'];
      router.push('/login');
    },

    clearError() {
      this.error = null;
    }
  }
});