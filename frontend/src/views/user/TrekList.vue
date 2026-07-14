<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>Browse Treks</h2>
      <p class="text-muted">Discover and book your next adventure</p>
    </div>

    <!-- Search & Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <input type="text" class="form-control" v-model="filters.q" placeholder="Search by name or location..." @keyup.enter="searchTreks" />
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.difficulty">
              <option value="">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Moderate">Moderate</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
          <div class="col-md-2">
            <input type="number" class="form-control" v-model="filters.min_duration" placeholder="Min days" min="1" />
          </div>
          <div class="col-md-2">
            <input type="number" class="form-control" v-model="filters.max_duration" placeholder="Max days" min="1" />
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary w-100" @click="searchTreks">Search</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Trek Cards -->
    <div class="row">
      <div v-for="trek in treks" :key="trek.id" class="col-md-4 col-lg-3 mb-4">
        <div class="card trek-card h-100">
          <div class="card-header">
            <span :class="getDifficultyClass(trek.difficulty)" class="float-end">{{ trek.difficulty }}</span>
            {{ trek.name }}
          </div>
          <div class="card-body">
            <p class="mb-1"><strong>📍 Location:</strong> {{ trek.location }}</p>
            <p class="mb-1"><strong>📅 Dates:</strong> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}</p>
            <p class="mb-1"><strong>⏱️ Duration:</strong> {{ trek.duration_days }} days</p>
            <p class="mb-1"><strong>🎟️ Available:</strong> {{ trek.available_slots }}/{{ trek.total_slots }} slots</p>
            <p class="mb-1" v-if="trek.price"><strong>💰 Price:</strong> ₹{{ trek.price }}</p>
            <p class="small text-muted mt-2" v-if="trek.description">{{ trek.description.substring(0, 100) }}...</p>
          </div>
          <div class="card-footer bg-white">
            <button
              class="btn btn-primary w-100"
              @click="bookTrek(trek)"
              :disabled="trek.available_slots === 0"
            >
              {{ trek.available_slots > 0 ? 'Book This Trek' : 'Fully Booked' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="treks.length === 0" class="col-12">
        <div class="text-center py-5 text-muted">
          <h4>No treks found</h4>
          <p>Try adjusting your search filters</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { trekAPI, bookingAPI } from '../../services/api'

export default {
  name: 'TrekList',
  data() {
    return {
      treks: [],
      filters: {
        q: '',
        difficulty: '',
        min_duration: '',
        max_duration: ''
      }
    }
  },
  async mounted() {
    await this.fetchTreks()
  },
  methods: {
    async fetchTreks() {
      try {
        const response = await trekAPI.getOpenTreks()
        this.treks = response.data.treks
      } catch (err) {
        console.error('Failed to load treks:', err)
      }
    },
    async searchTreks() {
      try {
        const params = {}
        if (this.filters.q) params.q = this.filters.q
        if (this.filters.difficulty) params.difficulty = this.filters.difficulty
        if (this.filters.min_duration) params.min_duration = this.filters.min_duration
        if (this.filters.max_duration) params.max_duration = this.filters.max_duration

        const response = await trekAPI.searchTreks(params)
        this.treks = response.data.treks
      } catch (err) {
        console.error('Search failed:', err)
      }
    },
    async bookTrek(trek) {
      if (!confirm(`Book "${trek.name}" at ${trek.location} for ₹${trek.price || 0}?`)) return

      try {
        await bookingAPI.createBooking(trek.id)
        alert('Trek booked successfully! 🎉')
        await this.fetchTreks()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to book trek')
      }
    },
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
