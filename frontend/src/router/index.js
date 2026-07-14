import { createRouter, createWebHistory } from 'vue-router'

// Auth views
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Admin views
import AdminDashboard from '../views/admin/Dashboard.vue'
import ManageTreks from '../views/admin/ManageTreks.vue'
import ManageStaff from '../views/admin/ManageStaff.vue'
import ManageUsers from '../views/admin/ManageUsers.vue'

// Staff views
import StaffDashboard from '../views/staff/Dashboard.vue'
import StaffTrekDetails from '../views/staff/TrekDetails.vue'
import StaffParticipants from '../views/staff/Participants.vue'

// User views
import UserDashboard from '../views/user/Dashboard.vue'
import TrekList from '../views/user/TrekList.vue'
import BookingHistory from '../views/user/BookingHistory.vue'
import Profile from '../views/user/Profile.vue'

const routes = [
  // Public routes
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },

  // Admin routes
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks', name: 'ManageTreks', component: ManageTreks, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/staff', name: 'ManageStaff', component: ManageStaff, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/users', name: 'ManageUsers', component: ManageUsers, meta: { requiresAuth: true, role: 'admin' } },

  // Staff routes
  { path: '/staff/dashboard', name: 'StaffDashboard', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/staff/treks/:id', name: 'StaffTrekDetails', component: StaffTrekDetails, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/staff/treks/:id/participants', name: 'StaffParticipants', component: StaffParticipants, meta: { requiresAuth: true, role: 'staff' } },

  // User routes
  { path: '/user/dashboard', name: 'UserDashboard', component: UserDashboard, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/user/treks', name: 'TrekList', component: TrekList, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/user/bookings', name: 'BookingHistory', component: BookingHistory, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/user/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true, role: 'trekker' } },

  // Catch all
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // If route requires auth and no token
  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  // If route is guest-only and user is logged in
  if (to.meta.guest && token) {
    const role = user.role
    if (role === 'admin') return next('/admin/dashboard')
    if (role === 'staff') return next('/staff/dashboard')
    return next('/user/dashboard')
  }

  // Role-based access control
  if (to.meta.role && user.role !== to.meta.role) {
    const role = user.role
    if (role === 'admin') return next('/admin/dashboard')
    if (role === 'staff') return next('/staff/dashboard')
    return next('/user/dashboard')
  }

  next()
})

export default router
