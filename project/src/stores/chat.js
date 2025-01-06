import { defineStore } from 'pinia';
import axios from 'axios';

export const useChatStore = defineStore('chat', {
  state: () => ({
    chats: [],
    currentChat: null,
    messages: [],
    socket: null
  }),
  
  actions: {
    async fetchChats() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/chat/list/');
        this.chats = response.data;
      } catch (error) {
        console.error('Failed to fetch chats:', error);
        throw error;
      }
    },
    
    async createChat(name) {
      try {
        const response = await axios.post('http://127.0.0.1:8000/chat/create/', { name });
        this.chats.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Failed to create chat:', error);
        throw error;
      }
    },
    
    async addUserToChat(username, roomName) {
      try {
        await axios.post('http://127.0.0.1:8000/chat/add_user/', {
          username,
          room_name: roomName
        });
      } catch (error) {
        console.error('Failed to add user:', error);
        throw error;
      }
    },
    
    connectToChat(roomName) {
      const token = localStorage.getItem('token');
      if (!token) return;

      this.disconnectFromChat(); // Close existing connection if any
      
      this.socket = new WebSocket(
        `ws://${window.location.hostname}:8000/ws/chat/${roomName}/?token=${token}`
      );
      
      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.messages.push(message);
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    },
    
    sendMessage(message) {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ message }));
      }
    },
    
    disconnectFromChat() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
        this.messages = [];
      }
    }
  }
});