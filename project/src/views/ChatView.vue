<template>
  <div class="min-h-screen flex flex-col bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div class="flex items-center">
          <router-link
            to="/chats"
            class="text-gray-600 hover:text-gray-800 transition duration-200 mr-4"
          >
            <ArrowLeft class="h-5 w-5" />
          </router-link>
          <h1 class="text-xl font-semibold text-gray-800">{{ currentChatName }}</h1>
        </div>
      </div>
    </nav>

    <div v-if="chatStore.error" class="bg-red-100 p-4">
      <p class="text-red-700">{{ chatStore.error }}</p>
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <div class="max-w-3xl mx-auto space-y-4">
        <div
          v-for="message in chatStore.messages"
          :key="message.datetime"
          :class="[
            'p-4 rounded-lg max-w-[80%]',
            message.user === username
              ? 'ml-auto bg-blue-500 text-white'
              : 'bg-white text-gray-800'
          ]"
        >
          <div class="flex items-center mb-1">
            <span class="font-medium">{{ message.user }}</span>
            <span class="text-xs ml-2 opacity-75">
              {{ formatDate(message.datetime) }}
            </span>
          </div>
          <p>{{ message.message }}</p>
        </div>
      </div>
    </div>

    <div class="bg-white border-t p-4">
      <div class="max-w-3xl mx-auto">
        <form @submit.prevent="sendMessage" class="flex space-x-4">
          <input
            v-model="newMessage"
            type="text"
            placeholder="Type a message..."
            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200"
          />
          <button
            type="submit"
            class="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 transition duration-200 flex items-center"
          >
            <Send class="h-4 w-4 mr-2" />
            Send
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useChatStore } from '../stores/chat';
import { ArrowLeft, Send } from 'lucide-vue-next';
import { format } from 'date-fns';

const route = useRoute();
const chatStore = useChatStore();
const newMessage = ref('');

const currentChatName = computed(() => {
  const chat = chatStore.chats.find(chat => chat.id === parseInt(route.params.id));
  return chat?.name || '';
});

onMounted(() => {
  if (currentChatName.value) {
    chatStore.connectToChat(currentChatName.value);
  }
});

onUnmounted(() => {
  chatStore.disconnectFromChat();
});

const sendMessage = () => {
  if (newMessage.value.trim()) {
    chatStore.sendMessage(newMessage.value);
    newMessage.value = '';
  }
};

const formatDate = (datetime) => {
  return format(new Date(datetime), 'HH:mm');
};
</script>