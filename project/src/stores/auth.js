import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const useAuthStore = defineStore('auth', {
  state: () => {
    const token = localStorage.getItem('token');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Token ${token}`;
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    }
    return {
      token: token,
      user: null,
      error: null,
      avatarUrl: null
    };
  },

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username, password) {
      try {
        // Clear any existing token first
        this.clearAuth();

        const response = await api.post('/login/', {
          username,
          password
        });

        this.token = response.data.token;
        this.user = { username };

        // Set token in localStorage and axios defaults
        localStorage.setItem('token', this.token);
        api.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;

        this.error = null;

        // Fetch user profile after login
        await this.fetchProfile();

        router.push('/chats');
      } catch (err) {
        this.clearAuth();
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

    async logout() {
      try {
        if (this.token) {
          await api.post('/logout/', {
            username: this.user?.username,
            token: this.token
          });
        }
      } catch (err) {
        console.error('Logout request failed:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      } finally {
        this.clearAuth();
        router.push('/login');
      }
    },

    clearAuth() {
      // Clear state
      this.token = null;
      this.user = null;
      this.error = null;
      this.avatarUrl = null;

      // Remove token from localStorage
      localStorage.removeItem('token');

      // Clear Authorization headers
      delete api.defaults.headers.common['Authorization'];
      delete axios.defaults.headers.common['Authorization'];
    },

    async fetchProfile() {
      try {
        const response = await api.get('/user/profile/');
        this.user = {
          username: response.data.username,
          avatarUrl: response.data.avatar_url
        };
        this.avatarUrl = response.data.avatar_url;
      } catch (err) {
        console.error('Failed to fetch profile:', err);
        // If we get a 401 error, the token is invalid
        if (err.response?.status === 401) {
          this.clearAuth();
          router.push('/login');
        }
      }
    },

    async updateAvatar(file) {
      try {
        const formData = new FormData();
        formData.append('avatar', file);

        const response = await api.post('/user/profile/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.avatarUrl = response.data.avatar_url;
        return response.data.avatar_url;
      } catch (err) {
        console.error('Failed to update avatar:', err);
        throw err;
      }
    },

    clearError() {
      this.error = null;
    }
  }
});