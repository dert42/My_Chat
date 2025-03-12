<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Global VideoCall component to handle calls from anywhere in the app -->
    <VideoCall />
    <router-view></router-view>
  </div>
</template>

<script setup>
import VideoCall from './components/VideoCall.vue';
</script>