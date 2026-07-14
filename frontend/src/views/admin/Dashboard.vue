<template>
  <div class="container-fluid py-4">
    <div class="page-header">
      <h2>Admin Dashboard</h2>
      <p class="text-muted">Overview of trekking operations</p>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card treks">
          <h6>Total Treks</h6>
          <h2>{{ stats.total_treks }}</h2>
          <small>{{ stats.active_treks }} active</small>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card users">
          <h6>Total Users</h6>
          <h2>{{ stats.total_users }}</h2>
          <small>Registered trekkers</small>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card staff">
          <h6>Total Staff</h6>
          <h2>{{ stats.total_staff }}</h2>
          <small>Trek coordinators</small>
        </div>
      </div>
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="stats-card bookings">
          <h6>Total Bookings</h6>
          <h2>{{ stats.total_bookings }}</h2>
          <small>All time</small>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Search</h5>
            <div class="row g-3">
              <div class="col-md-8">
                <input
                  type="text"
                  class="form-control"
                  v-model="searchQuery"
                  placeholder="Search users, staff, or treks..."
                  @keyup.enter="handleSearch"
                />
              </div>
              <div class="col-md-2">
                <select class="form-select" v-model="searchType">
                  <option value="all">All</option>
                  <option value="users">Users</option>
                  <option value="staff">Staff</option>
                  <option value="treks">Treks</option>
                </select>
              </div>
              <div class="col-md-2">
                <button class="btn btn-primary w-100" @click="handleSearch">Search</button>
              </div>
            </div>

            <!-- Search Results -->
            <div v-if="searchResults" class="mt-3">
              <div v-if="searchResults.users && searchResults.users.length" class="mb-3">
                <h6>Users ({{ searchResults.users.length }})</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead><tr><th>Name</th><th>Email</th><th>Status</th></tr></thead>
                    <tbody>
                      <tr v-for="user in searchResults.users" :key="user.id">
                        <td>{{ user.name }}</td>
                        <td>{{ user.email }}</td>
                        <td>
                          <span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">
                            {{ user.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-if="searchResults.staff && searchResults.staff.length" class="mb-3">
                <h6>Staff ({{ searchResults.staff.length }})</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead><tr><th>Name</th><th>Email</th><th>Status</th></tr></thead>
                    <tbody>
                      <tr v-for="s in searchResults.staff" :key="s.id">
                        <td>{{ s.name }}</td>
                        <td>{{ s.email }}</td>
                        <td>
                          <span :class="s.is_active ? 'badge bg-success' : 'badge bg-danger'">
                            {{ s.is_active ? 'Active' : 'Inactive' }}
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-if="searchResults.treks && searchResults.treks.length">
                <h6>Treks ({{ searchResults.treks.length }})</h6>
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead><tr><th>Name</th><th>Location</th><th>Status</th></tr></thead>
                    <tbody>
                      <tr v-for="trek in searchResults.treks" :key="trek.id">
                        <td>{{ trek.name }}</td>
                        <td>{{ trek.location }}</td>
                        <td><span class="badge bg-info">{{ trek.status }}</span></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-if="!searchResults.users?.length && !searchResults.staff?.length && !searchResults.treks?.length">
                <p class="text-muted">No results found.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row">
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5>🗻 Manage Treks</h5>
            <p class="text-muted">Create and manage trekking routes</p>
            <router-link to="/admin/treks" class="btn btn-outline-primary">Go to Treks</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5>👥 Manage Staff</h5>
            <p class="text-muted">Add and manage trek staff</p>
            <router-link to="/admin/staff" class="btn btn-outline-primary">Go to Staff</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body text-center">
            <h5>🧑‍🤝‍🧑 Manage Users</h5>
            <p class="text-muted">View and manage trekkers</p>
            <router-link to="/admin/users" class="btn btn-outline-primary">Go to Users</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        total_treks: 0,
        total_users: 0,
        total_staff: 0,
        total_bookings: 0,
        active_treks: 0,
        completed_treks: 0
      },
      searchQuery: '',
      searchType: 'all',
      searchResults: null
    }
  },
  async mounted() {
    await this.fetchDashboard()
  },
  methods: {
    async fetchDashboard() {
      try {
        const response = await adminAPI.getDashboard()
        this.stats = response.data
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      }
    },
    async handleSearch() {
      if (!this.searchQuery.trim()) return

      try {
        const response = await adminAPI.search(this.searchQuery, this.searchType)
        this.searchResults = response.data
      } catch (err) {
        console.error('Search failed:', err)
      }
    }
  }
}
</script>
