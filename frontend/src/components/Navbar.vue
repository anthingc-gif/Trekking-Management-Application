<template>
  <nav class="navbar navbar-expand-lg navbar-dark navbar-custom">
    <div class="container-fluid">
      <router-link class="navbar-brand" :to="dashboardRoute">
        🏔️ TMA
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <!-- Admin Nav -->
          <template v-if="userRole === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/treks">Manage Treks</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/staff">Manage Staff</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/users">Manage Users</router-link>
            </li>
          </template>

          <!-- Staff Nav -->
          <template v-if="userRole === 'staff'">
            <li class="nav-item">
              <router-link class="nav-link" to="/staff/dashboard">Dashboard</router-link>
            </li>
          </template>

          <!-- User Nav -->
          <template v-if="userRole === 'trekker'">
            <li class="nav-item">
              <router-link class="nav-link" to="/user/dashboard">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/treks">Browse Treks</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/bookings">My Bookings</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/user/profile">Profile</router-link>
            </li>
          </template>
        </ul>

        <ul class="navbar-nav">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
              👤 {{ userName }}
              <span class="badge bg-light text-dark ms-1">{{ userRole }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><span class="dropdown-item-text text-muted">{{ userEmail }}</span></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item" href="#" @click.prevent="logout">Logout</a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavbarComponent',
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user') || '{}')
    },
    userName() {
      return this.user.name || 'User'
    },
    userEmail() {
      return this.user.email || ''
    },
    userRole() {
      return this.user.role || ''
    },
    dashboardRoute() {
      const role = this.userRole
      if (role === 'admin') return '/admin/dashboard'
      if (role === 'staff') return '/staff/dashboard'
      return '/user/dashboard'
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    }
  }
}
</script>
