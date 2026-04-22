<template>
  <section class="sg-sub-page">
    <header class="sg-sub-header dashboard-enter dashboard-enter--1">
      <h1 class="sg-sub-title">My Excuse Letters</h1>
      <button
        @click="loadLetters"
        class="sg-sub-action"
        :disabled="loading"
      >
        <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
        <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>
    </header>

    <div class="flex-1 overflow-hidden p-8 flex flex-col">
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50/80 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider sticky top-0 z-10 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <th class="py-4 px-6 font-semibold">Event Name</th>
                <th class="py-4 px-6 font-semibold">Submitted On</th>
                <th class="py-4 px-6 font-semibold">Status</th>
                <th class="py-4 px-6 font-semibold">Remarks</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
              <tr v-if="loading" class="animate-pulse">
                <td colspan="4" class="py-12 text-center text-gray-500 dark:text-gray-400">Loading your excuse letters...</td>
              </tr>
              <tr v-else-if="letters.length === 0">
                <td colspan="4" class="py-16">
                  <div class="flex flex-col items-center justify-center text-center">
                    <div class="w-16 h-16 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4 border border-gray-100 dark:border-gray-700 shadow-inner">
                      <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"></path></svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-1">No Excuse Letters</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                      You haven't submitted any excuse letters yet.
                    </p>
                  </div>
                </td>
              </tr>
              <tr
                v-else
                v-for="letter in sortedLetters"
                :key="letter.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800/60 transition-colors"
              >
                <td class="py-4 px-6">
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{{ letter.eventName || 'Event Name' }}</span>
                    <span v-if="letter.attachmentUrl" class="text-xs text-primary-500 mt-1 flex items-center">
                      <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                      Document Attached
                    </span>
                  </div>
                </td>
                <td class="py-4 px-6 text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(letter.submittedAt) }}
                </td>
                <td class="py-4 px-6">
                  <span
                    :class="{
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border': true,
                      'bg-yellow-50 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800/50': letter.status === 'Pending',
                      'bg-green-50 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800/50': letter.status === 'Approved',
                      'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800/50': letter.status === 'Rejected'
                    }"
                  >
                    {{ letter.status }}
                  </span>
                </td>
                <td class="py-4 px-6">
                  <p class="text-sm text-gray-800 dark:text-gray-200 max-w-xs truncate" :title="letter.reviewerRemarks || 'N/A'">
                    {{ letter.reviewerRemarks || '-' }}
                  </p>
                  <p v-if="letter.status !== 'Pending' && letter.reviewedBy" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    Reviewed by Officer #{{ letter.reviewedBy }}
                  </p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { RefreshCw } from 'lucide-vue-next';
import { useExcuseLetters } from '@/composables/useExcuseLetters';

const { fetchStudentLetters, loading, letters } = useExcuseLetters();

const loadLetters = async () => {
  await fetchStudentLetters();
};

onMounted(() => {
  loadLetters();
});

const sortedLetters = computed(() => {
  return [...letters.value].sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  } catch (e) {
    return dateString;
  }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 20px;
}
</style>
