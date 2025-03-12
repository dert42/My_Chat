import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './index.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Initialize call socket connection if user is already logged in
const token = localStorage.getItem('token');
if (token) {
    // Import and initialize call store after app is mounted
    import('./stores/call').then(({ useCallStore }) => {
        const callStore = useCallStore();
        callStore.connectToCallSocket();
    });
}

app.mount('#app');