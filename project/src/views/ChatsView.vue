<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <h1 class="text-xl font-semibold text-gray-800">Chats</h1>
        <div class="flex items-center space-x-4">
          <router-link
              to="/profile"
              class="text-gray-600 hover:text-gray-800 transition duration-200"
          >
            <User class="h-5 w-5" />
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

    <div v-if="chatStore.error" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
      <div class="bg-red-100 p-4 rounded-md">
        <p class="text-red-700">{{ chatStore.error }}</p>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-lg font-medium text-gray-900">Your Chats</h2>
        <button
            @click="showNewChatModal = true"
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200 flex items-center"
        >
          <Plus class="h-4 w-4 mr-2" />
          New Chat
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
            v-for="chat in chatStore.chats"
            :key="chat.id"
            class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition duration-200"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <MessageSquare class="h-8 w-8 text-blue-500" />
              <h3 class="ml-3 text-lg font-medium text-gray-900">{{ chat.name }}</h3>
            </div>
            <button
                @click="() => handleDeleteChat(chat)"
                class="text-red-500 hover:text-red-700 transition duration-200"
                title="Delete chat"
            >
              <Trash2 class="h-5 w-5" />
            </button>
          </div>

          <p class="text-sm text-gray-600 mb-4">
            {{ chat.users.length }} participants
          </p>

          <div class="flex justify-between items-center">
            <router-link
                :to="'/chat/' + chat.id"
                class="text-blue-500 hover:text-blue-600 transition duration-200"
            >
              Join Chat
            </router-link>

            <button
                @click="() => showAddUserModal(chat)"
                class="text-gray-500 hover:text-gray-700 transition duration-200"
            >
              <UserPlus class="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- New Chat Modal -->
    <div v-if="showNewChatModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Create New Chat</h3>

        <form @submit.prevent="createNewChat">
          <input
              v-model="newChatName"
              type="text"
              placeholder="Chat name"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 mb-4"
          />

          <div class="flex justify-end space-x-3">
            <button
                type="button"
                @click="showNewChatModal = false"
                class="text-gray-600 hover:text-gray-800 transition duration-200"
            >
              Cancel
            </button>
            <button
                type="submit"
                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add User Modal -->
    <div v-if="selectedChat" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Add User to {{ selectedChat.name }}</h3>

        <form @submit.prevent="addUserToChat">
          <input
              v-model="newUsername"
              type="text"
              placeholder="Username"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 mb-4"
          />

          <div class="flex justify-end space-x-3">
            <button
                type="button"
                @click="selectedChat = null"
                class="text-gray-600 hover:text-gray-800 transition duration-200"
            >
              Cancel
            </button>
            <button
                type="submit"
                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200"
            >
              Add User
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';
import { LogOut, MessageSquare, Plus, UserPlus, Trash2, User } from 'lucide-vue-next';

const authStore = useAuthStore();
const chatStore = useChatStore();

const showNewChatModal = ref(false);
const newChatName = ref('');
const selectedChat = ref(null);
const newUsername = ref('');

onMounted(() => {
  chatStore.fetchChats();
});

const createNewChat = async () => {
  try {
    await chatStore.createChat(newChatName.value);
    showNewChatModal.value = false;
    newChatName.value = '';
  } catch (error) {
    // Error is handled in the store
  }
};

const showAddUserModal = (chat) => {
  selectedChat.value = chat;
};

const addUserToChat = async () => {
  if (!selectedChat.value) return;

  try {
    await chatStore.addUserToChat(newUsername.value, selectedChat.value.id);

    // Обновляем количество участников в локальном состоянии
    selectedChat.value.users.push({ username: newUsername.value });
    // Сбрасываем поля после добавления
    newUsername.value = '';
  } catch (error) {
    console.error("Error adding user to chat:", error);
  }
};


const handleDeleteChat = async (chat) => {
  if (confirm(`Are you sure you want to delete the chat "${chat.name}"?`)) {
    await chatStore.deleteChat(chat.id);
  }
};
</script>