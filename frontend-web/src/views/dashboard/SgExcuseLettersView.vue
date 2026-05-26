<template>
  <section class="sg-sub-page">
    <header class="sg-sub-header dashboard-enter dashboard-enter--1">
      <button class="sg-sub-back" type="button" @click="goBack">
        <ArrowLeft :size="20" />
      </button>
      <h1 class="sg-sub-title" style="color: var(--color-primary);">Excuse Letters</h1>
    </header>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-hidden py-4 flex flex-col">
      <!-- Filters -->
      <div class="shrink-0 mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div class="flex items-center space-x-2">
          <!-- Status Filter -->
          <div class="relative">
            <select
              v-model="filters.status"
              class="appearance-none pl-4 pr-10 py-2.5 rounded-xl text-sm font-bold shadow-sm focus:outline-none focus:ring-2 focus:border-transparent cursor-pointer transition-all"
              style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border); color: var(--color-text-primary); outline-color: var(--color-primary);"
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3" style="color: var(--color-text-muted);">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"></path></svg>
            </div>
          </div>
        </div>
        
        <!-- Search -->
        <div class="relative w-full sm:w-80">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5" style="color: var(--color-text-muted);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <input
            v-model="filters.search"
            type="text"
            class="block w-full pl-10 pr-3 py-2.5 rounded-xl text-sm shadow-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all placeholder:opacity-50"
            style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border); color: var(--color-text-primary); outline-color: var(--color-primary);"
            placeholder="Search students or events..."
          />
        </div>
      </div>

      <!-- Data Table -->
      <div class="flex-1 rounded-[2rem] shadow-sm overflow-hidden flex flex-col" style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-[11px] font-black uppercase tracking-widest sticky top-0 z-10 shadow-sm backdrop-blur-md" style="background-color: color-mix(in srgb, var(--color-nav) 90%, transparent); color: var(--color-nav-text); border-bottom: 1px solid var(--color-surface-border);">
                <th class="py-5 px-8">Student</th>
                <th class="py-5 px-8">Event</th>
                <th class="py-5 px-8">Date Submitted</th>
                <th class="py-5 px-8 text-center">Status</th>
                <th class="py-5 px-8 text-right">Actions</th>
              </tr>
            </thead>
            <tbody style="border-top: 1px solid var(--color-surface-border);">
              <tr v-if="loading" class="animate-pulse">
                <td colspan="5" class="py-16 text-center font-bold text-sm" style="color: var(--color-text-muted);">Fetching excuse letters...</td>
              </tr>
              <tr v-else-if="filteredLetters.length === 0">
                <td colspan="5" class="py-24">
                  <div class="flex flex-col items-center justify-center text-center">
                    <div class="w-20 h-20 rounded-[2rem] flex items-center justify-center mb-5 shadow-inner" style="background-color: var(--color-nav);">
                      <svg class="w-10 h-10 opacity-30" style="color: var(--color-text-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    </div>
                    <h3 class="text-xl font-extrabold tracking-tight mb-2" style="color: var(--color-primary);">No Excuse Letters Found</h3>
                    <p class="text-sm px-8 font-medium leading-relaxed opacity-70" style="color: var(--color-text-primary);">
                      There are currently no excuse letters matching your filters.
                    </p>
                  </div>
                </td>
              </tr>
              <tr
                v-else
                v-for="letter in filteredLetters"
                :key="letter.id"
                class="transition-colors group hover:bg-gray-50/50 dark:hover:bg-gray-800/20" style="border-bottom: 1px solid var(--color-surface-border);"
              >
                <td class="py-5 px-8">
                  <div class="flex items-center space-x-4">
                    <div class="h-10 w-10 rounded-[1rem] flex items-center justify-center text-sm font-black flex-shrink-0 shadow-sm" style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);">
                      {{ letter.studentName?.charAt(0) || 'S' }}
                    </div>
                    <div>
                      <p class="text-sm font-bold leading-tight mb-1" style="color: var(--color-text-primary);">{{ letter.studentName || 'Unknown Student' }}</p>
                      <p class="text-[11px] font-bold opacity-50 uppercase tracking-wide" style="color: var(--color-text-primary);">{{ letter.course || 'Course' }} ΓÇó Yr {{ letter.yearLevel || '-' }}</p>
                    </div>
                  </div>
                </td>
                <td class="py-5 px-8">
                  <p class="text-sm font-bold leading-tight mb-1" style="color: var(--color-primary);">{{ letter.eventName || 'Event Name' }}</p>
                  <p v-if="letter.attachmentUrl" class="inline-flex items-center text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md w-fit mt-1" 
                        style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 12%, transparent);">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                    Has Attachment
                  </p>
                </td>
                <td class="py-5 px-8 text-sm font-medium opacity-70" style="color: var(--color-text-primary);">
                  {{ formatDate(letter.submittedAt) }}
                </td>
                <td class="py-5 px-8 text-center">
                  <span
                    class="px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-sm inline-block"
                    :style="{
                      backgroundColor: letter.status === 'Approved' ? 'color-mix(in srgb, #10B981 15%, transparent)' : (letter.status === 'Rejected' ? 'color-mix(in srgb, #EF4444 15%, transparent)' : 'color-mix(in srgb, #F59E0B 15%, transparent)'),
                      color: letter.status === 'Approved' ? '#059669' : (letter.status === 'Rejected' ? '#DC2626' : '#D97706')
                    }"
                  >
                    {{ letter.status }}
                  </span>
                </td>
                <td class="py-5 px-8 text-right">
                  <button
                    @click="openReviewModal(letter)"
                    class="inline-flex items-center space-x-1 px-4 py-2 text-[11px] font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 shadow-sm"
                    style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent); border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);"
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
        <div class="px-8 py-4 flex items-center justify-between" style="background-color: color-mix(in srgb, var(--color-nav) 40%, transparent); border-top: 1px solid var(--color-surface-border);">
          <p class="text-xs font-bold uppercase tracking-wider opacity-60" style="color: var(--color-text-primary);">
            Showing <span class="font-black opacity-100">{{ filteredLetters.length }}</span> results
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

const canReview = computed(() => hasPermission('manage_attendance'));

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
