<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">Login</h1>
      
      <div v-if="authStore.error" class="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
        <p class="flex items-center">
          <AlertCircle class="h-5 w-5 mr-2" />
          {{ authStore.error }}
        </p>
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <input
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
            @input="authStore.clearError"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
            @input="authStore.clearError"
          />
        </div>
        
        <button
          type="submit"
          class="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition duration-200 flex items-center justify-center"
          :disabled="isLoading"
        >
          <Loader2 v-if="isLoading" class="h-5 w-5 mr-2 animate-spin" />
          <span>{{ isLoading ? 'Logging in...' : 'Login' }}</span>
        </button>
      </form>
      
      <p class="mt-4 text-center text-sm text-gray-600">
        Don't have an account?
        <router-link 
          to="/register" 
          class="text-blue-500 hover:text-blue-600"
          @click="authStore.clearError"
        >
          Register
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { AlertCircle, Loader2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const username = ref('');
const password = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (isLoading.value) return;
  
  try {
    isLoading.value = true;
    await authStore.login(username.value, password.value);
  } catch (error) {
    // Error is handled in the store
  } finally {
    isLoading.value = false;
  }
};
</script>