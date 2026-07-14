<template>
  <div class="card mb-4">
    <div class="card-body">
      <div class="row g-3">
        <div class="col-md-4">
          <div class="search-box">
            <input
              type="text"
              class="form-control"
              :value="modelValue"
              @input="$emit('update:modelValue', $event.target.value)"
              :placeholder="placeholder"
              @keyup.enter="$emit('search')"
            />
          </div>
        </div>
        <slot></slot>
        <div class="col-md-2">
          <button class="btn btn-primary w-100" @click="$emit('search')">Search</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchFilter',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Search...' }
  },
  emits: ['update:modelValue', 'search']
}
</script>
