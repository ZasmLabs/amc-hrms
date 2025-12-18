<template>
	<div class="flex flex-col gap-2">
		<!-- Display existing image if available -->
		<div v-if="modelValue" class="relative">
			<img
				:src="getImageUrl(modelValue)"
				:alt="label"
				class="w-full h-48 object-cover rounded border border-gray-300"
			/>
			<button
				v-if="!isReadOnly"
				type="button"
				@click="removeImage"
				class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
			>
				<FeatherIcon name="x" class="h-4 w-4" />
			</button>
		</div>

		<!-- Upload button -->
		<label v-if="!isReadOnly" class="file-select cursor-pointer">
			<div
				class="flex flex-col w-full border-2 border-dashed border-gray-300 rounded-lg p-4 items-center justify-center gap-2 hover:border-gray-400 transition-colors"
			>
				<FeatherIcon name="upload" class="h-8 w-8 text-gray-500" />
				<span class="text-sm font-medium text-gray-700">
					{{ modelValue ? __("Change Photo") : __("Upload Photo") }}
				</span>
				<span class="text-xs text-gray-500">
					{{ __("Click to select an image") }}
				</span>
			</div>
			<input
				ref="fileInput"
				type="file"
				accept="image/*"
				class="hidden"
				@change="handleFileSelect"
			/>
		</label>
	</div>
</template>

<script setup>
import { ref, inject } from "vue"
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

async function handleFileSelect(event) {
	const file = event.target.files?.[0]
	if (!file) return

	// Check if it's an image
	if (!file.type.startsWith("image/")) {
		alert(__("Please select an image file"))
		return
	}

	try {
		// Use FormData to upload the file
		const formData = new FormData()
		formData.append("file", file, file.name)
		formData.append("is_private", "0")
		formData.append("folder", "Home")
		formData.append("file_name", file.name)

		// Use native fetch for FormData upload
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

		// The API returns the File document
		if (result?.message) {
			// If file_name is directly in message, use it
			if (result.message.file_name) {
				emit("update:modelValue", result.message.file_name)
			} else if (result.message.name) {
				// Otherwise, fetch the File document to get file_name
				const fileDoc = await frappeRequest({
					url: `/api/resource/File/${result.message.name}`,
					method: "GET",
				})
				if (fileDoc?.data?.file_name) {
					emit("update:modelValue", fileDoc.data.file_name)
				}
			}
		}
	} catch (error) {
		console.error("Error uploading image:", error)
		alert(__("Failed to upload image. Please try again."))
	}

	// Reset the input
	if (fileInput.value) {
		fileInput.value.value = ""
	}
}

function removeImage() {
	emit("update:modelValue", "")
}
</script>

