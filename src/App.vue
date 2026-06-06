<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from './stores/user';

onMounted(() => {
  const userStore = useUserStore();
  userStore.restoreSession();
});
</script>