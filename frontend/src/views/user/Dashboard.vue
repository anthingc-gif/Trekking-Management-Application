<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>Welcome, {{ userName }}! 🏔️</h2>
      <p class="text-muted">Your trekking dashboard</p>
    </div>

    <!-- Stats -->
    <div class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card treks">
          <h6>Available Treks</h6>
          <h2>{{ availableTreks.length }}</h2>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card bookings">
          <h6>Active Bookings</h6>
          <h2>{{ activeBookings }}</h2>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card users">
          <h6>Completed Treks</h6>
          <h2>{{ completedBookings }}</h2>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card staff">
          <h6>Notifications</h6>
          <h2>{{ unreadNotifications }}</h2>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Available Treks -->
      <div class="col-md-8 mb-4">
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Available Treks</h5>
            <router-link to="/user/treks" class="btn btn-sm btn-outline-primary">View All</router-link>
          </div>
          <div class="card-body">
            <div v-if="availableTreks.length === 0" class="text-center py-3 text-muted">
              No treks available at the moment.
            </div>
            <div v-else class="row">
              <div v-for="trek in availableTreks.slice(0, 4)" :key="trek.id" class="col-md-6 mb-3">
                <div class="card trek-card h-100">
                  <div class="card-body">
                    <h6 class="card-title">{{ trek.name }}</h6>
                    <p class="text-muted small mb-1">📍 {{ trek.location }}</p>
                    <p class="small mb-1">
                      <span :class="getDifficultyClass(trek.difficulty)">{{ trek.difficulty }}</span>
                      · {{ trek.duration_days }} days
                    </p>
                    <p class="small mb-2">🎟️ {{ trek.available_slots }} slots left</p>
                    <button
                      class="btn btn-sm btn-primary w-100"
                      @click="bookTrek(trek)"
                      :disabled="trek.available_slots === 0"
                    >
                      {{ trek.available_slots > 0 ? 'Book Now' : 'Fully Booked' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- My Bookings -->
      <div class="col-md-4 mb-4">
        <div class="card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">My Bookings</h5>
            <router-link to="/user/bookings" class="btn btn-sm btn-outline-primary">All</router-link>
          </div>
          <div class="card-body">
            <div v-if="bookings.length === 0" class="text-center py-3 text-muted">
              No bookings yet. Book your first trek!
            </div>
            <div v-for="booking in bookings.slice(0, 5)" :key="booking.id" class="mb-2 p-2 border rounded">
              <strong class="small">{{ booking.trek_name }}</strong>
              <br />
              <span class="small text-muted">{{ booking.trek_location }}</span>
              <span :class="getBookingStatusClass(booking.status)" class="float-end">
                {{ booking.status }}
              </span>
            </div>
          </div>
        </div>

        <!-- Notifications -->
        <div class="card mt-3">
          <div class="card-header bg-white">
            <h5 class="mb-0">Notifications</h5>
          </div>
          <div class="card-body" style="max-height: 300px; overflow-y: auto;">
            <div v-if="notifications.length === 0" class="text-center py-3 text-muted">
              No notifications.
            </div>
            <div v-for="n in notifications.slice(0, 5)" :key="n.id" class="mb-2 p-2 border rounded" :class="{ 'bg-light': !n.is_read }">
              <small>{{ n.message }}</small>
              <br />
              <small class="text-muted">{{ formatDate(n.created_at) }}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { trekAPI, bookingAPI, userAPI } from '../../services/api'

export default {
  name: 'UserDashboard',
  data() {
    return {
      availableTreks: [],
      bookings: [],
      notifications: []
    }
  },
  computed: {
    userName() {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.name || 'Trekker'
    },
    activeBookings() {
      return this.bookings.filter(b => b.status === 'Booked').length
    },
    completedBookings() {
      return this.bookings.filter(b => b.status === 'Completed').length
    },
    unreadNotifications() {
      return this.notifications.filter(n => !n.is_read).length
    }
  },
  async mounted() {
    await Promise.all([
      this.fetchTreks(),
      this.fetchBookings(),
      this.fetchNotifications()
    ])
  },
  methods: {
    async fetchTreks() {
      try {
        const response = await trekAPI.getOpenTreks()
        this.availableTreks = response.data.treks
      } catch (err) {
        console.error('Failed to load treks:', err)
      }
    },
    async fetchBookings() {
      try {
        const response = await bookingAPI.getMyBookings()
        this.bookings = response.data.bookings
      } catch (err) {
        console.error('Failed to load bookings:', err)
      }
    },
    async fetchNotifications() {
      try {
        const response = await userAPI.getNotifications()
        this.notifications = response.data.notifications
      } catch (err) {
        console.error('Failed to load notifications:', err)
      }
    },
    async bookTrek(trek) {
      if (!confirm(`Book "${trek.name}" at ${trek.location}?`)) return

      try {
        await bookingAPI.createBooking(trek.id)
        alert('Trek booked successfully!')
        await this.fetchTreks()
        await this.fetchBookings()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to book trek')
      }
    },
    getDifficultyClass(difficulty) {
      const classes = { Easy: 'badge badge-easy', Moderate: 'badge badge-moderate', Hard: 'badge badge-hard' }
      return classes[difficulty] || 'badge bg-secondary'
    },
    getBookingStatusClass(status) {
      const classes = { Booked: 'badge bg-success', Cancelled: 'badge bg-danger', Completed: 'badge bg-info' }
      return classes[status] || 'badge bg-secondary'
    },
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
    }
  }
}
</script>
