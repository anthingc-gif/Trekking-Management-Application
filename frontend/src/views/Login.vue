<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="text-center mb-4">
        <h2>🏔️ TMA</h2>
        <p class="text-muted">Trekking Management Application</p>
      </div>

      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="email" class="form-label">Email address</label>
          <input
            type="email"
            class="form-control"
            id="email"
            v-model="form.email"
            placeholder="Enter your email"
            required
          />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="form.password"
            placeholder="Enter your password"
            required
            minlength="6"
          />
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <div class="text-center mt-3">
        <p class="text-muted">
          Don't have an account?
          <router-link to="/register" class="text-decoration-none">Register here</router-link>
        </p>
      </div>

      <div class="text-center mt-2">
        <small class="text-muted">
          Admin: admin@tma.com / admin123
        </small>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../services/api'

export default {
  name: 'LoginPage',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''

      try {
        const response = await authAPI.login(this.form)
        const { token, user } = response.data

        // Store token and user info
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        // Redirect based on role
        if (user.role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (user.role === 'staff') {
          this.$router.push('/staff/dashboard')
        } else {
          this.$router.push('/user/dashboard')
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
