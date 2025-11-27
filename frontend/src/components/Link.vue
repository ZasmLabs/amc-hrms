<template>
	<Autocomplete
		ref="autocompleteRef"
		size="sm"
		v-model="value"
		:placeholder="__('Select {0}', [__(doctype)])"
		:options="options.data || []"
		:class="disabled ? 'pointer-events-none' : ''"
		:disabled="disabled"
		@update:query="handleQueryUpdate"
	/>
</template>

<script setup>
import { createResource, Autocomplete, debounce } from "frappe-ui"
import { ref, computed, watch } from "vue"

const props = defineProps({
	doctype: {
		type: String,
		required: true,
	},
	modelValue: {
		type: String,
		required: false,
		default: "",
	},
	filters: {
		type: Object,
		default: {},
	},
	disabled: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

const autocompleteRef = ref(null)
const searchText = ref("")

const value = computed({
	get: () => props.modelValue,
	set: (val) => {
		const newVal = (val && typeof val === "object" && val.value !== undefined) ? val.value : val
		emit("update:modelValue", newVal || "")
	},
})

const options = createResource({
	url: "frappe.desk.search.search_link",
	params: computed(() => {
		console.log("[Link Component] Options params computed:", {
			doctype: props.doctype,
			txt: searchText.value,
			filters: props.filters,
		})
		return {
			doctype: props.doctype,
			txt: searchText.value,
			filters: props.filters,
		}
	}),
	method: "POST",
	transform: (data) => {
		console.log("[Link Component] Transform data:", data)
		return data.map((doc) => {
			// Extract title from description (first part before comma) or use label if available
			const title = doc?.label || doc?.description?.split(",")?.[0]?.trim()
			
			// For Customer List, format as "CUST-0001 : [Customer Name]"
			if (props.doctype === "Customer List" && title) {
				return {
					label: `${doc.value} : ${title}`,
					value: doc.value,
				}
			}
			
			// For Customer Branch, format as "CB-001 : [Actual Branch Name]"
			if (props.doctype === "Customer Branch") {
				// Use label (which contains the branch name from title_field) or description, fallback to value
				const branchName = doc?.label || doc?.description?.split(",")?.[0]?.trim() || doc.value
				return {
					label: `${doc.value} : ${branchName}`,
					value: doc.value,
				}
			}
			
			// For other doctypes, use default format
			return {
				label: title ? `${title} : ${doc.value}` : doc.value,
				value: doc.value,
			}
		})
	},
	onSuccess(data) {
		console.log("[Link Component] Options loaded successfully:", data)
	},
	onError(error) {
		console.error("[Link Component] Options error:", error)
	},
})

const reloadOptions = (searchTextVal) => {
	options.update({
		params: {
			txt: searchTextVal,
			doctype: props.doctype,
			filters: props.filters
		},
	})
	options.reload()
}

const handleQueryUpdate = debounce((newQuery) => {
    const val = newQuery || ""

    if (val === "" && props.modelValue) return

    if (searchText.value === val) return
    searchText.value = val
    reloadOptions(val)
}, 300)

watch(
	() => props.doctype,
	() => {
		if (!props.doctype || props.doctype === options.doctype) return
		reloadOptions(props.modelValue)
	},
	{ immediate: true }
)

// Watch for filter changes and reload options
watch(
	() => props.filters,
	(newFilters, oldFilters) => {
		// Only reload if filters actually changed
		if (JSON.stringify(newFilters) !== JSON.stringify(oldFilters)) {
			console.log("[Link Component] Filters changed, reloading options:", { newFilters, oldFilters })
			reloadOptions(searchText.value || props.modelValue || "")
		}
	},
	{ deep: true }
)
</script>
