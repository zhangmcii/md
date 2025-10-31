<template>
  <div class="music-player-container">
    <el-avatar
      class="music-avatar"
      :size="avatarSize"
      :style="{ marginTop: isMobile ? '0' : '2rem' }"
      @mouseenter="showMusicPlayer = true"
      @mouseleave="showMusicPlayer = false"
    >
      <img
        :src="avatar"
        alt="Avatar"
        :class="{ 'leleo-spin': isPlaying }"
        :style="{ animation: isPlaying ? 'spin 6s linear infinite' : 'none', transformOrigin: 'center' }"
      />

      <transition name="fade">
        <div v-show="showMusicPlayer" class="music-player-overlay" :class="{ 'fade-in': showMusicPlayer }">
          <div v-if="audioLoading" class="loading-spinner">
            <el-icon class="is-loading">
              <Loading />
            </el-icon>
          </div>

          <div class="song-info">
            <span class="song-title">{{ currentSong?.title || '加载中...' }}</span>
            <span class="song-author">{{ currentSong?.author || '' }}</span>
          </div>

          <audio
            ref="audioPlayer"
            :src="currentSong?.url"
            @waiting="onWaiting"
            @canplay="onCanPlay"
            style="display: none;"
          ></audio>

          <div class="player-controls">
            <el-button
              :size="controlSize"
              circle
              @click="previousTrack"
              class="control-btn"
            >
              <el-icon><CaretLeft /></el-icon>
            </el-button>

            <el-button
              :size="playButtonSize"
              circle
              @click="togglePlay"
              class="play-btn"
            >
              <el-icon v-if="isPlaying"><VideoPause /></el-icon>
              <el-icon v-else><VideoPlay /></el-icon>
            </el-button>

            <el-button
              :size="controlSize"
              circle
              @click="nextTrack"
              class="control-btn"
            >
              <el-icon><CaretRight /></el-icon>
            </el-button>
          </div>
        </div>
      </transition>
    </el-avatar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElAvatar, ElButton, ElIcon } from 'element-plus'
import { Loading, CaretLeft, CaretRight, VideoPlay, VideoPause } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  // 头像图片URL
  avatar: {
    type: String,
    required: true
  },
  // 音乐配置
  musicConfig: {
    type: Object,
    required: true,
    validator: (value) => {
      return value.server && value.type && value.id
    }
  },
  // 是否移动端
  isMobile: {
    type: Boolean,
    default: false
  },
  // 头像大小
  avatarSize: {
    type: [Number, String],
    default: 140
  }
})

// Emits
const emit = defineEmits(['toggle-background-muted'])

// Refs
const showMusicPlayer = ref(false)
const isPlaying = ref(false)
const playlistIndex = ref(0)
const audioLoading = ref(false)
const musicInfo = ref([])
const musicInfoLoading = ref(false)
const audioPlayer = ref(null)

// Computed
const currentSong = computed(() => {
  return musicInfo.value[playlistIndex.value]
})

const controlSize = computed(() => {
  return props.isMobile ? 'small' : 'default'
})

const playButtonSize = computed(() => {
  return props.isMobile ? 'default' : 'large'
})

// Methods
const fetchMusicInfo = async () => {
  musicInfoLoading.value = true
  try {
    console.log('开始请求音乐信息，配置:', props.musicConfig)
    const response = await fetch(
      `https://api.i-meto.com/meting/api?server=${props.musicConfig.server}&type=${props.musicConfig.type}&id=${props.musicConfig.id}`
    )
    if (!response.ok) {
      throw new Error(`网络请求失败: ${response.status}`)
    }
    const data = await response.json()
    console.log('音乐信息获取成功:', data)
    musicInfo.value = data
  } catch (error) {
    console.error('请求音乐信息失败:', error)
    // 设置默认音乐信息以防请求失败
    musicInfo.value = [{
      title: '音乐加载失败',
      author: '请检查网络连接',
      url: ''
    }]
  } finally {
    musicInfoLoading.value = false
  }
}

const setupAudioListener = () => {
  if (audioPlayer.value) {
    audioPlayer.value.addEventListener('ended', nextTrack)
  }
}

const togglePlay = () => {
  if (!audioPlayer.value) return

  if (!isPlaying.value) {
    audioPlayer.value.play()
    emit('toggle-background-muted', true)
    isPlaying.value = true
  } else {
    audioPlayer.value.pause()
    emit('toggle-background-muted', false)
    isPlaying.value = false
  }
}

const previousTrack = () => {
  playlistIndex.value = playlistIndex.value > 0 ? playlistIndex.value - 1 : musicInfo.value.length - 1
  updateAudio()
}

const nextTrack = () => {
  playlistIndex.value = playlistIndex.value < musicInfo.value.length - 1 ? playlistIndex.value + 1 : 0
  updateAudio()
}

const updateAudio = () => {
  if (!audioPlayer.value || !currentSong.value) return

  audioPlayer.value.src = currentSong.value.url
  isPlaying.value = true
  audioPlayer.value.play()
}

const onWaiting = () => {
  audioLoading.value = true
}

const onCanPlay = () => {
  audioLoading.value = false
}

// Lifecycle
onMounted(async () => {
  await fetchMusicInfo()
  setupAudioListener()
})

onBeforeUnmount(() => {
  if (audioPlayer.value) {
    audioPlayer.value.removeEventListener('ended', nextTrack)
  }
})

// Watchers
watch(audioLoading, (val) => {
  if (!val && audioPlayer.value && audioPlayer.value.paused) {
    isPlaying.value = false
  }
})
</script>

<style scoped>
.music-player-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.music-avatar {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.music-avatar:hover {
  transform: scale(1.05);
}

.music-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.music-player-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  /* background: rgba(0, 0, 0, 0); */
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 10px;
  box-sizing: border-box;
}

.song-info {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  color: white;
  font-size: 12px;
  pointer-events: none;
}

.song-title {
  position: absolute;
  top: 1.6rem;
  left: 0;
  right: 0;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 10px;
}

.song-author {
  position: absolute;
  bottom: 1.4rem;
  left: 0;
  right: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 10px;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  border: none !important;
  color: white !important;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
}

.play-btn {
  background: rgba(255, 255, 255, 0.3) !important;
  border: none !important;
  color: white !important;
}

.play-btn:hover {
  background: rgba(255, 255, 255, 0.4) !important;
}

.loading-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.leleo-spin {
  animation: spin 6s linear infinite !important;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.fade-in {
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.8s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .song-title {
    font-size: 10px;
    top: 1.2rem;
  }

  .song-author {
    font-size: 9px;
    bottom: 1rem;
  }

  .player-controls {
    gap: 6px;
  }
}
</style>



// vue.js
<music-player
:avatar="configdata.avatar"
:music-config="configdata.musicPlayer"
:is-mobile="xs||sm"
@toggle-background-muted="handleBackgroundMuted"
></music-player>

// app.js
import musicPlayer from './components/music2.vue';

handleBackgroundMuted(isMuted) {
  if (this.$refs.VdPlayer) {
    this.$refs.VdPlayer.muted = isMuted;
  }
},