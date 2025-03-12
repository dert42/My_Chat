<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">Register</h1>
      
      <div v-if="error" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
        <p class="flex items-center">
          <AlertCircle class="h-5 w-5 mr-2" />
          {{ error }}
        </p>
      </div>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <input
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
            @input="error = ''"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
            @input="error = ''"
          />
        </div>
        
        <button
          type="submit"
          class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-200 flex items-center justify-center"
          :disabled="isLoading"
        >
          <Loader2 v-if="isLoading" class="h-5 w-5 mr-2 animate-spin" />
          <span>{{ isLoading ? 'Registering...' : 'Register' }}</span>
        </button>
      </form>
      
      <p class="mt-4 text-center text-sm text-gray-600">
        Already have an account?
        <router-link 
          to="/login" 
          class="text-blue-500 hover:text-blue-600"
          @click="authStore.clearError"
        >
          Login
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { AlertCircle, Loader2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const router = useRouter();
const username = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

const handleRegister = async () => {
  if (isLoading.value) return;

  try {
    isLoading.value = true;
    await axios.post('http://localhost:8000/register/', {
      username: username.value,
      password: password.value,
    });
    error.value = '';
    await authStore.login(username.value, password.value);
  } catch (err) {
    if (!err.response) {
      error.value = 'Unable to connect to server. Please check if the server is running.';
    } else if (err.response.status === 400) {
      error.value = 'Username already exists or invalid input';
    } else {
      error.value = 'Registration failed. Please try again later.';
    }
    console.error('Registration failed:', {
      message: err.message,
      status: err.response?.status,
      statusText: err.response?.statusText
    });
  } finally {
    isLoading.value = false;
  }
};
</script>