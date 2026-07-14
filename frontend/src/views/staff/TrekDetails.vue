<template>
  <div class="container-fluid py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h2>Trek Management</h2>
        <p class="text-muted" v-if="trek">{{ trek.name }} - {{ trek.location }}</p>
      </div>
      <router-link to="/staff/dashboard" class="btn btn-outline-secondary">← Back</router-link>
    </div>

    <div v-if="trek" class="row">
      <!-- Trek Info -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">Trek Details</h5>
          </div>
          <div class="card-body">
            <table class="table table-borderless">
              <tbody>
                <tr><td class="fw-bold">Name</td><td>{{ trek.name }}</td></tr>
                <tr><td class="fw-bold">Location</td><td>{{ trek.location }}</td></tr>
                <tr><td class="fw-bold">Difficulty</td><td><span :class="getDifficultyClass(trek.difficulty)">{{ trek.difficulty }}</span></td></tr>
                <tr><td class="fw-bold">Duration</td><td>{{ trek.duration_days }} days</td></tr>
                <tr><td class="fw-bold">Dates</td><td>{{ trek.start_date }} to {{ trek.end_date }}</td></tr>
                <tr><td class="fw-bold">Slots</td><td>{{ trek.available_slots }} / {{ trek.total_slots }}</td></tr>
                <tr><td class="fw-bold">Status</td><td><span :class="getStatusClass(trek.status)">{{ trek.status }}</span></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Update Trek -->
      <div class="col-md-6 mb-4">
        <div class="card h-100">
          <div class="card-header bg-white">
            <h5 class="mb-0">Update Trek</h5>
          </div>
          <div class="card-body">
            <div v-if="updateError" class="alert alert-danger">{{ updateError }}</div>
            <div v-if="updateSuccess" class="alert alert-success">{{ updateSuccess }}</div>

            <form @submit.prevent="updateTrek">
              <div class="mb-3">
                <label class="form-label">Available Slots</label>
                <input type="number" class="form-control" v-model="updateForm.available_slots" :max="trek.total_slots" min="0" />
              </div>
              <div class="mb-3">
                <label class="form-label">Trek Status</label>
                <select class="form-select" v-model="updateForm.status">
                  <option value="Open">Open</option>
                  <option value="Closed">Closed</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Updating...' : 'Update Trek' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-5">
      <div class="spinner-border" role="status"></div>
      <p class="text-muted mt-2">Loading trek details...</p>
    </div>
  </div>
</template>

<script>
import { staffAPI } from '../../services/api'

export default {
  name: 'StaffTrekDetails',
  data() {
    return {
      trek: null,
      loading: false,
      updateError: '',
      updateSuccess: '',
      updateForm: {
        available_slots: 0,
        status: ''
      }
    }
  },
  async mounted() {
    await this.fetchTrek()
  },
  methods: {
    async fetchTrek() {
      try {
        const trekId = this.$route.params.id
        const response = await staffAPI.getAssignedTreks()
        this.trek = response.data.treks.find(t => t.id === parseInt(trekId))

        if (this.trek) {
          this.updateForm.available_slots = this.trek.available_slots
          this.updateForm.status = this.trek.status
        }
      } catch (err) {
        console.error('Failed to load trek:', err)
      }
    },
    async updateTrek() {
      this.loading = true
      this.updateError = ''
      this.updateSuccess = ''

      try {
        await staffAPI.updateTrek(this.trek.id, this.updateForm)
        this.updateSuccess = 'Trek updated successfully!'
        await this.fetchTrek()
      } catch (err) {
        this.updateError = err.response?.data?.error || 'Failed to update trek'
      } finally {
        this.loading = false
      }
    },
    getDifficultyClass(difficulty) {
      const classes = { Easy: 'badge badge-easy', Moderate: 'badge badge-moderate', Hard: 'badge badge-hard' }
      return classes[difficulty] || 'badge bg-secondary'
    },
    getStatusClass(status) {
      const classes = { Open: 'badge badge-open', Closed: 'badge badge-closed', Pending: 'badge badge-pending', Completed: 'badge badge-completed' }
      return classes[status] || 'badge bg-secondary'
    }
  }
}
</script>
