<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <!-- Header -->
    <div class="sticky top-0 z-20 bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 px-4 py-4 shadow-sm">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">My Excuse Letters</h1>
        <button
          @click="loadLetters"
          class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 transition-colors"
          :class="{ 'animate-spin': loading }"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
      </div>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Status of your submitted excuse letters</p>
    </div>

    <!-- Content -->
    <div class="p-4 space-y-4">
      <div v-if="loading && letters.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p class="text-gray-500 dark:text-gray-400">Loading letters...</p>
      </div>

      <div v-else-if="letters.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
        <div class="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
          <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">No letters found</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 px-10">You haven't submitted any excuse letters yet.</p>
      </div>

      <div v-else v-for="letter in sortedLetters" :key="letter.id" class="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm border border-gray-100 dark:border-gray-700 active:scale-[0.98] transition-transform">
        <div class="flex justify-between items-start mb-3">
          <div class="flex-1 min-w-0 mr-2">
            <h4 class="font-bold text-gray-900 dark:text-white truncate">{{ letter.eventName || 'Event Name' }}</h4>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Submitted {{ formatDate(letter.submittedAt) }}</p>
          </div>
          <span
            :class="{
              'px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider': true,
              'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-500': letter.status === 'Pending',
              'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-500': letter.status === 'Approved',
              'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-500': letter.status === 'Rejected'
            }"
          >
            {{ letter.status }}
          </span>
        </div>

        <div v-if="letter.attachmentUrl" class="flex items-center text-xs text-primary-500 mb-3 bg-primary-50 dark:bg-primary-900/10 p-2 rounded-lg">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
          Document Attached
        </div>

        <div class="space-y-2">
          <div>
            <span class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Reason</span>
            <p class="text-sm text-gray-700 dark:text-gray-300 line-clamp-3">{{ letter.reason }}</p>
          </div>
          <div v-if="letter.reviewerRemarks">
            <span class="text-[10px] text-gray-400 uppercase font-bold tracking-wider">Remarks</span>
            <p class="text-sm text-gray-700 dark:text-gray-300 italic">"{{ letter.reviewerRemarks }}"</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
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
    const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  } catch (e) {
    return dateString;
  }
};
</script>
