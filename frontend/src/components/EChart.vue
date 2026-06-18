<template>
  <div ref="chartRef" class="chart"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ option: { type: Object, required: true } })
const chartRef = ref(null)
let chart = null

function render() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.resize()
  chart.setOption(props.option)
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  if (chart) chart.dispose()
})
watch(() => props.option, render, { deep: true })
</script>