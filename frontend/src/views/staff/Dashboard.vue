<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>Staff Dashboard</h2>
      <p class="text-muted">Manage your assigned treks</p>
    </div>

    <!-- Stats -->
    <div class="row mb-4">
      <div class="col-md-4 col-sm-6 mb-3">
        <div class="stats-card treks">
          <h6>Assigned Treks</h6>
          <h2>{{ assignedTreks.length }}</h2>
        </div>
      </div>
      <div class="col-md-4 col-sm-6 mb-3">
        <div class="stats-card bookings">
          <h6>Active Treks</h6>
          <h2>{{ activeTreks }}</h2>
        </div>
      </div>
      <div class="col-md-4 col-sm-6 mb-3">
        <div class="stats-card users">
          <h6>Total Participants</h6>
          <h2>{{ totalParticipants }}</h2>
        </div>
      </div>
    </div>

    <!-- Assigned Treks -->
    <div class="card">
      <div class="card-header bg-white">
        <h5 class="mb-0">My Assigned Treks</h5>
      </div>
      <div class="card-body">
        <div v-if="assignedTreks.length === 0" class="text-center py-4 text-muted">
          No treks assigned yet. Contact admin for assignments.
        </div>
        <div class="row">
          <div v-for="trek in assignedTreks" :key="trek.id" class="col-md-6 col-lg-4 mb-3">
            <div class="card trek-card h-100">
              <div class="card-header">
                {{ trek.name }}
              </div>
              <div class="card-body">
                <p><strong>Location:</strong> {{ trek.location }}</p>
                <p><strong>Dates:</strong> {{ formatDate(trek.start_date) }} - {{ formatDate(trek.end_date) }}</p>
                <p>
                  <strong>Status:</strong>
                  <span :class="getStatusClass(trek.status)">{{ trek.status }}</span>
                </p>
                <p><strong>Slots:</strong> {{ trek.available_slots }}/{{ trek.total_slots }}</p>
                <p><strong>Registered:</strong> {{ trek.registered_users }} participants</p>
              </div>
              <div class="card-footer bg-white">
                <div class="btn-group btn-group-sm w-100">
                  <router-link :to="`/staff/treks/${trek.id}`" class="btn btn-outline-primary">Manage</router-link>
                  <router-link :to="`/staff/treks/${trek.id}/participants`" class="btn btn-outline-info">
                    Participants
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { staffAPI } from '../../services/api'

export default {
  name: 'StaffDashboard',
  data() {
    return {
      assignedTreks: []
    }
  },
  computed: {
    activeTreks() {
      return this.assignedTreks.filter(t => t.status === 'Open' || t.status === 'Approved').length
    },
    totalParticipants() {
      return this.assignedTreks.reduce((sum, trek) => sum + (trek.registered_users || 0), 0)
    }
  },
  async mounted() {
    await this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      try {
        const response = await staffAPI.getDashboard()
        this.assignedTreks = response.data.assigned_treks
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      }
    },
    getStatusClass(status) {
      const classes = { Open: 'badge badge-open', Closed: 'badge badge-closed', Pending: 'badge badge-pending', Completed: 'badge badge-completed', Approved: 'badge bg-primary' }
      return classes[status] || 'badge bg-secondary'
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
