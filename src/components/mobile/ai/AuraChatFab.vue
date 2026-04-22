<template>
  <button
    class="aura-chat-fab"
    aria-label="Talk to Aura AI"
    @click="openFull"
  >
    <img :src="activeAuraLogo" alt="Aura" class="aura-chat-fab__logo" />
    <span class="aura-chat-fab__ping" v-if="hasUnread" />
  </button>
</template>

<script setup>
import { activeAuraLogo } from '@/config/theme.js'
import { useChat } from '@/composables/useChat.js'

const { openFull } = useChat()

// For now, no unread logic, but we can add it later.
const hasUnread = false
</script>

<style scoped>
.aura-chat-fab {
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background: var(--color-primary);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  position: relative;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.aura-chat-fab:active {
  transform: scale(0.9);
}

.aura-chat-fab__logo {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.aura-chat-fab__ping {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #ff4d4d;
  border: 2px solid var(--color-primary);
  border-radius: 50%;
}
</style>
