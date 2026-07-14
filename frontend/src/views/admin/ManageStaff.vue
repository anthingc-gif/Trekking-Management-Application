<template>
  <div class="container-fluid py-4">
    <div class="page-header d-flex justify-content-between align-items-center">
      <div>
        <h2>Manage Staff</h2>
        <p class="text-muted">Add and manage trek staff members</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">+ Add Staff</button>
    </div>

    <!-- Staff Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Blacklisted</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="staff in staffList" :key="staff.id">
                <td><strong>{{ staff.name }}</strong></td>
                <td>{{ staff.email }}</td>
                <td>{{ staff.phone || 'N/A' }}</td>
                <td>
                  <span :class="staff.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ staff.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span :class="staff.is_blacklisted ? 'badge bg-danger' : 'badge bg-light text-dark'">
                    {{ staff.is_blacklisted ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td>{{ formatDate(staff.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editStaff(staff)">Edit</button>
                    <button
                      :class="staff.is_active ? 'btn btn-outline-warning' : 'btn btn-outline-success'"
                      @click="toggleActive(staff)"
                    >
                      {{ staff.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button
                      :class="staff.is_blacklisted ? 'btn btn-outline-success' : 'btn btn-outline-danger'"
                      @click="toggleBlacklist(staff)"
                    >
                      {{ staff.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="staffList.length === 0">
                <td colspan="7" class="text-center text-muted py-4">No staff members found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Staff Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ showEditModal ? 'Edit Staff' : 'Add New Staff' }}</h5>
            <button type="button" class="btn-close" @click="closeModals"></button>
          </div>
          <form @submit.prevent="showEditModal ? updateStaff() : createStaff()">
            <div class="modal-body">
              <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
              <div class="mb-3">
                <label class="form-label">Full Name *</label>
                <input type="text" class="form-control" v-model="staffForm.name" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input type="email" class="form-control" v-model="staffForm.email" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="staffForm.phone" />
              </div>
              <div class="mb-3">
                <label class="form-label">{{ showEditModal ? 'New Password (leave blank to keep)' : 'Password *' }}</label>
                <input type="password" class="form-control" v-model="staffForm.password" :required="!showEditModal" minlength="6" />
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModals">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ showEditModal ? 'Update Staff' : 'Add Staff' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'

export default {
  name: 'ManageStaff',
  data() {
    return {
      staffList: [],
      loading: false,
      formError: '',
      showCreateModal: false,
      showEditModal: false,
      editingStaffId: null,
      staffForm: {
        name: '',
        email: '',
        phone: '',
        password: ''
      }
    }
  },
  async mounted() {
    await this.fetchStaff()
  },
  methods: {
    async fetchStaff() {
      try {
        const response = await adminAPI.getAllStaff()
        this.staffList = response.data.staff
      } catch (err) {
        console.error('Failed to load staff:', err)
      }
    },
    async createStaff() {
      this.loading = true
      this.formError = ''

      try {
        await adminAPI.createStaff(this.staffForm)
        await this.fetchStaff()
        this.closeModals()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to create staff'
      } finally {
        this.loading = false
      }
    },
    editStaff(staff) {
      this.editingStaffId = staff.id
      this.staffForm = {
        name: staff.name,
        email: staff.email,
        phone: staff.phone || '',
        password: ''
      }
      this.showEditModal = true
    },
    async updateStaff() {
      this.loading = true
      this.formError = ''

      const data = { ...this.staffForm }
      if (!data.password) delete data.password

      try {
        await adminAPI.updateStaff(this.editingStaffId, data)
        await this.fetchStaff()
        this.closeModals()
      } catch (err) {
        this.formError = err.response?.data?.error || 'Failed to update staff'
      } finally {
        this.loading = false
      }
    },
    async toggleActive(staff) {
      try {
        await adminAPI.toggleDeactivate(staff.id)
        await this.fetchStaff()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update status')
      }
    },
    async toggleBlacklist(staff) {
      try {
        await adminAPI.toggleBlacklist(staff.id)
        await this.fetchStaff()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update blacklist status')
      }
    },
    closeModals() {
      this.showCreateModal = false
      this.showEditModal = false
      this.formError = ''
      this.editingStaffId = null
      this.staffForm = { name: '', email: '', phone: '', password: '' }
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
