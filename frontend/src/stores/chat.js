import { defineStore } from 'pinia';
import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000, // 5 second timeout
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token if it exists
const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Token ${token}`;
}

export const useChatStore = defineStore('chat', {
  state: () => ({
    chats: [],
    currentChat: null,
    messages: [],
    socket: null,
    error: null,
    isReconnecting: false
  }),
  
  actions: {
    async fetchChats() {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          api.defaults.headers.common['Authorization'] = `Token ${token}`;
        }

        console.log(token)
        const response = await api.get('/chat/list/');
        this.chats = response.data;
        this.error = null;
      } catch (err) {
        if (!err.response) {
          this.error = 'Unable to connect to server. Please check if the server is running.';
        } else {
          this.error = 'Failed to fetch chats. Please try again later.';
        }
        console.error('Failed to fetch chats:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      }
    },
    
    async createChat(name) {
      try {
        const response = await api.post('/chat/create/', { name });
        this.chats.push(response.data);
        this.error = null;
        return response.data;
      } catch (err) {
        if (!err.response) {
          this.error = 'Unable to connect to server. Please check if the server is running.';
        } else {
          this.error = 'Failed to create chat. Please try again.';
        }
        console.error('Failed to create chat:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      }
    },

    async deleteChat(chatId) {
      try {
        await api.delete(`/chat/${chatId}/`);
        this.chats = this.chats.filter(chat => chat.id !== chatId);
        this.error = null;
      } catch (err) {
        if (!err.response) {
          this.error = 'Unable to connect to server. Please check if the server is running.';
        } else {
          this.error = 'Failed to delete chat. Please try again.';
        }
        console.error('Failed to delete chat:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      }
    },
    
    async addUserToChat(username, chatId) {
      try {
        await api.post('/chat/add_user/', {
          username,
          chat_id: chatId
        });
        this.error = null;
      } catch (err) {
        if (!err.response) {
          this.error = 'Unable to connect to server. Please check if the server is running.';
        } else {
          this.error = 'Failed to add user to chat. Please check the username and try again.';
        }
        console.error('Failed to add user:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText
        });
      }
    },
    
    connectToChat(chatId) {
      const token = localStorage.getItem('token');
      if (!token) {
        this.error = 'Authentication required. Please log in.';
        return;
      }

      this.disconnectFromChat();
      
      try {
        this.socket = new WebSocket(
          `ws://${window.location.hostname}:8000/ws/chat/${chatId}/?token=${token}`
        );
        
        this.socket.onmessage = (event) => {
          const message = JSON.parse(event.data);
          // Handle different message types
          if (message.type === 'delete') {
            this.messages = this.messages.filter(m => m.id !== message.message_id);
          } else if (message.type === 'edit') {
            const index = this.messages.findIndex(m => m.id === message.message_id);
            if (index !== -1) {
              this.messages[index] = {
                ...this.messages[index],
                message: message.new_text,
                edited: true
              };
            }
          } else {
            // Regular message
            this.messages.push({
              id: message.id || Date.now(), // Fallback to timestamp if no ID
              message: message.message || '',
              user: message.user || 'Unknown',
              datetime: message.datetime || new Date().toISOString(),
              avatar_url: message.avatar_url || null,
              edited: message.edited || false
            });
          }
        };

        this.socket.onerror = (err) => {
          this.error = 'Connection error. Please check if the server is running.';
          console.error('WebSocket error:', {
            message: err.message || 'WebSocket connection failed'
          });
        };

        this.socket.onclose = () => {
          if (!this.isReconnecting) {
            this.error = 'Connection lost. Attempting to reconnect...';
            this.isReconnecting = true;
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
              if (this.error === 'Connection lost. Attempting to reconnect...') {
                this.connectToChat(chatId);
              }
              this.isReconnecting = false;
            }, 5000);
          }
        };

        this.socket.onopen = () => {
          this.error = null;
          this.isReconnecting = false;
        };
      } catch (err) {
        this.error = 'Failed to establish WebSocket connection. Please check if the server is running.';
        console.error('WebSocket connection error:', {
          message: err.message
        });
      }
    },
    
    sendMessage(message) {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ 
          type: 'message',
          message 
        }));
      } else {
        this.error = 'Unable to send message. Please check your connection.';
      }
    },

    editMessage(messageId, newText) {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          type: 'edit',
          message_id: messageId,
          new_text: newText
        }));
      } else {
        this.error = 'Unable to edit message. Please check your connection.';
      }
    },

    deleteMessage(messageId) {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          type: 'delete',
          message_id: messageId
        }));
      } else {
        this.error = 'Unable to delete message. Please check your connection.';
      }
    },
    
    disconnectFromChat() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
        this.messages = [];
        this.error = null;
        this.isReconnecting = false;
      }
    }
  }
});