import axios from 'axios'
import router from '../router'

const API_BASE_URL = 'http://127.0.0.1:5001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

// ============ AUTH APIs ============
export const authAPI = {
  login(credentials) {
    return api.post('/auth/login', credentials)
  },
  register(userData) {
    return api.post('/auth/register', userData)
  },
  logout() {
    return api.post('/auth/logout')
  },
  getMe() {
    return api.get('/auth/me')
  }
}

// ============ ADMIN APIs ============
export const adminAPI = {
  getDashboard() {
    return api.get('/admin/dashboard')
  },
  // Treks
  getAllTreks() {
    return api.get('/admin/treks')
  },
  createTrek(trekData) {
    return api.post('/admin/treks', trekData)
  },
  updateTrek(trekId, trekData) {
    return api.put(`/admin/treks/${trekId}`, trekData)
  },
  deleteTrek(trekId) {
    return api.delete(`/admin/treks/${trekId}`)
  },
  assignStaff(trekId, staffId) {
    return api.put(`/admin/treks/${trekId}/assign`, { staff_id: staffId })
  },
  // Staff
  getAllStaff() {
    return api.get('/admin/staff')
  },
  createStaff(staffData) {
    return api.post('/admin/staff', staffData)
  },
  updateStaff(staffId, staffData) {
    return api.put(`/admin/staff/${staffId}`, staffData)
  },
  deleteStaff(staffId) {
    return api.delete(`/admin/staff/${staffId}`)
  },
  // Users
  getAllUsers() {
    return api.get('/admin/users')
  },
  toggleBlacklist(userId) {
    return api.put(`/admin/users/${userId}/blacklist`)
  },
  toggleDeactivate(userId) {
    return api.put(`/admin/users/${userId}/deactivate`)
  },
  // Bookings
  getAllBookings() {
    return api.get('/admin/bookings')
  },
  // Search
  search(query, type = 'all') {
    return api.get(`/admin/search?q=${query}&type=${type}`)
  }
}

// ============ STAFF APIs ============
export const staffAPI = {
  getDashboard() {
    return api.get('/staff/dashboard')
  },
  getAssignedTreks() {
    return api.get('/staff/treks')
  },
  updateTrek(trekId, data) {
    return api.put(`/staff/treks/${trekId}`, data)
  },
  getParticipants(trekId) {
    return api.get(`/staff/treks/${trekId}/participants`)
  }
}

// ============ TREK APIs (User) ============
export const trekAPI = {
  getOpenTreks() {
    return api.get('/treks')
  },
  getTrekDetail(trekId) {
    return api.get(`/treks/${trekId}`)
  },
  searchTreks(params) {
    const queryString = new URLSearchParams(params).toString()
    return api.get(`/treks/search?${queryString}`)
  }
}

// ============ BOOKING APIs ============
export const bookingAPI = {
  createBooking(trekId) {
    return api.post('/bookings', { trek_id: trekId })
  },
  getMyBookings() {
    return api.get('/bookings')
  },
  cancelBooking(bookingId) {
    return api.put(`/bookings/${bookingId}/cancel`)
  }
}

// ============ USER APIs ============
export const userAPI = {
  getProfile() {
    return api.get('/user/profile')
  },
  updateProfile(profileData) {
    return api.put('/user/profile', profileData)
  },
  getNotifications() {
    return api.get('/user/notifications')
  },
  markNotificationRead(id) {
    return api.put(`/user/notifications/${id}/read`)
  },
  markAllNotificationsRead() {
    return api.put('/user/notifications/read-all')
  },
  triggerExport() {
    return api.post('/user/export')
  }
}

export default api
