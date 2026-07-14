<template>
  <div class="container-fluid py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h2>Manage Treks</h2>
        <p class="text-muted">Create and manage trekking routes</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">+ Create Trek</button>
    </div>

    <!-- Treks Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Duration</th>
                <th>Slots</th>
                <th>Status</th>
                <th>Staff</th>
                <th>Start Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trek in treks" :key="trek.id">
                <td><strong>{{ trek.name }}</strong></td>
                <td>{{ trek.location }}</td>
                <td>
                  <span :class="getDifficultyClass(trek.difficulty)">
                    {{ trek.difficulty }}
                  </span>
                </td>
                <td>{{ trek.duration_days }} days</td>
                <td>{{ trek.available_slots }}/{{ trek.total_slots }}</td>
                <td>
                  <span :class="getStatusClass(trek.status)">{{ trek.status }}</span>
                </td>
                <td>{{ trek.assigned_staff_name || 'Unassigned' }}</td>
                <td>{{ formatDate(trek.start_date) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editTrek(trek)">Edit</button>
                    <button class="btn btn-outline-info" @click="openAssignModal(trek)">Assign</button>
                    <button class="btn btn-outline-danger" @click="deleteTrek(trek.id)">Delete</button>
                  </div>
                </td>
              </tr>
              <tr v-if="treks.length === 0">
                <td colspan="9" class="text-center text-muted py-4">No treks found. Create your first trek!</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Trek Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ showEditModal ? 'Edit Trek' : 'Create New Trek' }}</h5>
            <button type="button" class="btn-close" @click="closeModals"></button>
          </div>
          <form @submit.prevent="showEditModal ? updateTrek() : createTrek()">
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Trek Name *</label>
                  <input type="text" class="form-control" v-model="trekForm.name" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Location *</label>
                  <input type="text" class="form-control" v-model="trekForm.location" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Difficulty *</label>
                  <select class="form-select" v-model="trekForm.difficulty" required>
                    <option value="Easy">Easy</option>
                    <option value="Moderate">Moderate</option>
                    <option value="Hard">Hard</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Duration (days) *</label>
                  <input type="number" class="form-control" v-model="trekForm.duration_days" min="1" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Total Slots *</label>
                  <input type="number" class="form-control" v-model="trekForm.total_slots" min="1" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Start Date *</label>
                  <input type="date" class="form-control" v-model="trekForm.start_date" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">End Date *</label>
                  <input type="date" class="form-control" v-model="trekForm.end_date" required />
                </div>
                <div class="col-md-4">
                  <label class="form-label">Price (₹)</label>
                  <input type="number" class="form-control" v-model="trekForm.price" min="0" step="0.01" />
                </div>
                <div class="col-md-6">
                  <label class="form-label">Status</label>
                  <select class="form-select" v-model="trekForm.status">
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Open">Open</option>
                    <option value="Closed">Closed</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Description</label>
                  <textarea class="form-control" v-model="trekForm.description" rows="3"></textarea>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModals">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ showEditModal ? 'Update Trek' : 'Create Trek' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Assign Staff Modal -->
    <div v-if="showAssignModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Assign Staff to "{{ selectedTrek?.name }}"</h5>
            <button type="button" class="btn-close" @click="showAssignModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Select Staff Member</label>
              <select class="form-select" v-model="selectedStaffId">
                <option value="">-- Select Staff --</option>
                <option v-for="staff in staffList" :key="staff.id" :value="staff.id">
                  {{ staff.name }} ({{ staff.email }})
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showAssignModal = false">Cancel</button>
            <button class="btn btn-primary" @click="assignStaff" :disabled="!selectedStaffId">Assign</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'

export default {
  name: 'ManageTreks',
  data() {
    return {
      treks: [],
      staffList: [],
      loading: false,
      formError: '',
      showCreateModal: false,
      showEditModal: false,
      showAssignModal: false,
      selectedTrek: null,
      selectedStaffId: '',
      editingTrekId: null,
      trekForm: {
        name: '',
        location: '',
        difficulty: 'Moderate',
        duration_days: 1,
        total_slots: 10,
        start_date: '',
        end_date: '',
        price: 0,
        status: 'Pending',
        description: ''
      }
    }
  },
  async mounted() {
    await this.fetchTreks()
    await this.fetchStaff()
  },
  methods: {
    async fetchTreks() {
      try {
        const response = await adminAPI.getAllTreks()
        this.treks = response.data.treks
      } catch (err) {
        console.error('Failed to load treks:', err)
      }
    },
    async fetchStaff() {
      try {
        const response = await adminAPI.getAllStaff()
        this.staffList = response.data.staff.filter(s => s.is_active)
      } catch (err) {
        console.error('Failed to load staff:', err)
      }
    },
    async createTrek() {
      this.loading = true
      this.formError = ''

      try {
        await adminAPI.createTrek(this.trekForm)
        await this.fetchTreks()
        this.closeModals()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to create trek'
      } finally {
        this.loading = false
      }
    },
    editTrek(trek) {
      this.editingTrekId = trek.id
      this.trekForm = {
        name: trek.name,
        location: trek.location,
        difficulty: trek.difficulty,
        duration_days: trek.duration_days,
        total_slots: trek.total_slots,
        start_date: trek.start_date,
        end_date: trek.end_date,
        price: trek.price,
        status: trek.status,
        description: trek.description || ''
      }
      this.showEditModal = true
    },
    async updateTrek() {
      this.loading = true
      this.formError = ''

      try {
        await adminAPI.updateTrek(this.editingTrekId, this.trekForm)
        await this.fetchTreks()
        this.closeModals()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to update trek'
      } finally {
        this.loading = false
      }
    },
    async deleteTrek(trekId) {
      if (!confirm('Are you sure you want to delete this trek?')) return

      try {
        await adminAPI.deleteTrek(trekId)
        await this.fetchTreks()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to delete trek')
      }
    },
    openAssignModal(trek) {
      this.selectedTrek = trek
      this.selectedStaffId = trek.assigned_staff_id || ''
      this.showAssignModal = true
    },
    async assignStaff() {
      try {
        await adminAPI.assignStaff(this.selectedTrek.id, this.selectedStaffId)
        await this.fetchTreks()
        this.showAssignModal = false
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to assign staff')
      }
    },
    closeModals() {
      this.showCreateModal = false
      this.showEditModal = false
      this.formError = ''
      this.editingTrekId = null
      this.trekForm = {
        name: '', location: '', difficulty: 'Moderate', duration_days: 1,
        total_slots: 10, start_date: '', end_date: '', price: 0, status: 'Pending', description: ''
      }
    },
    getDifficultyClass(difficulty) {
      const classes = { Easy: 'badge badge-easy', Moderate: 'badge badge-moderate', Hard: 'badge badge-hard' }
      return classes[difficulty] || 'badge bg-secondary'
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
