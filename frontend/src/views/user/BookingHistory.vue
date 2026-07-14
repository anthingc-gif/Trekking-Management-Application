<template>
  <div class="container-fluid py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h2>My Bookings</h2>
        <p class="text-muted">View your booking history and trek status</p>
      </div>
      <button class="btn btn-outline-primary" @click="exportHistory" :disabled="exporting">
        {{ exporting ? 'Exporting...' : '📥 Export CSV' }}
      </button>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="bookings.length === 0" class="text-center py-5 text-muted">
          <h4>No bookings yet</h4>
          <p>Start by browsing available treks!</p>
          <router-link to="/user/treks" class="btn btn-primary">Browse Treks</router-link>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Booking Date</th>
                <th>Status</th>
                <th>Payment</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in bookings" :key="booking.id">
                <td><strong>{{ booking.trek_name }}</strong></td>
                <td>{{ booking.trek_location }}</td>
                <td>{{ formatDate(booking.booking_date) }}</td>
                <td>
                  <span :class="getStatusClass(booking.status)">{{ booking.status }}</span>
                </td>
                <td>
                  <span :class="getPaymentClass(booking.payment_status)">{{ booking.payment_status }}</span>
                </td>
                <td>
                  <button
                    v-if="booking.status === 'Booked'"
                    class="btn btn-sm btn-outline-danger"
                    @click="cancelBooking(booking)"
                  >
                    Cancel
                  </button>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { bookingAPI, userAPI } from '../../services/api'

export default {
  name: 'BookingHistory',
  data() {
    return {
      bookings: [],
      exporting: false
    }
  },
  async mounted() {
    await this.fetchBookings()
  },
  methods: {
    async fetchBookings() {
      try {
        const response = await bookingAPI.getMyBookings()
        this.bookings = response.data.bookings
      } catch (err) {
        console.error('Failed to load bookings:', err)
      }
    },
    async cancelBooking(booking) {
      if (!confirm(`Cancel your booking for "${booking.trek_name}"?`)) return

      try {
        await bookingAPI.cancelBooking(booking.id)
        alert('Booking cancelled successfully.')
        await this.fetchBookings()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to cancel booking')
      }
    },
    async exportHistory() {
      this.exporting = true
      try {
        const response = await userAPI.triggerExport()
        alert(response.data.message || 'Export initiated!')
      } catch (err) {
        alert('Failed to export. Please try again.')
      } finally {
        this.exporting = false
      }
    },
    getStatusClass(status) {
      const classes = { Booked: 'badge bg-success', Cancelled: 'badge bg-danger', Completed: 'badge bg-info' }
      return classes[status] || 'badge bg-secondary'
    },
    getPaymentClass(status) {
      const classes = { Paid: 'badge bg-success', Pending: 'badge bg-warning text-dark', Refunded: 'badge bg-secondary' }
      return classes[status] || 'badge bg-light text-dark'
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
