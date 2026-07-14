<template>
  <div class="container-fluid py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h2>Participants</h2>
        <p class="text-muted" v-if="trek">{{ trek.name }} - {{ totalParticipants }} registered</p>
      </div>
      <router-link to="/staff/dashboard" class="btn btn-outline-secondary">← Back</router-link>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="participants.length === 0" class="text-center py-4 text-muted">
          No participants registered yet.
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Booking Date</th>
                <th>Status</th>
                <th>Payment</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, index) in participants" :key="p.booking_id">
                <td>{{ index + 1 }}</td>
                <td><strong>{{ p.user_name }}</strong></td>
                <td>{{ p.user_email }}</td>
                <td>{{ p.user_phone || 'N/A' }}</td>
                <td>{{ formatDate(p.booking_date) }}</td>
                <td>
                  <span :class="getBookingStatusClass(p.status)">{{ p.status }}</span>
                </td>
                <td>
                  <span :class="getPaymentClass(p.payment_status)">{{ p.payment_status }}</span>
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
import { staffAPI } from '../../services/api'

export default {
  name: 'StaffParticipants',
  data() {
    return {
      trek: null,
      participants: [],
      totalParticipants: 0
    }
  },
  async mounted() {
    await this.fetchParticipants()
  },
  methods: {
    async fetchParticipants() {
      try {
        const trekId = this.$route.params.id
        const response = await staffAPI.getParticipants(trekId)
        this.trek = response.data.trek
        this.participants = response.data.participants
        this.totalParticipants = response.data.total_participants
      } catch (err) {
        console.error('Failed to load participants:', err)
      }
    },
    getBookingStatusClass(status) {
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
