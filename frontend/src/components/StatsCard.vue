<template>
  <div :class="['stats-card', variant]">
    <h6>{{ title }}</h6>
    <h2>{{ value }}</h2>
    <small v-if="subtitle">{{ subtitle }}</small>
  </div>
</template>

<script>
export default {
  name: 'StatsCard',
  props: {
    title: { type: String, required: true },
    value: { type: [String, Number], required: true },
    subtitle: { type: String, default: '' },
    variant: { type: String, default: 'treks' }
  }
}
</script>
