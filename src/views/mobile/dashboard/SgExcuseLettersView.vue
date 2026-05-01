<template>
  <div class="min-h-screen pb-20" style="background-color: var(--color-bg);">
    <!-- Header -->
    <div class="sticky top-0 z-20 px-5 py-5 shadow-sm backdrop-blur-xl" style="background-color: color-mix(in srgb, var(--color-surface) 85%, transparent); border-bottom: 1px solid var(--color-surface-border);">
      <div class="flex items-center justify-between">
        <h1 class="text-2xl font-black tracking-tight" style="color: var(--color-primary);">Review Letters</h1>
        <button
          @click="loadLetters"
          class="p-2.5 rounded-full transition-transform active:scale-90" style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);"
          :class="{ 'animate-spin': loading }"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
      </div>
      <p class="text-xs font-bold mt-1.5 opacity-60 uppercase tracking-wider" style="color: var(--color-text-primary);">Manage excuse letters from students</p>
    </div>

    <!-- Content -->
    <div class="p-5 space-y-5">
      <!-- Loading State -->
      <div v-if="loading && letters.length === 0" class="flex flex-col items-center justify-center py-24">
        <div class="w-14 h-14 border-4 rounded-full animate-spin mb-5" style="border-color: color-mix(in srgb, var(--color-primary) 20%, transparent); border-top-color: var(--color-primary);"></div>
        <p class="font-bold text-sm" style="color: var(--color-text-muted);">Fetching letters...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="letters.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
        <div class="w-24 h-24 rounded-[2rem] flex items-center justify-center mb-6 shadow-inner" style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
          <svg class="w-10 h-10 opacity-30" style="color: var(--color-text-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
        </div>
        <h3 class="text-xl font-extrabold tracking-tight mb-2" style="color: var(--color-primary);">No letters found</h3>
        <p class="text-sm px-8 font-medium leading-relaxed opacity-70" style="color: var(--color-text-primary);">There are no excuse letters to review at the moment.</p>
      </div>

      <!-- Letters List -->
      <div v-else v-for="letter in sortedLetters" :key="letter.id" @click="selectLetter(letter)" 
           class="relative overflow-hidden rounded-3xl p-5 shadow-sm active:scale-[0.98] transition-all hover:shadow-md cursor-pointer" 
           style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
        
        <!-- Status Left Border -->
        <div class="absolute left-0 top-0 bottom-0 w-1.5"
             :style="{
               backgroundColor: letter.status === 'Approved' ? '#10B981' : (letter.status === 'Rejected' ? '#EF4444' : '#F59E0B')
             }">
        </div>

        <div class="pl-2">
          <!-- Top Row -->
          <div class="flex justify-between items-start mb-4 gap-3">
            <div class="flex-1 min-w-0">
              <h4 class="font-bold text-base leading-tight truncate mb-1.5" style="color: var(--color-primary);">{{ letter.eventName || 'Event Name' }}</h4>
              <div class="flex items-center">
                <span class="text-[10px] px-2 py-1 rounded-lg font-black uppercase tracking-wider mr-2" style="color: var(--color-text-primary); background-color: color-mix(in srgb, var(--color-surface-border) 40%, transparent);">STU-{{ letter.studentId }}</span>
                <span class="text-[11px] font-bold opacity-50 uppercase tracking-wide truncate" style="color: var(--color-text-primary);">{{ formatDate(letter.submittedAt) }}</span>
              </div>
            </div>
            <span
              class="px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-sm"
              :style="{
                backgroundColor: letter.status === 'Approved' ? 'color-mix(in srgb, #10B981 15%, transparent)' : (letter.status === 'Rejected' ? 'color-mix(in srgb, #EF4444 15%, transparent)' : 'color-mix(in srgb, #F59E0B 15%, transparent)'),
                color: letter.status === 'Approved' ? '#059669' : (letter.status === 'Rejected' ? '#DC2626' : '#D97706')
              }"
            >
              {{ letter.status }}
            </span>
          </div>

          <!-- Reason -->
          <p class="text-sm font-medium leading-relaxed line-clamp-2 p-3 rounded-2xl mb-4 italic" 
             style="color: var(--color-text-primary); background-color: color-mix(in srgb, var(--color-nav) 40%, transparent); border: 1px solid color-mix(in srgb, var(--color-surface-border) 50%, transparent);">
            "{{ letter.reason }}"
          </p>

          <!-- Bottom Row: Attachment & Review Action -->
          <div class="flex items-center justify-between">
            <div v-if="letter.attachmentUrl" class="inline-flex items-center text-[11px] font-extrabold uppercase tracking-wide px-3 py-2 rounded-xl" style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);">
              <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
              Attachment
            </div>
            <div v-else></div>
            
            <button v-if="letter.status === 'Pending' && canReview" class="text-[11px] font-black uppercase tracking-wider flex items-center px-4 py-2 rounded-xl transition-all active:scale-95" 
                    style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent); border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);">
              Review Request
              <svg class="w-3.5 h-3.5 ml-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7"></path></svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Modal (Overlay) -->
    <ExcuseLetterReviewModal
      v-model="isModalOpen"
      :letter="selectedLetter"
      :can-review="canReview"
      @reviewed="handleReviewed"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useExcuseLetters } from '@/composables/useExcuseLetters';
import { useSgDashboard } from '@/composables/useSgDashboard';
import ExcuseLetterReviewModal from '@/components/desktop/events/ExcuseLetterReviewModal.vue';

const { fetchGovernanceLetters, loading, letters } = useExcuseLetters();
const { activeUnitId, hasPermission } = useSgDashboard();

const selectedLetter = ref(null);
const isModalOpen = ref(false);

const canReview = computed(() => hasPermission('manage_attendance') || true); // Default true for mock

const loadLetters = async () => {
  if (activeUnitId.value) {
    await fetchGovernanceLetters(activeUnitId.value);
  } else {
    // Fallback for mock environment
    await fetchGovernanceLetters(1);
  }
};

onMounted(() => {
  loadLetters();
});

const sortedLetters = computed(() => {
  return [...letters.value].sort((a, b) => {
    // Show Pending first, then sort by date
    if (a.status === 'Pending' && b.status !== 'Pending') return -1;
    if (a.status !== 'Pending' && b.status === 'Pending') return 1;
    return new Date(b.submittedAt) - new Date(a.submittedAt);
  });
});

const selectLetter = (letter) => {
  selectedLetter.value = letter;
  isModalOpen.value = true;
};

const handleReviewed = () => {
  loadLetters();
};

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
