<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-md">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Incoming Call</h3>
      <p class="text-gray-600 mb-6">{{ caller }} is calling you</p>

      <div class="flex justify-end space-x-3">
        <button
            @click="onReject"
            class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition duration-200 flex items-center"
        >
          <PhoneOff class="h-4 w-4 mr-2" />
          Decline
        </button>
        <button
            @click="onAccept"
            class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition duration-200 flex items-center"
        >
          <Phone class="h-4 w-4 mr-2" />
          Accept
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Phone, PhoneOff } from 'lucide-vue-next';
import { watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  caller: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['accept', 'reject']);

const onAccept = () => emit('accept');
const onReject = () => emit('reject');

// Add watch to log when dialog visibility changes
watch(() => props.show, (newValue) => {
  console.log('Call confirm dialog visibility changed:', newValue);
  if (newValue) {
    console.log('Showing call dialog for caller:', props.caller);
  }
});
</script>