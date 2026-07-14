<template>
  <div class="card trek-card h-100">
    <div class="card-header">
      <span :class="getDifficultyClass(trek.difficulty)" class="float-end">{{ trek.difficulty }}</span>
      {{ trek.name }}
    </div>
    <div class="card-body">
      <p class="mb-1"><strong>📍</strong> {{ trek.location }}</p>
      <p class="mb-1"><strong>📅</strong> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}</p>
      <p class="mb-1"><strong>⏱️</strong> {{ trek.duration_days }} days</p>
      <p class="mb-1"><strong>🎟️</strong> {{ trek.available_slots }}/{{ trek.total_slots }} slots</p>
      <p class="mb-1" v-if="trek.price"><strong>💰</strong> ₹{{ trek.price }}</p>
    </div>
    <div class="card-footer bg-white" v-if="showBookBtn">
      <button
        class="btn btn-primary w-100"
        @click="$emit('book', trek)"
        :disabled="trek.available_slots === 0"
      >
        {{ trek.available_slots > 0 ? 'Book This Trek' : 'Fully Booked' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TrekCard',
  props: {
    trek: { type: Object, required: true },
    showBookBtn: { type: Boolean, default: true }
  },
  emits: ['book'],
  methods: {
    getDifficultyClass(difficulty) {
      const classes = { Easy: 'badge badge-easy', Moderate: 'badge badge-moderate', Hard: 'badge badge-hard' }
      return classes[difficulty] || 'badge bg-secondary'
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
