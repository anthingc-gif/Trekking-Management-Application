<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>Manage Users</h2>
      <p class="text-muted">View and manage registered trekkers</p>
    </div>

    <!-- Users Table -->
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
                <th>Registered</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td><strong>{{ user.name }}</strong></td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone || 'N/A' }}</td>
                <td>
                  <span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <span :class="user.is_blacklisted ? 'badge bg-danger' : 'badge bg-light text-dark'">
                    {{ user.is_blacklisted ? 'Yes' : 'No' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button
                      :class="user.is_active ? 'btn btn-outline-warning' : 'btn btn-outline-success'"
                      @click="toggleActive(user)"
                    >
                      {{ user.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button
                      :class="user.is_blacklisted ? 'btn btn-outline-success' : 'btn btn-outline-danger'"
                      @click="toggleBlacklist(user)"
                    >
                      {{ user.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="users.length === 0">
                <td colspan="7" class="text-center text-muted py-4">No users found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'

export default {
  name: 'ManageUsers',
  data() {
    return {
      users: []
    }
  },
  async mounted() {
    await this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      try {
        const response = await adminAPI.getAllUsers()
        this.users = response.data.users
      } catch (err) {
        console.error('Failed to load users:', err)
      }
    },
    async toggleActive(user) {
      try {
        await adminAPI.toggleDeactivate(user.id)
        await this.fetchUsers()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update status')
      }
    },
    async toggleBlacklist(user) {
      try {
        await adminAPI.toggleBlacklist(user.id)
        await this.fetchUsers()
      } catch (err) {
        alert(err.response?.data?.error || 'Failed to update blacklist status')
      }
    },
    formatDate(date) {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    }
  }
}
</script>
