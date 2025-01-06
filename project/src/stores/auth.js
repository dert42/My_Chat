import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('http://127.0.0.1:8000/login/', {
          username,
          password
        });
        
        this.token = response.data.token;
        localStorage.setItem('token', this.token);
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        
        router.push('/chats');
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      router.push('/login');
    }
  }
});