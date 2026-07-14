<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="text-center mb-4">
        <h2>🏔️ Register</h2>
        <p class="text-muted">Join the Trekking Community</p>
      </div>

      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <div v-if="success" class="alert alert-success">
        {{ success }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="name" class="form-label">Full Name</label>
          <input
            type="text"
            class="form-control"
            id="name"
            v-model="form.name"
            placeholder="Enter your full name"
            required
          />
        </div>

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
          <label for="phone" class="form-label">Phone (optional)</label>
          <input
            type="tel"
            class="form-control"
            id="phone"
            v-model="form.phone"
            placeholder="Enter your phone number"
          />
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            type="password"
            class="form-control"
            id="password"
            v-model="form.password"
            placeholder="Minimum 6 characters"
            required
            minlength="6"
          />
        </div>

        <div class="mb-3">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            type="password"
            class="form-control"
            id="confirmPassword"
            v-model="form.confirmPassword"
            placeholder="Confirm your password"
            required
            minlength="6"
          />
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <div class="text-center mt-3">
        <p class="text-muted">
          Already have an account?
          <router-link to="/login" class="text-decoration-none">Login here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../services/api'

export default {
  name: 'RegisterPage',
  data() {
    return {
      form: {
        name: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = ''

      // Validate passwords match
      if (this.form.password !== this.form.confirmPassword) {
        this.error = 'Passwords do not match'
        this.loading = false
        return
      }

      try {
        const response = await authAPI.register({
          name: this.form.name,
          email: this.form.email,
          phone: this.form.phone,
          password: this.form.password
        })

        const { token, user } = response.data

        // Store token and user info
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        this.success = 'Registration successful! Redirecting...'

        setTimeout(() => {
          this.$router.push('/user/dashboard')
        }, 1000)
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
