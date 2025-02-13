<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <h1 class="text-xl font-semibold text-gray-800">Profile</h1>
        <div class="flex items-center space-x-4">
          <router-link
              to="/chats"
              class="text-gray-600 hover:text-gray-800 transition duration-200"
          >
            <MessageSquare class="h-5 w-5" />
          </router-link>
          <button
              @click="authStore.logout"
              class="text-gray-600 hover:text-gray-800 transition duration-200"
          >
            <LogOut class="h-5 w-5" />
          </button>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center space-x-6">
          <div class="relative">
            <img
                :src="authStore.avatarUrl || 'https://img.icons8.com/?size=100&id=41799&format=png&color=000000'"
                alt="Profile"
                class="w-32 h-32 rounded-full object-cover"
            />
            <label
                class="absolute bottom-0 right-0 bg-blue-500 text-white p-2 rounded-full cursor-pointer hover:bg-blue-600 transition duration-200"
            >
              <input
                  type="file"
                  class="hidden"
                  accept="image/*"
                  @change="handleAvatarChange"
              />
              <Camera class="h-5 w-5" />
            </label>
          </div>

          <div>
            <h2 class="text-2xl font-semibold text-gray-900">
              {{ authStore.user?.username }}
            </h2>
          </div>
        </div>

        <div v-if="error" class="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
          {{ error }}
        </div>

        <div v-if="success" class="mt-4 p-4 bg-green-100 text-green-700 rounded-md">
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { LogOut, MessageSquare, Camera } from 'lucide-vue-next';

const authStore = useAuthStore();
const error = ref('');
const success = ref('');

const handleAvatarChange = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // Validate file type
  if (!file.type.startsWith('image/')) {
    error.value = 'Please select an image file';
    return;
  }

  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Image size should be less than 5MB';
    return;
  }

  try {
    error.value = '';
    await authStore.updateAvatar(file);
    success.value = 'Profile picture updated successfully';
    setTimeout(() => {
      success.value = '';
    }, 3000);
  } catch (err) {
    error.value = 'Failed to update profile picture';
  }
};
</script>