import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useToastStore = defineStore('toast', () => {
    const toasts = ref([]);

    /**
     * Show a toast message
     * @param {string} message - The message to display
     * @param {'success' | 'error' | 'info' | 'warning'} type - The type of toast
     * @param {number} duration - Duration in milliseconds
     */
    const show = (message, type = 'info', duration = 3000) => {
        const id = Date.now();
        toasts.value.push({
            id,
            message,
            type,
            duration
        });

        if (duration > 0) {
            setTimeout(() => {
                remove(id);
            }, duration);
        }
    };

    const remove = (id) => {
        const index = toasts.value.findIndex(t => t.id === id);
        if (index !== -1) {
            toasts.value.splice(index, 1);
        }
    };

    const success = (message, duration) => show(message, 'success', duration);
    const error = (message, duration) => show(message, 'error', duration);
    const warn = (message, duration) => show(message, 'warning', duration);
    const info = (message, duration) => show(message, 'info', duration);

    return {
        toasts,
        show,
        remove,
        success,
        error,
        warn,
        info
    };
});
