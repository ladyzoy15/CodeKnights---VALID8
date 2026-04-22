<template>
  <section class="sg-sub-page">
    <header class="sg-sub-header dashboard-enter dashboard-enter--1">
      <button class="sg-sub-back" type="button" @click="goBack">
        <ArrowLeft :size="20" />
      </button>
      <h1 class="sg-sub-title">Excuse Letters</h1>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden p-8 flex flex-col">
      <!-- Filters -->
      <div class="shrink-0 mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div class="flex items-center space-x-2">
          <!-- Status Filter -->
          <div class="relative">
            <select
              v-model="filters.status"
              class="appearance-none pl-4 pr-10 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent cursor-pointer"
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>
        
        <!-- Search -->
        <div class="relative w-full sm:w-72">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <input
            v-model="filters.search"
            type="text"
            class="block w-full pl-10 pr-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
            placeholder="Search students or events..."
          />
        </div>
      </div>

      <!-- Data Table -->
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-gray-50/80 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider sticky top-0 z-10 shadow-sm border-b border-gray-200 dark:border-gray-700">
                <th class="py-4 px-6 font-semibold">Student</th>
                <th class="py-4 px-6 font-semibold">Event</th>
                <th class="py-4 px-6 font-semibold">Date Submitted</th>
                <th class="py-4 px-6 font-semibold text-center">Status</th>
                <th class="py-4 px-6 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
              <tr v-if="loading" class="animate-pulse">
                <td colspan="5" class="py-12 text-center text-gray-500 dark:text-gray-400">Loading excuse letters...</td>
              </tr>
              <tr v-else-if="filteredLetters.length === 0">
                <td colspan="5" class="py-16">
                  <div class="flex flex-col items-center justify-center text-center">
                    <div class="w-16 h-16 bg-gray-50 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4 border border-gray-100 dark:border-gray-700 shadow-inner">
                      <svg class="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </div>
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-1">No Excuse Letters Found</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
                      There are currently no excuse letters matching your filters.
                    </p>
                  </div>
                </td>
              </tr>
              <tr
                v-else
                v-for="letter in filteredLetters"
                :key="letter.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800/60 transition-colors group"
              >
                <td class="py-4 px-6">
                  <div class="flex items-center space-x-3">
                    <div class="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 text-sm font-bold flex-shrink-0">
                      {{ letter.studentName?.charAt(0) || 'S' }}
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{{ letter.studentName || 'Unknown Student' }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ letter.course || 'Course' }} • Yr {{ letter.yearLevel || '-' }}</p>
                    </div>
                  </div>
                </td>
                <td class="py-4 px-6">
                  <p class="text-sm text-gray-900 dark:text-gray-100 font-medium">{{ letter.eventName || 'Event Name' }}</p>
                  <p v-if="letter.attachmentUrl" class="text-xs text-primary-500 mt-1 flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                    Has Attachment
                  </p>
                </td>
                <td class="py-4 px-6 text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(letter.submittedAt) }}
                </td>
                <td class="py-4 px-6 text-center">
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
                <td class="py-4 px-6 text-right">
                  <button
                    @click="openReviewModal(letter)"
                    class="inline-flex items-center space-x-1 px-3 py-1.5 text-sm font-medium rounded-lg text-primary-600 bg-primary-50 hover:bg-primary-100 dark:text-primary-400 dark:bg-primary-900/20 dark:hover:bg-primary-900/40 transition-colors"
                  >
                    <span v-if="letter.status === 'Pending'">Review</span>
                    <span v-else>View Details</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination (Mock) -->
        <div class="border-t border-gray-100 dark:border-gray-800 px-6 py-3 flex items-center justify-between bg-gray-50/50 dark:bg-gray-900/50">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Showing <span class="font-medium text-gray-900 dark:text-white">{{ filteredLetters.length }}</span> results
          </p>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <ExcuseLetterReviewModal
      v-model="isModalOpen"
      :letter="selectedLetter"
      :can-review="canReview"
      @reviewed="handleReviewed"
    />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft } from 'lucide-vue-next';
import { useExcuseLetters } from '@/composables/useExcuseLetters';
import { useSgDashboard } from '@/composables/useSgDashboard';
import ExcuseLetterReviewModal from '@/components/desktop/events/ExcuseLetterReviewModal.vue';

const { fetchGovernanceLetters, loading, letters } = useExcuseLetters();
const { activeUnitId, hasPermission } = useSgDashboard();
const router = useRouter();

const goBack = () => router.push('/sg');

const canReview = computed(() => hasPermission('Review Excuse Letter'));

const isModalOpen = ref(false);
const selectedLetter = ref(null);

const filters = ref({
  status: 'All',
  search: ''
});

const loadLetters = async () => {
  if (activeUnitId.value) {
    // We would use actual active unit ID here
    await fetchGovernanceLetters(activeUnitId.value);
  } else {
    // Fallback for mock environment
    await fetchGovernanceLetters(1);
  }
};

onMounted(() => {
  loadLetters();
});

const filteredLetters = computed(() => {
  return letters.value.filter(letter => {
    const matchesStatus = filters.value.status === 'All' || letter.status === filters.value.status;
    const matchesSearch = !filters.value.search || 
      (letter.studentName || '').toLowerCase().includes(filters.value.search.toLowerCase()) ||
      (letter.eventName || '').toLowerCase().includes(filters.value.search.toLowerCase());
    
    return matchesStatus && matchesSearch;
  });
});

const openReviewModal = (letter) => {
  selectedLetter.value = letter;
  isModalOpen.value = true;
};

const handleReviewed = () => {
  // Option to reload or local state is updated in composable
  console.log('Letter reviewed');
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
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
