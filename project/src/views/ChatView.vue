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
          :key="message.id"
          :class="[
            'flex items-start space-x-3',
            message.user === authStore.user?.username ? 'flex-row-reverse space-x-reverse' : ''
          ]"
        >
          <img
            :src="message.avatar_url || 'https://via.placeholder.com/40'"
            :alt="message.user"
            class="w-10 h-10 rounded-full object-cover flex-shrink-0"
          />
          
          <div
            :class="[
              'p-4 rounded-lg max-w-[80%] relative group',
              message.user === authStore.user?.username
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-800'
            ]"
            @contextmenu.prevent="showContextMenu($event, message)"
          >
            <div class="flex items-center mb-1">
              <span class="font-medium">{{ message.user }}</span>
              <span class="text-xs ml-2 opacity-75">
                {{ formatDate(message.datetime) }}
                {{ message.edited ? '(edited)' : '' }}
              </span>
            </div>
            <p>{{ message.message }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.show"
      :style="{
        position: 'fixed',
        top: contextMenu.y + 'px',
        left: contextMenu.x + 'px'
      }"
      class="bg-white rounded-lg shadow-lg py-2 min-w-[160px] z-50"
      v-click-outside="hideContextMenu"
    >
      <button
        v-if="contextMenu.message?.user === authStore.user?.username"
        @click="editMessage(contextMenu.message)"
        class="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center"
      >
        <Edit2 class="h-4 w-4 mr-2" />
        Edit
      </button>
      <button
        v-if="contextMenu.message?.user === authStore.user?.username"
        @click="deleteMessage(contextMenu.message)"
        class="w-full px-4 py-2 text-left hover:bg-gray-100 text-red-600 flex items-center"
      >
        <Trash2 class="h-4 w-4 mr-2" />
        Delete
      </button>
    </div>

    <!-- Edit Message Modal -->
    <div
      v-if="editingMessage"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Edit Message</h3>
        <form @submit.prevent="handleEditMessage">
          <input
            v-model="editedMessageText"
            type="text"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 mb-4"
            @keydown.esc="cancelEdit"
          />
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="cancelEdit"
              class="text-gray-600 hover:text-gray-800 transition duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200"
            >
              Save
            </button>
          </div>
        </form>
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
import { useAuthStore } from '../stores/auth';
import { ArrowLeft, Send, Edit2, Trash2 } from 'lucide-vue-next';
import { format } from 'date-fns';

const route = useRoute();
const chatStore = useChatStore();
const authStore = useAuthStore();
const newMessage = ref('');

// Context menu state
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  message: null
});

// Edit message state
const editingMessage = ref(null);
const editedMessageText = ref('');

const currentChatName = computed(() => {
  const chat = chatStore.chats.find(chat => chat.id === parseInt(route.params.id));
  return chat?.name || '';
});

onMounted(() => {
  const chatId = route.params.id;
  if (chatId) {
    chatStore.connectToChat(chatId);
  }
  // Add click listener to hide context menu
  document.addEventListener('click', hideContextMenu);
});

onUnmounted(() => {
  chatStore.disconnectFromChat();
  document.removeEventListener('click', hideContextMenu);
});

const showContextMenu = (event, message) => {
  event.preventDefault();
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    message
  };
};

const hideContextMenu = () => {
  contextMenu.value.show = false;
};

const editMessage = (message) => {
  editingMessage.value = message;
  editedMessageText.value = message.message;
  hideContextMenu();
};

const cancelEdit = () => {
  editingMessage.value = null;
  editedMessageText.value = '';
};

const handleEditMessage = () => {
  if (editedMessageText.value.trim() && editingMessage.value) {
    chatStore.editMessage(editingMessage.value.id, editedMessageText.value);
    cancelEdit();
  }
};

const deleteMessage = (message) => {
  if (confirm('Are you sure you want to delete this message?')) {
    chatStore.deleteMessage(message.id);
  }
  hideContextMenu();
};

const sendMessage = () => {
  if (newMessage.value.trim()) {
    chatStore.sendMessage(newMessage.value);
    newMessage.value = '';
  }
};

const formatDate = (datetime) => {
  return format(new Date(datetime), 'HH:mm');
};

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};
</script>