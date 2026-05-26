<template>
  <div ref="pillRef" class="aura-chat-pill-wrapper">
    <div
      class="aura-chat-pill"
      :class="isMiniOpen
        ? 'aura-chat-pill--expanded'
        : 'aura-chat-pill--collapsed'"
      @click="!isMiniOpen ? openPill() : null"
    >
      <!-- Collapsed State: Logo + Label -->
      <div
        class="aura-chat-pill__collapsed-content"
        :class="isMiniOpen ? 'opacity-0 pointer-events-none' : 'opacity-100'"
      >
        <img :src="activeAuraLogo" alt="Aura" class="aura-chat-pill__logo" />
        <span class="aura-chat-pill__label">
          Talk to<br>Aura AI
        </span>
      </div>

      <!-- Expanded (Mini Chat) State -->
      <div
        class="aura-chat-pill__expanded-content"
        :class="isMiniOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'"
      >
        <!-- Mini Header -->
        <div class="mini-header">
          <button
            class="mini-header-btn"
            aria-label="Minimize chat"
            @click.stop="closeMini"
          >
            <ChevronDown :size="16" />
          </button>

          <div class="mini-header-actions">
            <button
              class="mini-header-btn"
              aria-label="Copy"
              @click.stop="copyConversation"
            >
              <Check v-if="copyStatus === 'copied'" :size="14" class="text-green-500" />
              <Copy v-else :size="14" />
            </button>
            <button
              class="mini-header-btn"
              aria-label="New chat"
              @click.stop="startNewConversation"
            >
              <Plus :size="15" />
            </button>
            <button
              class="mini-header-btn"
              aria-label="Expand"
              @click.stop="expandToFull"
            >
              <Maximize2 :size="15" />
            </button>
          </div>
        </div>

        <!-- Mini Messages -->
        <div class="mini-messages" ref="scrollEl">
          <TransitionGroup name="mini-bubble" tag="div" class="mini-messages-inner">
            <template v-for="msg in messages" :key="msg.id">
              <div
                v-if="msg.sender === 'user' || (msg.text && msg.text.trim().length > 0)"
                :class="['mini-bubble', msg.sender === 'ai' ? 'mini-bubble--ai' : 'mini-bubble--user']"
              >
                <ChatMarkdownMessage :text="msg.text" />
              </div>
            </template>

            <div v-if="isTyping" key="typing" class="mini-bubble mini-bubble--ai mini-bubble--typing">
              <div class="dot" style="animation-delay: 0ms" />
              <div class="dot" style="animation-delay: 150ms" />
              <div class="dot" style="animation-delay: 300ms" />
            </div>
          </TransitionGroup>
        </div>

        <!-- Mini Input -->
        <div class="mini-input-wrap">
          <div class="mini-input-row">
            <input
              v-model="inputText"
              type="text"
              class="mini-input"
              placeholder="Ask Aura..."
              :disabled="isTyping"
              @keyup.enter="sendMessage"
            />
            <button
              class="mini-send-btn"
              :disabled="!inputText.trim() || isTyping"
              @click="sendMessage"
            >
              <Send :size="14" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Maximize2, Send, ChevronDown, Copy, Plus, Check } from 'lucide-vue-next'
import { activeAuraLogo } from '@/config/theme.js'
import { useChat } from '@/composables/useChat.js'
import ChatMarkdownMessage from '@/components/desktop/ai/ChatMarkdownMessage.vue'

const {
  messages,
  inputText,
  isTyping,
  isMiniOpen,
  conversationId,
  sendMessage,
  startNewConversation,
  selectConversation,
  openPill,
  closeMini,
  expandToFull,
  copyConversation,
  copyStatus,
  scrollEl
} = useChat()

const pillRef = ref(null)

// Load messages when mini chat expands
watch(isMiniOpen, (val) => {
  if (val && conversationId.value) {
    selectConversation(conversationId.value).catch(() => {
      startNewConversation()
    })
  }
})

function handleOutsideClick(event) {
  if (isMiniOpen.value && pillRef.value && !pillRef.value.contains(event.target)) {
    closeMini()
  }
}

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onUnmounted(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<style scoped>
.aura-chat-pill-wrapper {
  position: relative;
  width: 40px;
  height: 74px;
  margin: 0 8px 6px;
  z-index: 50;
}

.aura-chat-pill {
  position: absolute;
  bottom: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  origin: bottom left;
  background: var(--color-primary);
}

.aura-chat-pill--collapsed {
  width: 40px;
  height: 74px;
  border-radius: 26px;
  cursor: pointer;
}

.aura-chat-pill--collapsed:hover {
  filter: brightness(1.1);
  transform: scale(1.05);
}

.aura-chat-pill--collapsed:active {
  transform: scale(0.95);
}

.aura-chat-pill--expanded {
  width: 360px;
  height: 550px;
  transform: translateX(60px);
  border-radius: 32px;
  cursor: default;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.aura-chat-pill__collapsed-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  items-center: center;
  justify-content: center;
  gap: 4px;
  transition: opacity 0.3s;
}

.aura-chat-pill__logo {
  width: 24px;
  height: 24px;
  object-fit: contain;
  opacity: 0.9;
}

.aura-chat-pill__label {
  font-size: 8px;
  font-weight: 800;
  text-align: center;
  line-height: 1.2;
  color: var(--color-banner-text);
}

.aura-chat-pill__expanded-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  padding: 12px;
  transition: opacity 0.3s 0.1s;
}

/* Mini Header */
.mini-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 0 4px;
}

.mini-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mini-header-btn {
  padding: 6px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-banner-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.mini-header-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

/* Mini Messages */
.mini-messages {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none;
  padding-bottom: 4px;
}

.mini-messages::-webkit-scrollbar {
  display: none;
}

.mini-messages-inner {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-bubble {
  max-width: 90%;
  padding: 10px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.6;
  word-break: break-word;
  font-family: 'Manrope', sans-serif;
}

.mini-bubble--ai {
  align-self: flex-start;
  background: #ffffff;
  color: #000000;
}

.mini-bubble--user {
  align-self: flex-end;
  background: rgba(0, 0, 0, 0.1);
  color: var(--color-banner-text);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.mini-bubble--typing {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  animation: bounce 1s infinite ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  40% { transform: translateY(-4px); }
}

/* Mini Input */
.mini-input-wrap {
  margin-top: 4px;
}

.mini-input-row {
  height: 36px;
  border-radius: 18px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  padding: 0 4px 0 12px;
  gap: 8px;
  background: rgba(0, 0, 0, 0.05);
}

.mini-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-banner-text);
}

.mini-input::placeholder {
  color: var(--color-banner-text);
  opacity: 0.4;
}

.mini-send-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-banner-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.mini-send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Animations */
.mini-bubble-enter-active {
  animation: mini-bubble-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.mini-bubble--ai.mini-bubble-enter-active { transform-origin: bottom left; }
.mini-bubble--user.mini-bubble-enter-active { transform-origin: bottom right; }

@keyframes mini-bubble-pop {
  0% { opacity: 0; transform: scale(0.6); }
  70% { opacity: 1; transform: scale(1.03); }
  100% { transform: scale(1); }
}

.opacity-0 { opacity: 0; }
.opacity-100 { opacity: 1; }
.pointer-events-none { pointer-events: none; }
</style>
