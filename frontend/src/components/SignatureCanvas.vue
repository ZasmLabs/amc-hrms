<template>
	<div class="signature-container">
		<div
			ref="canvasContainer"
			class="signature-canvas-wrapper"
			:class="{ 'read-only': isReadOnly }"
		>
			<canvas
				ref="canvas"
				:width="canvasWidth"
				:height="canvasHeight"
				@mousedown="startDrawing"
				@mousemove="draw"
				@mouseup="stopDrawing"
				@mouseleave="stopDrawing"
				@touchstart="startDrawingTouch"
				@touchmove="drawTouch"
				@touchend="stopDrawing"
				class="signature-canvas"
			></canvas>
			<div v-if="!isReadOnly" class="signature-actions">
				<button
					type="button"
					@click="clearSignature"
					class="signature-clear-btn"
					:title="__('Clear')"
				>
					<FeatherIcon name="x" class="h-4 w-4" />
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from "vue"
import { FeatherIcon } from "frappe-ui"
import { inject } from "vue"

const props = defineProps({
	modelValue: {
		type: String,
		default: "",
	},
	isReadOnly: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

const __ = inject("$translate")

const canvas = ref(null)
const canvasContainer = ref(null)
const canvasWidth = ref(600)
const canvasHeight = ref(200)
const isDrawing = ref(false)
const lastX = ref(0)
const lastY = ref(0)

let ctx = null

onMounted(() => {
	nextTick(() => {
		if (canvas.value) {
			ctx = canvas.value.getContext("2d")
			ctx.strokeStyle = "#000000"
			ctx.lineWidth = 2
			ctx.lineCap = "round"
			ctx.lineJoin = "round"

			// Set canvas size based on container
			if (canvasContainer.value) {
				const containerWidth = canvasContainer.value.clientWidth
				canvasWidth.value = containerWidth > 0 ? containerWidth : 600
			}

			// Load existing signature if present
			if (props.modelValue) {
				loadSignature(props.modelValue)
			}
		}
	})

	// Handle window resize
	window.addEventListener("resize", handleResize)
})

onUnmounted(() => {
	window.removeEventListener("resize", handleResize)
})

watch(
	() => props.modelValue,
	(newValue) => {
		if (newValue && ctx) {
			loadSignature(newValue)
		} else if (!newValue && ctx) {
			clearCanvas()
		}
	}
)

function handleResize() {
	if (canvasContainer.value) {
		const containerWidth = canvasContainer.value.clientWidth
		if (containerWidth > 0) {
			canvasWidth.value = containerWidth
		}
	}
}

function loadSignature(imageData) {
	if (!ctx || !imageData) return

	const img = new Image()
	img.onload = () => {
		ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
		ctx.drawImage(img, 0, 0, canvasWidth.value, canvasHeight.value)
	}
	img.src = imageData
}

function clearCanvas() {
	if (!ctx) return
	ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
}

function getEventPos(e) {
	const rect = canvas.value.getBoundingClientRect()
	return {
		x: e.clientX - rect.left,
		y: e.clientY - rect.top,
	}
}

function getTouchPos(e) {
	const rect = canvas.value.getBoundingClientRect()
	const touch = e.touches[0] || e.changedTouches[0]
	return {
		x: touch.clientX - rect.left,
		y: touch.clientY - rect.top,
	}
}

function startDrawing(e) {
	if (props.isReadOnly) return
	isDrawing.value = true
	const pos = getEventPos(e)
	lastX.value = pos.x
	lastY.value = pos.y
}

function startDrawingTouch(e) {
	if (props.isReadOnly) return
	e.preventDefault()
	isDrawing.value = true
	const pos = getTouchPos(e)
	lastX.value = pos.x
	lastY.value = pos.y
}

function draw(e) {
	if (!isDrawing.value || props.isReadOnly) return
	const pos = getEventPos(e)
	drawLine(lastX.value, lastY.value, pos.x, pos.y)
	lastX.value = pos.x
	lastY.value = pos.y
	saveSignature()
}

function drawTouch(e) {
	if (!isDrawing.value || props.isReadOnly) return
	e.preventDefault()
	const pos = getTouchPos(e)
	drawLine(lastX.value, lastY.value, pos.x, pos.y)
	lastX.value = pos.x
	lastY.value = pos.y
	saveSignature()
}

function drawLine(x1, y1, x2, y2) {
	if (!ctx) return
	ctx.beginPath()
	ctx.moveTo(x1, y1)
	ctx.lineTo(x2, y2)
	ctx.stroke()
}

function stopDrawing() {
	if (isDrawing.value) {
		isDrawing.value = false
		saveSignature()
	}
}

function saveSignature() {
	if (!canvas.value) return
	const imageData = canvas.value.toDataURL("image/png")
	emit("update:modelValue", imageData)
}

function clearSignature() {
	clearCanvas()
	emit("update:modelValue", "")
}
</script>

<style scoped>
.signature-container {
	width: 100%;
}

.signature-canvas-wrapper {
	position: relative;
	width: 100%;
	background: white;
	border: 2px solid #e5e7eb;
	border-radius: 8px;
	overflow: hidden;
}

.signature-canvas-wrapper.read-only {
	opacity: 0.7;
	cursor: not-allowed;
}

.signature-canvas {
	display: block;
	width: 100%;
	height: 200px;
	cursor: crosshair;
	touch-action: none;
}

.signature-canvas-wrapper.read-only .signature-canvas {
	cursor: not-allowed;
}

.signature-actions {
	position: absolute;
	top: 8px;
	right: 8px;
	z-index: 10;
}

.signature-clear-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 32px;
	height: 32px;
	background: white;
	border: 1px solid #e5e7eb;
	border-radius: 6px;
	cursor: pointer;
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	transition: all 0.2s;
}

.signature-clear-btn:hover {
	background: #f3f4f6;
	border-color: #d1d5db;
}

.signature-clear-btn:active {
	transform: scale(0.95);
}

</style>

