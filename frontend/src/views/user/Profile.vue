<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>My Profile</h2>
      <p class="text-muted">Manage your account details</p>
    </div>

    <div class="row">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Profile Information</h5>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger">{{ error }}</div>
            <div v-if="success" class="alert alert-success">{{ success }}</div>

            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="form.name" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="form.email" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="form.phone" />
              </div>
              <div class="mb-3">
                <label class="form-label">New Password (leave blank to keep current)</label>
                <input type="password" class="form-control" v-model="form.password" minlength="6" placeholder="Enter new password" />
              </div>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? 'Saving...' : 'Update Profile' }}
              </button>
            </form>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Account Info</h5>
          </div>
          <div class="card-body">
            <table class="table table-borderless">
              <tbody>
                <tr><td class="fw-bold">Role</td><td><span class="badge bg-primary">{{ user.role }}</span></td></tr>
                <tr><td class="fw-bold">Status</td><td><span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">{{ user.is_active ? 'Active' : 'Inactive' }}</span></td></tr>
                <tr><td class="fw-bold">Member Since</td><td>{{ formatDate(user.created_at) }}</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userAPI } from '../../services/api'

export default {
  name: 'UserProfile',
  data() {
    return {
      user: {},
      form: {
        name: '',
        email: '',
        phone: '',
        password: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  async mounted() {
    await this.fetchProfile()
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await userAPI.getProfile()
        this.user = response.data.user
        this.form.name = this.user.name
        this.form.email = this.user.email
        this.form.phone = this.user.phone || ''
      } catch (err) {
        console.error('Failed to load profile:', err)
      }
    },
    async updateProfile() {
      this.loading = true
      this.error = ''
      this.success = ''

      const data = {
        name: this.form.name,
        email: this.form.email,
        phone: this.form.phone
      }
      if (this.form.password) {
        data.password = this.form.password
      }

      try {
        const response = await userAPI.updateProfile(data)
        this.success = 'Profile updated successfully!'
        this.user = response.data.user
        this.form.password = ''

        // Update local storage
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}')
        storedUser.name = this.user.name
        storedUser.email = this.user.email
        localStorage.setItem('user', JSON.stringify(storedUser))
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to update profile'
      } finally {
        this.loading = false
      }
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
