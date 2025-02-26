import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';

export const useCallStore = defineStore('call', {
  state: () => ({
    localStream: null,
    peerConnections: new Map(), // username -> RTCPeerConnection
    pendingIceCandidates: new Map(), // username -> ICE candidate[]
    isInCall: false,
    participants: new Set(),
    error: null,
    socket: null,
    pendingCall: null,
    currentCallId: null,
    incomingCall: null
  }),

  actions: {
    connectToCallSocket() {
      const authStore = useAuthStore();
      if (!authStore.token) return;

      this.socket = new WebSocket(
          `ws://${window.location.hostname}:8000/ws/call/?token=${authStore.token}`
      );

      this.socket.onmessage = async (event) => {
        const signal = JSON.parse(event.data);
        console.log('WebSocket received signal:', signal.type, signal);
        await this.handleCallSignal(signal);
      };

      this.socket.onerror = (error) => {
        console.error('Call WebSocket error:', error);
        this.error = 'Connection error occurred';
      };

      this.socket.onclose = () => {
        console.log('Call WebSocket closed, attempting to reconnect in 5 seconds');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => this.connectToCallSocket(), 5000);
      };

      this.socket.onopen = () => {
        console.log('Call WebSocket connected successfully');
      };
    },

    async initializeCall(targetUsername) {
      try {
        console.log('Initializing call to:', targetUsername);
        // Get user media first
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        });

        this.localStream = stream;

        // Send call creation request to server
        this.sendCallSignal({
          type: 'create-call',
          target: targetUsername,
          from: useAuthStore().user.username
        });

        // Store pending call information
        this.pendingCall = {
          target: targetUsername,
          stream: stream
        };

      } catch (err) {
        this.error = 'Failed to access camera/microphone';
        console.error('Media error:', err);
      }
    },

    createPeerConnection(username) {
      console.log('Creating peer connection for:', username);
      const peerConnection = new RTCPeerConnection({
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' }
        ]
      });

      // Add local tracks to the connection
      if (this.localStream) {
        this.localStream.getTracks().forEach(track => {
          peerConnection.addTrack(track, this.localStream);
        });
      }

      // Handle ICE candidates
      peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
          this.sendCallSignal({
            type: 'ice-candidate',
            target: username,
            from: useAuthStore().user.username,
            callId: this.currentCallId,
            candidate: event.candidate
          });
        }
      };

      // Handle incoming tracks
      peerConnection.ontrack = (event) => {
        console.log('Received remote track from:', username, event.track.kind);

        // The VideoCall component will handle displaying the tracks
        // We'll trigger a reactivity update by creating a new Set from participants
        this.participants = new Set([...this.participants]);
      };

      this.peerConnections.set(username, peerConnection);
      return peerConnection;
    },

    async handleCallSignal(signal) {
      const { type, from, target, sdp, candidate, callId } = signal;
      console.log('Processing signal:', { type, from, target, callId });

      switch (type) {
        case 'call-created': {
          // Server confirmed call creation, now we can proceed with the call
          console.log('Call created, proceeding with call setup');
          if (this.pendingCall && target === this.pendingCall.target) {
            this.isInCall = true;
            this.participants.add(target);
            this.currentCallId = callId;

            // Create peer connection and send offer
            const peerConnection = await this.createPeerConnection(target);
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);

            this.sendCallSignal({
              type: 'call-invite',
              target: target,
              from: useAuthStore().user.username,
              callId: callId,
              sdp: offer
            });

            // Clear pending call
            this.pendingCall = null;
          }
          break;
        }

        case 'call-invite': {
          console.log('Received call invitation from:', from);

          // If we're already in a call or have a pending outgoing call, reject the new call
          if (this.isInCall || this.pendingCall) {
            console.log('Rejecting call - already in call or pending call');
            this.sendCallSignal({
              type: 'call-rejected',
              target: from,
              from: useAuthStore().user.username,
              callId: callId,
              reason: this.isInCall ? 'User is already in another call' : 'User is initiating another call'
            });
            return;
          }

          // Store incoming call information immediately
          this.incomingCall = {
            from,
            callId,
            sdp
          };

          console.log('Incoming call set:', this.incomingCall);
          break;
        }

        case 'call-answer': {
          console.log('Received call answer from:', from);
          const peerConnection = this.peerConnections.get(from);
          if (peerConnection) {
            try {
              await peerConnection.setRemoteDescription(new RTCSessionDescription(sdp));
              console.log('Remote description set successfully');

              // Add any pending ICE candidates
              const pendingCandidates = this.pendingIceCandidates.get(from) || [];
              console.log(`Adding ${pendingCandidates.length} pending ICE candidates`);
              for (const candidate of pendingCandidates) {
                await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
              }
              this.pendingIceCandidates.delete(from);
            } catch (err) {
              console.error('Error setting remote description:', err);
              this.error = 'Failed to establish connection';
            }
          } else {
            console.error('No peer connection found for:', from);
          }
          break;
        }

        case 'call-rejected': {
          const reason = signal.reason || 'Call rejected';
          console.log('Call rejected by:', from, 'Reason:', reason);
          this.error = `${from} rejected the call: ${reason}`;
          this.participants.delete(from);
          this.cleanupPeerConnection(from);

          // Clear call state if this was our outgoing call
          if (this.pendingCall?.target === from) {
            this.pendingCall = null;
            this.currentCallId = null;
            if (this.localStream) {
              this.localStream.getTracks().forEach(track => track.stop());
              this.localStream = null;
            }
          }
          break;
        }

        case 'ice-candidate': {
          if (!callId) {
            console.error('Received ICE candidate without callId');
            return;
          }

          console.log('Received ICE candidate from:', from, 'for call:', callId);

          // Only process ICE candidates if they match our current call
          if (this.currentCallId && callId === this.currentCallId) {
            const peerConnection = this.peerConnections.get(from);
            if (peerConnection?.remoteDescription) {
              try {
                console.log('Adding ICE candidate immediately');
                await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
              } catch (err) {
                console.error('Error adding ICE candidate:', err);
              }
            } else {
              // Store the candidate for later
              console.log('Storing ICE candidate for later');
              const pendingCandidates = this.pendingIceCandidates.get(from) || [];
              pendingCandidates.push(candidate);
              this.pendingIceCandidates.set(from, pendingCandidates);
            }
          } else {
            console.log('Ignoring ICE candidate for different call', {
              currentCallId: this.currentCallId,
              receivedCallId: callId
            });
          }
          break;
        }

        case 'participant-left': {
          console.log('Participant left the call:', from);
          this.participants.delete(from);
          this.cleanupPeerConnection(from);
          break;
        }

        case 'call-error': {
          console.error('Call error:', signal.message);
          this.error = signal.message || 'Call creation failed';
          if (this.pendingCall) {
            // Cleanup if we have a pending call
            if (this.localStream) {
              this.localStream.getTracks().forEach(track => track.stop());
              this.localStream = null;
            }
            this.pendingCall = null;
          }
          break;
        }
      }
    },

    async acceptIncomingCall() {
      if (!this.incomingCall) {
        console.error('No incoming call to accept');
        return;
      }

      const { from, callId, sdp } = this.incomingCall;
      console.log('Accepting incoming call from:', from);

      try {
        this.participants.add(from);
        this.currentCallId = callId;

        // Get user media if not already available
        if (!this.localStream) {
          console.log('Getting user media for incoming call');
          const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
          });
          this.localStream = stream;
        }

        this.isInCall = true;

        // Create peer connection
        const peerConnection = await this.createPeerConnection(from);

        // Set remote description (offer)
        console.log('Setting remote description (offer)');
        await peerConnection.setRemoteDescription(new RTCSessionDescription(sdp));

        // Add any pending ICE candidates
        const pendingCandidates = this.pendingIceCandidates.get(from) || [];
        console.log(`Adding ${pendingCandidates.length} pending ICE candidates`);
        for (const candidate of pendingCandidates) {
          await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        }
        this.pendingIceCandidates.delete(from);

        // Create answer
        console.log('Creating answer');
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);

        // Send answer back
        this.sendCallSignal({
          type: 'call-answer',
          target: from,
          from: useAuthStore().user.username,
          callId: callId,
          sdp: answer
        });

        // Clear incoming call
        this.incomingCall = null;
      } catch (err) {
        console.error('Error accepting call:', err);
        this.error = 'Failed to accept call';
        this.sendCallSignal({
          type: 'call-rejected',
          target: from,
          from: useAuthStore().user.username,
          callId: callId,
          reason: 'Failed to setup media'
        });
        this.incomingCall = null;
      }
    },

    rejectIncomingCall(reason = 'User declined') {
      if (!this.incomingCall) {
        console.error('No incoming call to reject');
        return;
      }

      const { from, callId } = this.incomingCall;
      console.log('Rejecting incoming call from:', from);

      this.sendCallSignal({
        type: 'call-rejected',
        target: from,
        from: useAuthStore().user.username,
        callId: callId,
        reason
      });

      this.incomingCall = null;
    },

    async addParticipant(username) {
      if (this.participants.has(username)) {
        this.error = 'User is already in the call';
        return;
      }

      if (!this.currentCallId) {
        this.error = 'No active call to add participant to';
        return;
      }

      try {
        console.log('Adding participant to call:', username);
        // Create peer connection
        const peerConnection = await this.createPeerConnection(username);

        // Create offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        // Add to participants and send invite
        this.participants.add(username);
        this.sendCallSignal({
          type: 'call-invite',
          target: username,
          from: useAuthStore().user.username,
          callId: this.currentCallId,
          sdp: offer
        });
      } catch (err) {
        this.error = 'Failed to add participant';
        console.error('Add participant error:', err);
      }
    },

    sendCallSignal(signal) {
      if (this.socket?.readyState === WebSocket.OPEN) {
        console.log('Sending signal:', signal.type, { target: signal.target, callId: signal.callId });
        this.socket.send(JSON.stringify(signal));
      } else {
        console.error('WebSocket is not connected');
        this.error = 'Connection error. Please try again.';
      }
    },

    cleanupPeerConnection(username) {
      console.log('Cleaning up peer connection for:', username);
      const peerConnection = this.peerConnections.get(username);
      if (peerConnection) {
        peerConnection.close();
        this.peerConnections.delete(username);
      }
    },

    endCall() {
      console.log('Ending call');
      // Notify all participants
      this.participants.forEach(username => {
        this.sendCallSignal({
          type: 'participant-left',
          target: username,
          from: useAuthStore().user.username,
          callId: this.currentCallId
        });
      });

      // Cleanup all peer connections
      this.peerConnections.forEach((_, username) => {
        this.cleanupPeerConnection(username);
      });

      // Stop local stream
      if (this.localStream) {
        this.localStream.getTracks().forEach(track => track.stop());
        this.localStream = null;
      }

      this.isInCall = false;
      this.participants.clear();
      this.error = null;
      this.pendingCall = null;
      this.currentCallId = null;
      this.incomingCall = null;
      this.pendingIceCandidates.clear();
    },

    disconnect() {
      console.log('Disconnecting from call WebSocket');
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
    }
  }
});