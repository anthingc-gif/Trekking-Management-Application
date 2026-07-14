<template>
  <div id="app">
    <Navbar v-if="isLoggedIn" />
    <div class="container-fluid p-0">
      <router-view />
    </div>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
