<template>
	<div class="flex flex-col gap-2">
		<!-- Display existing images in a grid -->
		<div v-if="imageList.length > 0" class="grid grid-cols-2 gap-3">
			<div
				v-for="(image, index) in imageList"
				:key="index"
				class="relative"
			>
				<img
					:src="getImageUrl(image)"
					:alt="`${label} ${index + 1}`"
					class="w-full h-48 object-cover rounded border border-gray-300"
				/>
				<button
					v-if="!isReadOnly"
					type="button"
					@click="removeImage(index)"
					class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
				>
					<FeatherIcon name="x" class="h-4 w-4" />
				</button>
			</div>
		</div>

		<!-- Upload button -->
		<label v-if="!isReadOnly" class="file-select cursor-pointer">
			<div
				class="flex flex-col w-full border-2 border-dashed border-gray-300 rounded-lg p-4 items-center justify-center gap-2 hover:border-gray-400 transition-colors"
			>
				<FeatherIcon name="upload" class="h-8 w-8 text-gray-500" />
				<span class="text-sm font-medium text-gray-700">
					{{ imageList.length > 0 ? __("Add More Photos") : __("Add Photos") }}
				</span>
				<span class="text-xs text-gray-500">
					{{ __("Click to select one or more images") }}
				</span>
			</div>
			<input
				ref="fileInput"
				type="file"
				accept="image/*"
				multiple
				class="hidden"
				@change="handleFileSelect"
			/>
		</label>
	</div>
</template>

<script setup>
import { ref, computed, inject } from "vue"
import { FeatherIcon } from "frappe-ui"
import { frappeRequest } from "frappe-ui"

const __ = inject("$translate")

const props = defineProps({
	modelValue: String,
	label: String,
	fieldname: String,
	isReadOnly: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])
const fileInput = ref(null)

// Parse modelValue to get array of image file names
// Frappe stores multiple attachments as comma-separated string
const imageList = computed(() => {
	if (!props.modelValue) return []
	// Split by comma and trim whitespace, filter out empty strings
	return props.modelValue
		.split(",")
		.map((img) => img.trim())
		.filter((img) => img.length > 0)
})

function getImageUrl(value) {
	if (!value) return ""
	// If it's already a full URL, return it
	if (value.startsWith("http://") || value.startsWith("https://")) {
		return value
	}
	// If it's a file name, construct the URL
	// Frappe attachments are typically at /files/[filename]
	return `/files/${value}`
}

// Update the modelValue by joining the image list with commas
function updateModelValue(images) {
	if (images.length === 0) {
		emit("update:modelValue", "")
	} else {
		emit("update:modelValue", images.join(","))
	}
}

async function handleFileSelect(event) {
	const files = Array.from(event.target.files || [])
	if (files.length === 0) return

	// Filter to only image files
	const imageFiles = files.filter((file) => file.type.startsWith("image/"))
	if (imageFiles.length === 0) {
		alert(__("Please select image files"))
		return
	}

	// If some files were filtered out, notify user
	if (imageFiles.length < files.length) {
		alert(__("Some files were skipped. Only image files are allowed."))
	}

	// Start with existing images
	const currentImages = [...imageList.value]
	const uploadedFiles = []

	try {
		// Upload all selected images
		for (const file of imageFiles) {
			const formData = new FormData()
			formData.append("file", file, file.name)
			formData.append("is_private", "0")
			formData.append("folder", "Home")
			formData.append("file_name", file.name)

			const response = await fetch("/api/method/upload_file", {
				method: "POST",
				headers: {
					"X-Frappe-CSRF-Token": window.csrf_token || document.querySelector('meta[name="csrf-token"]')?.content,
				},
				body: formData,
			})

			if (!response.ok) {
				const errorData = await response.json().catch(() => ({}))
				throw new Error(errorData.message || "Upload failed")
			}

			const result = await response.json()

			// Get the file name from the response
			let fileName = null
			if (result?.message) {
				if (result.message.file_name) {
					fileName = result.message.file_name
				} else if (result.message.name) {
					// Fetch the File document to get file_name
					const fileDoc = await frappeRequest({
						url: `/api/resource/File/${result.message.name}`,
						method: "GET",
					})
					if (fileDoc?.data?.file_name) {
						fileName = fileDoc.data.file_name
					}
				}
			}

			if (fileName) {
				uploadedFiles.push(fileName)
			}
		}

		// Combine existing images with newly uploaded ones
		const allImages = [...currentImages, ...uploadedFiles]
		updateModelValue(allImages)
	} catch (error) {
		console.error("Error uploading images:", error)
		alert(__("Failed to upload images. Please try again."))
	}

	// Reset the input
	if (fileInput.value) {
		fileInput.value.value = ""
	}
}

function removeImage(index) {
	const newImages = imageList.value.filter((_, i) => i !== index)
	updateModelValue(newImages)
}
</script>

