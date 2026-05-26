<script setup>
import { useToastStore } from '@/stores/useToastStore';
import { 
    CheckCircle, 
    XCircle, 
    AlertCircle, 
    Info, 
    X 
} from 'lucide-vue-next';

const toastStore = useToastStore();

const icons = {
    success: CheckCircle,
    error: XCircle,
    warning: AlertCircle,
    info: Info
};

const styles = {
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-900/30 dark:border-emerald-800 dark:text-emerald-300',
    error: 'bg-rose-50 border-rose-200 text-rose-800 dark:bg-rose-900/30 dark:border-rose-800 dark:text-rose-300',
    warning: 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-900/30 dark:border-amber-800 dark:text-amber-300',
    info: 'bg-indigo-50 border-indigo-200 text-indigo-800 dark:bg-indigo-900/30 dark:border-indigo-800 dark:text-indigo-300'
};

const iconColors = {
    success: 'text-emerald-500',
    error: 'text-rose-500',
    warning: 'text-amber-500',
    info: 'text-indigo-500'
};
</script>

<template>
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-3 w-full max-w-sm pointer-events-none">
        <TransitionGroup 
            name="toast"
            enter-active-class="transform transition duration-300 ease-out"
            enter-from-class="translate-x-full opacity-0"
            enter-to-class="translate-x-0 opacity-100"
            leave-active-class="transform transition duration-200 ease-in"
            leave-from-class="opacity-100"
            leave-to-class="translate-x-4 opacity-0"
        >
            <div 
                v-for="toast in toastStore.toasts" 
                :key="toast.id"
                class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl border shadow-lg backdrop-blur-md"
                :class="styles[toast.type]"
            >
                <!-- Icon -->
                <div class="mt-0.5 shrink-0">
                    <component :is="icons[toast.type]" :class="iconColors[toast.type]" class="w-5 h-5" />
                </div>

                <!-- Message -->
                <div class="flex-1 text-sm font-medium leading-relaxed">
                    {{ toast.message }}
                </div>

                <!-- Close Button -->
                <button 
                    @click="toastStore.remove(toast.id)"
                    class="mt-0.5 shrink-0 opacity-50 hover:opacity-100 transition-opacity p-0.5 hover:bg-black/5 dark:hover:bg-white/5 rounded"
                >
                    <X class="w-4 h-4" />
                </button>
            </div>
        </TransitionGroup>
    </div>
</template>

<style scoped>
.toast-move {
    transition: all 0.3s ease;
}
</style>
