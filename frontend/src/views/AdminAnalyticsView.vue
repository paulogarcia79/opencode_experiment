<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { fetchAnalytics } from '@/composables/useAdminApi'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Doughnut } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const range = ref<'7d' | '30d' | '90d'>('30d')
const analyticsData = ref<any>(null)
const loading = ref(true)

const growthChartData = computed(() => {
  if (!analyticsData.value) return null

  const signups = analyticsData.value.growth.signups
  const unsubscribes = analyticsData.value.growth.unsubscribes

  // Combine all unique dates and sort them
  const allDates = Array.from(new Set([
    ...signups.map((s: any) => s.date),
    ...unsubscribes.map((u: any) => u.date)
  ])).sort()

  return {
    labels: allDates,
    datasets: [
      {
        label: 'Signups',
        data: allDates.map(date => {
          const match = signups.find((s: any) => s.date === date)
          return match ? match.count : 0
        }),
        borderColor: '#10b981', // emerald-500
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Unsubscribes',
        data: allDates.map(date => {
          const match = unsubscribes.find((u: any) => u.date === date)
          return match ? match.count : 0
        }),
        borderColor: '#f43f5e', // rose-500
        backgroundColor: 'rgba(244, 63, 94, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  }
})

const engagementChartData = computed(() => {
  if (!analyticsData.value) return null

  const opens = analyticsData.value.growth.opens
  const clicks = analyticsData.value.growth.clicks

  const allDates = Array.from(new Set([
    ...opens.map((s: any) => s.date),
    ...clicks.map((u: any) => u.date)
  ])).sort()

  return {
    labels: allDates,
    datasets: [
      {
        label: 'Opens',
        data: allDates.map(date => {
          const match = opens.find((s: any) => s.date === date)
          return match ? match.count : 0
        }),
        borderColor: '#6366f1', // primary-500
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Clicks',
        data: allDates.map(date => {
          const match = clicks.find((u: any) => u.date === date)
          return match ? match.count : 0
        }),
        borderColor: '#f43f5e', // rose-500
        backgroundColor: 'rgba(244, 63, 94, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  }
})

const deliveryChartData = computed(() => {
  if (!analyticsData.value) return null

  const { sent, failed, pending } = analyticsData.value.delivery

  return {
    labels: ['Sent', 'Failed', 'Pending'],
    datasets: [
      {
        data: [sent, failed, pending],
        backgroundColor: [
          '#10b981', // emerald-500
          '#f43f5e', // rose-500
          '#6366f1', // primary-500
        ],
        borderWidth: 0,
        hoverOffset: 4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        color: '#94a3b8',
        font: { family: 'Inter' }
      }
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#64748b' }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#64748b' }
    }
  }
}

async function loadAnalytics() {
  loading.value = true
  try {
    analyticsData.value = await fetchAnalytics(range.value)
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)
watch(range, loadAnalytics)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-display font-bold text-white">Analytics</h1>
      
      <div class="flex bg-white/5 rounded-lg p-1 border border-white/10">
        <button 
          v-for="r in ['7d', '30d', '90d']" 
          :key="r"
          @click="range = r as any"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 cursor-pointer',
            range === r ? 'bg-primary-600 text-white shadow-lg shadow-primary-900/20' : 'text-slate-400 hover:text-white'
          ]"
        >
          {{ r === '7d' ? '7 Days' : r === '30d' ? '30 Days' : '90 Days' }}
        </button>
      </div>
    </div>

    <div v-if="loading && !analyticsData" class="flex items-center justify-center py-20">
      <div class="w-10 h-10 border-4 border-primary-500/20 border-t-primary-500 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="analyticsData" class="space-y-8">
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl -mr-8 -mt-8"></div>
          <p class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">Active Subscribers</p>
          <p class="text-4xl font-display font-bold text-white leading-none">
            {{ analyticsData.summary.total_active }}
          </p>
          <div class="mt-4 flex items-center text-xs text-emerald-400">
            <span class="bg-emerald-400/10 px-2 py-0.5 rounded-full">+{{ analyticsData.growth.signups.length }} this period</span>
          </div>
        </div>

        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-24 h-24 bg-primary-500/5 rounded-full blur-2xl -mr-8 -mt-8"></div>
          <p class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">Pending</p>
          <p class="text-4xl font-display font-bold text-white leading-none">
            {{ analyticsData.summary.total_pending }}
          </p>
          <p class="mt-4 text-xs text-slate-500 italic">Waiting for confirmation</p>
        </div>

        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 relative overflow-hidden group">
          <div class="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl -mr-8 -mt-8"></div>
          <p class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-2">Total Unsubscribed</p>
          <p class="text-4xl font-display font-bold text-white leading-none">
            {{ analyticsData.summary.total_unsubscribed }}
          </p>
          <div class="mt-4 flex items-center text-xs text-rose-400">
            <span class="bg-rose-400/10 px-2 py-0.5 rounded-full">{{ analyticsData.growth.unsubscribes.length }} this period</span>
          </div>
        </div>
      </div>

      <!-- Engagement Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Total Opens</p>
          <p class="text-3xl font-display font-bold text-white">{{ analyticsData.summary.total_opens }}</p>
        </div>
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Total Clicks</p>
          <p class="text-3xl font-display font-bold text-white">{{ analyticsData.summary.total_clicks }}</p>
        </div>
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">Open Rate</p>
          <p class="text-3xl font-display font-bold text-emerald-400">{{ analyticsData.summary.open_rate }}%</p>
        </div>
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6">
          <p class="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2">CTR</p>
          <p class="text-3xl font-display font-bold text-primary-400">{{ analyticsData.summary.ctr }}%</p>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 h-[400px]">
           <h3 class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-6">Audience Growth</h3>
           <div class="h-[300px]">
             <Line v-if="growthChartData" :data="growthChartData" :options="chartOptions" />
           </div>
        </div>
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 h-[400px]">
           <h3 class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-6">Engagement Trends</h3>
           <div class="h-[300px]">
             <Line v-if="engagementChartData" :data="engagementChartData" :options="chartOptions" />
           </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-surface-900 border border-white/5 rounded-2xl p-6 h-[400px]">
           <h3 class="text-sm font-medium text-slate-400 uppercase tracking-wider mb-6">Newsletter Delivery</h3>
           <div class="h-[300px]">
             <Doughnut v-if="deliveryChartData" :data="deliveryChartData" :options="{ ...chartOptions, scales: undefined }" />
           </div>
        </div>
      </div>
    </div>
  </div>
</template>
