<template>
  <div class="analytics-card">
    <div class="analytics-header">
      <h3 class="analytics-title">Attendance Overview</h3>
      <span v-if="isAtRisk" class="risk-badge">Warning: At Risk</span>
    </div>

    <div class="chart-container">
      <div class="chart-wrapper">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div class="chart-center">
          <span class="percentage">{{ attendancePercentage }}%</span>
        </div>
      </div>
      
      <div class="stats-list">
        <div class="stat-item">
          <div class="stat-dot present"></div>
          <div class="stat-info">
            <span class="stat-label">Present</span>
            <span class="stat-value">{{ presentCount }}</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-dot absent"></div>
          <div class="stat-info">
            <span class="stat-label">Absent</span>
            <span class="stat-value">{{ absentCount }}</span>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-dot excused"></div>
          <div class="stat-info">
            <span class="stat-label">Excused</span>
            <span class="stat-value">{{ excusedCount }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  presentCount: {
    type: Number,
    default: 0
  },
  absentCount: {
    type: Number,
    default: 0
  },
  excusedCount: {
    type: Number,
    default: 0
  },
  totalRequired: {
    type: Number,
    default: 0
  }
})

const attendancePercentage = computed(() => {
  const total = props.presentCount + props.absentCount + props.excusedCount
  if (total === 0) return 0
  // Excused absences usually don't count against you, but for simple display:
  const present = props.presentCount
  return Math.round((present / total) * 100)
})

const isAtRisk = computed(() => {
  // If attendance drops below 80% and there's enough data
  const total = props.presentCount + props.absentCount + props.excusedCount
  return total > 3 && attendancePercentage.value < 80
})

const chartData = computed(() => ({
  labels: ['Present', 'Absent', 'Excused'],
  datasets: [
    {
      backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
      borderWidth: 0,
      data: [props.presentCount, props.absentCount, props.excusedCount],
      cutout: '75%',
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          return ` ${context.label}: ${context.raw}`
        }
      }
    }
  }
}
</script>

<style scoped>
.analytics-card {
  background: var(--color-surface, #ffffff);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.analytics-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--color-text-primary, #111a12);
  margin: 0;
}

.risk-badge {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 4px 10px;
  border-radius: 999px;
  animation: pulse-danger 2s infinite ease-in-out;
}

@keyframes pulse-danger {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(0.98); }
}

.chart-container {
  display: flex;
  align-items: center;
  gap: 24px;
}

.chart-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.chart-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.percentage {
  font-size: 22px;
  font-weight: 800;
  color: var(--color-text-primary, #111a12);
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.stat-dot.present { background: #10b981; }
.stat-dot.absent { background: #ef4444; }
.stat-dot.excused { background: #f59e0b; }

.stat-info {
  display: flex;
  justify-content: space-between;
  flex: 1;
  font-size: 13px;
}

.stat-label {
  color: var(--color-text-muted, #536355);
  font-weight: 600;
}

.stat-value {
  color: var(--color-text-primary, #111a12);
  font-weight: 800;
}

@media (max-width: 400px) {
  .chart-container {
    flex-direction: column;
  }
}
</style>
