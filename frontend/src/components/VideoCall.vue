<template>
  <div>
    <!-- Call Confirmation Dialog -->
    <CallConfirmDialog
        :show="!!callStore.incomingCall"
        :caller="callStore.incomingCall?.from || ''"
        @accept="callStore.acceptIncomingCall()"
        @reject="callStore.rejectIncomingCall()"
    />

    <div class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-40" v-if="callStore.isInCall">
      <div class="bg-gray-900 p-6 rounded-lg w-full max-w-6xl">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-white text-xl font-semibold">Video Call</h2>
          <div class="flex items-center space-x-4">
            <button
                @click="showAddParticipant = true"
                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200 flex items-center"
            >
              <UserPlus class="h-4 w-4 mr-2" />
              Add Participant
            </button>
            <button
                @click="callStore.endCall"
                class="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition duration-200 flex items-center"
            >
              <PhoneOff class="h-4 w-4 mr-2" />
              End Call
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <!-- Local video -->
          <div class="relative">
            <video
                ref="localVideo"
                autoplay
                muted
                playsinline
                class="w-full rounded-lg bg-gray-800"
            ></video>
            <span class="absolute bottom-2 left-2 text-white bg-black bg-opacity-50 px-2 py-1 rounded">
              You
            </span>
          </div>

          <!-- Remote videos -->
          <div
              v-for="participant in callStore.participants"
              :key="participant"
              class="relative"
          >
            <video
                :ref="el => setRemoteVideoRef(el, participant)"
                autoplay
                playsinline
                class="w-full rounded-lg bg-gray-800"
            ></video>
            <span class="absolute bottom-2 left-2 text-white bg-black bg-opacity-50 px-2 py-1 rounded">
              {{ participant }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Participant Modal -->
    <div v-if="showAddParticipant" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg w-full max-w-md">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Add Participant</h3>

        <form @submit.prevent="handleAddParticipant">
          <input
              v-model="newParticipant"
              type="text"
              placeholder="Username"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 mb-4"
          />

          <div class="flex justify-end space-x-3">
            <button
                type="button"
                @click="showAddParticipant = false"
                class="text-gray-600 hover:text-gray-800 transition duration-200"
            >
              Cancel
            </button>
            <button
                type="submit"
                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition duration-200"
            >
              Add
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch} from 'vue';
import {useCallStore} from '../stores/call';
import {UserPlus, PhoneOff} from 'lucide-vue-next';
import CallConfirmDialog from './CallConfirmDialog.vue';

const callStore = useCallStore();
const localVideo = ref(null);
const showAddParticipant = ref(false);
const newParticipant = ref('');
const remoteVideos = ref(new Map());

onMounted(() => {
  console.log('VideoCall component mounted');
  updateLocalVideo();

  // Update remote videos for any existing participants
  callStore.participants.forEach(participant => {
    updateRemoteVideo(participant);
  });
});

// Watch for changes to localStream and update video element
watch(() => callStore.localStream, (newStream) => {
  console.log('Local stream changed:', newStream ? 'stream available' : 'no stream');
  updateLocalVideo();
});

// Watch for changes to incomingCall to log when it changes
watch(() => callStore.incomingCall, (newCall) => {
  console.log('Incoming call changed:', newCall ? `from ${newCall.from}` : 'no call');
});

// Watch for changes to participants
watch(() => callStore.participants, (newParticipants) => {
  console.log('Participants changed:', [...newParticipants]);
  // Update remote videos for all participants
  newParticipants.forEach(participant => {
    updateRemoteVideo(participant);
  });
}, {deep: true});

// Watch for changes to peerConnections
watch(() => callStore.peerConnections, (newPeerConnections) => {
  console.log('PeerConnections changed, updating remote videos');
  // Update all remote videos when peer connections change
  callStore.participants.forEach(participant => {
    updateRemoteVideo(participant);
  });
}, {deep: true});

function updateLocalVideo() {
  if (callStore.localStream && localVideo.value) {
    console.log('Updating local video element with stream');
    localVideo.value.srcObject = callStore.localStream;
  }
}

function setRemoteVideoRef(el, participant) {
  if (el) {
    remoteVideos.value.set(participant, el);
    updateRemoteVideo(participant);
  }
}

function updateRemoteVideo(participant) {
  const peerConnection = callStore.peerConnections.get(participant);
  const videoElement = remoteVideos.value.get(participant);

  if (videoElement && peerConnection) {
    console.log(`Checking remote streams for participant: ${participant}`);

    // Get remote streams from the peer connection
    const remoteStreams = peerConnection.getReceivers()
        .filter(receiver => receiver.track && receiver.track.kind === 'video')
        .map(receiver => receiver.track);

    if (remoteStreams.length > 0) {
      console.log(`Found ${remoteStreams.length} remote video tracks for ${participant}`);

      // Create a MediaStream with the remote tracks if not already set
      if (!videoElement.srcObject || videoElement.srcObject.getTracks().length === 0) {
        const stream = new MediaStream();
        remoteStreams.forEach(track => stream.addTrack(track));
        videoElement.srcObject = stream;
        console.log(`Set remote stream for ${participant}`);
      }
    } else {
      console.log(`No remote streams found yet for ${participant}`);
    }
  }
}

onUnmounted(() => {
  console.log('VideoCall component unmounted');
  callStore.endCall();
});

const handleAddParticipant = async () => {
  if (newParticipant.value.trim()) {
    await callStore.addParticipant(newParticipant.value);
    showAddParticipant.value = false;
    newParticipant.value = '';
  }
};
</script>