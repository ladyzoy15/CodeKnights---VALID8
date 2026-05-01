<template>
  <section class="sg-sub-page">
    <header class="sg-sub-header dashboard-enter dashboard-enter--1">
      <h1 class="sg-sub-title">My Excuse Letters</h1>
      <button
        @click="loadLetters"
        class="sg-sub-action"
        style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);"
        :disabled="loading"
      >
        <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
        <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>
    </header>

    <div class="flex-1 overflow-hidden py-4 flex flex-col">
      <div class="flex-1 rounded-[2rem] shadow-sm overflow-hidden flex flex-col" style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
        <div class="overflow-x-auto flex-1 custom-scrollbar">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-[11px] font-black uppercase tracking-widest sticky top-0 z-10 shadow-sm backdrop-blur-md" style="background-color: color-mix(in srgb, var(--color-nav) 90%, transparent); color: var(--color-nav-text); border-bottom: 1px solid var(--color-surface-border);">
                <th class="py-5 px-8">Event Name</th>
                <th class="py-5 px-8">Submitted On</th>
                <th class="py-5 px-8">Status</th>
                <th class="py-5 px-8">Remarks</th>
              </tr>
            </thead>
            <tbody style="border-top: 1px solid var(--color-surface-border);">
              <tr v-if="loading" class="animate-pulse">
                <td colspan="4" class="py-16 text-center font-bold text-sm" style="color: var(--color-text-muted);">Fetching your letters...</td>
              </tr>
              <tr v-else-if="letters.length === 0">
                <td colspan="4" class="py-24">
                  <div class="flex flex-col items-center justify-center text-center">
                    <div class="w-20 h-20 rounded-[2rem] flex items-center justify-center mb-5 shadow-inner" style="background-color: var(--color-nav);">
                      <svg class="w-10 h-10 opacity-30" style="color: var(--color-text-primary);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"></path></svg>
                    </div>
                    <h3 class="text-xl font-extrabold tracking-tight mb-2" style="color: var(--color-primary);">No Excuse Letters</h3>
                    <p class="text-sm px-8 font-medium leading-relaxed opacity-70" style="color: var(--color-text-primary);">
                      You haven't submitted any excuse letters yet.
                    </p>
                  </div>
                </td>
              </tr>
              <tr
                v-else
                v-for="letter in sortedLetters"
                :key="letter.id"
                class="transition-colors group hover:bg-gray-50/50 dark:hover:bg-gray-800/20" style="border-bottom: 1px solid var(--color-surface-border);"
              >
                <td class="py-5 px-8">
                  <div class="flex flex-col relative">
                    <!-- Status Left Line Indicator -->
                    <div class="absolute -left-8 top-1/2 -translate-y-1/2 w-1.5 h-full max-h-8 rounded-r-lg opacity-0 group-hover:opacity-100 transition-opacity"
                         :style="{
                           backgroundColor: letter.status === 'Approved' ? '#10B981' : (letter.status === 'Rejected' ? '#EF4444' : '#F59E0B')
                         }">
                    </div>
                    <span class="text-sm font-bold leading-tight mb-1.5" style="color: var(--color-primary);">{{ letter.eventName || 'Event Name' }}</span>
                    <span v-if="letter.attachmentUrl" class="inline-flex items-center text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-lg w-fit" 
                          style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 12%, transparent);">
                      <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                      Document Attached
                    </span>
                  </div>
                </td>
                <td class="py-5 px-8 text-sm font-medium opacity-70" style="color: var(--color-text-primary);">
                  {{ formatDate(letter.submittedAt) }}
                </td>
                <td class="py-5 px-8">
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
                <td class="py-5 px-8">
                  <p class="text-sm font-medium max-w-xs truncate" :title="letter.reviewerRemarks || 'N/A'" style="color: var(--color-text-primary);">
                    {{ letter.reviewerRemarks || '-' }}
                  </p>
                  <p v-if="letter.status !== 'Pending' && letter.reviewedBy" class="text-[10px] font-bold uppercase tracking-wider mt-1 opacity-50" style="color: var(--color-text-primary);">
                    Officer #{{ letter.reviewedBy }}
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
