<template>
	<div class="flex flex-col gap-1.5">
		<!-- Label -->
		<span
			:class="[
				props.reqd ? `after:content-['_*'] after:text-red-600` : ``,
				`block text-sm leading-5 text-gray-700`,
			]"
		>
			{{ __("Contact Person") }}
		</span>

		<!-- Autocomplete dropdown -->
		<Autocomplete
			ref="autocompleteRef"
			size="sm"
			v-model="selectedValue"
			:options="autocompleteOptions"
			:placeholder="__('Select contact person')"
			:disabled="isReadOnly"
			@update:query="handleQueryUpdate"
			@update:modelValue="handleValueChange"
		/>

		<!-- Inline Create Form (like Cash Memo) -->
		<div
			v-if="showCreateForm"
			class="flex flex-col p-4 bg-white rounded-lg border border-gray-200 gap-4 mt-2"
		>
			<div class="flex flex-row justify-between items-center">
				<h3 class="text-sm font-semibold text-gray-800">{{ __("Create New Contact Person") }}</h3>
				<Button
					icon="x"
					variant="ghost"
					size="sm"
					@click="cancelCreate"
					:title="__('Cancel')"
				/>
			</div>

			<!-- Name Field -->
			<div class="flex flex-col gap-1.5">
				<label class="block text-sm leading-5 text-gray-700">
					{{ __("Name") }} <span class="text-red-600">*</span>
				</label>
				<Input
					v-model="newContact.name1"
					type="text"
					:placeholder="__('Enter contact name')"
					class="w-full"
					@keyup.enter="createContactPerson"
				/>
			</div>

			<!-- Mobile and Email Row -->
			<div class="grid grid-cols-2 gap-4">
				<div class="flex flex-col gap-1.5">
					<label class="block text-sm leading-5 text-gray-700">
						{{ __("Mobile") }}
					</label>
					<Input
						v-model="newContact.mobile"
						type="text"
						:placeholder="__('Enter mobile number')"
						class="w-full"
					/>
				</div>
				<div class="flex flex-col gap-1.5">
					<label class="block text-sm leading-5 text-gray-700">
						{{ __("Email") }}
					</label>
					<Input
						v-model="newContact.email"
						type="email"
						:placeholder="__('Enter email address')"
						class="w-full"
					/>
				</div>
			</div>

			<!-- Branch Field (read-only) -->
			<div v-if="branch" class="flex flex-col gap-1.5">
				<label class="block text-sm leading-5 text-gray-700">
					{{ __("Branch") }}
				</label>
				<Input
					:value="branch"
					type="text"
					disabled
					class="w-full bg-gray-50"
				/>
			</div>

			<!-- Error Message -->
			<div v-if="createError" class="text-sm text-red-600">
				{{ createError }}
			</div>

			<!-- Action Buttons -->
			<div class="flex flex-row gap-2 justify-end">
				<Button
					variant="ghost"
					@click="cancelCreate"
				>
					{{ __("Cancel") }}
				</Button>
				<Button
					variant="solid"
					@click="createContactPerson"
					:loading="isCreating"
					:disabled="!canCreate"
				>
					{{ __("Create") }}
				</Button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue"
import { Autocomplete, Button, Input, createResource, toast, debounce } from "frappe-ui"

const __ = inject("$translate")

const props = defineProps({
	modelValue: {
		type: String,
		default: "",
	},
	branch: {
		type: String,
		default: "",
	},
	customer: {
		type: String,
		default: "",
	},
	isReadOnly: {
		type: Boolean,
		default: false,
	},
	reqd: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

const autocompleteRef = ref(null)
const searchText = ref("")
const showCreateForm = ref(false)
const isCreating = ref(false)
const createError = ref("")

const newContact = ref({
	name1: "",
	mobile: "",
	email: "",
	branch: props.branch || "",
	customer: props.customer || "",
})

// Build filters in the format expected by search_link API
const linkFilters = computed(() => {
	const filters = {}
	if (props.branch) {
		filters.branch = props.branch
	}
	return filters
})

// Fetch contact persons from API - auto-load when branch is available
const contactOptionsResource = createResource({
	url: "frappe.desk.search.search_link",
	params: computed(() => ({
		doctype: "Customer Contact",
		txt: searchText.value || "",
		filters: linkFilters.value,
	})),
	method: "POST",
	auto: computed(() => !!props.branch), // Auto-load when branch is available
	transform: (data) => {
		if (!data || !Array.isArray(data)) return []
		return data.map((doc) => {
			const title = doc?.label || doc?.description?.split(",")?.[0]?.trim()
			return {
				label: title ? `${title} : ${doc.value}` : doc.value,
				value: doc.value,
			}
		})
	},
	onSuccess(data) {
		console.log("[ContactPersonField] Options loaded:", data)
	},
	onError(error) {
		console.error("[ContactPersonField] Error loading options:", error)
	},
})

// Reload options function
function reloadOptions(searchTextVal = "") {
	contactOptionsResource.update({
		params: {
			doctype: "Customer Contact",
			txt: searchTextVal,
			filters: linkFilters.value,
		},
	})
	contactOptionsResource.reload()
}

// Computed autocomplete options - add "Create new" option if query doesn't match
const autocompleteOptions = computed(() => {
	const options = contactOptionsResource.data || []
	const query = searchText.value?.trim() || ""
	
	// If there's a query and no exact match, add "Create new" option
	if (query && !props.isReadOnly) {
		const hasExactMatch = options.some(
			(opt) => opt.label?.toLowerCase().includes(query.toLowerCase()) || 
			         opt.value?.toLowerCase() === query.toLowerCase()
		)
		
		if (!hasExactMatch && query.length > 0) {
			return [
				...options,
				{
					label: __("Create new: {0}", [query]),
					value: "__CREATE_NEW__",
					isCreateOption: true,
				},
			]
		}
	}
	
	return options
})

// Selected value for autocomplete
const selectedValue = computed({
	get: () => {
		if (!props.modelValue) return null
		// Find the option that matches the current value
		const options = contactOptionsResource.data || []
		const found = options.find((opt) => opt.value === props.modelValue)
		if (found) return found
		// If not found in current options, return a temporary option
		return { label: props.modelValue, value: props.modelValue }
	},
	set: (val) => {
		if (!val) {
			emit("update:modelValue", "")
			return
		}
		
		// Check if it's the "Create new" option
		if (val.value === "__CREATE_NEW__" || val.isCreateOption) {
			openCreateFormWithName(searchText.value)
			return
		}
		
		emit("update:modelValue", val.value || val)
	},
})

// Handle query update
const handleQueryUpdate = debounce((newQuery) => {
	const val = newQuery || ""
	if (val === "" && props.modelValue) {
		// Don't clear search if we have a value, but still reload to show all options
		reloadOptions("")
		return
	}
	if (searchText.value === val) return
	searchText.value = val
	reloadOptions(val)
}, 300)

// Handle value change
function handleValueChange(value) {
	if (!value) {
		emit("update:modelValue", "")
		showCreateForm.value = false
		return
	}
	
	// Check if it's the "Create new" option
	if (value.value === "__CREATE_NEW__" || value.isCreateOption) {
		openCreateFormWithName(searchText.value)
		return
	}
	
	emit("update:modelValue", value.value || value)
	showCreateForm.value = false
}

// Open create form with pre-filled name (inline, not modal)
function openCreateFormWithName(name = "") {
	if (!props.branch) {
		toast({
			title: __("Branch Required"),
			text: __("Please select a branch first before creating a new contact person."),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		})
		return
	}
	
	newContact.value = {
		name1: name.trim() || "",
		mobile: "",
		email: "",
		branch: props.branch || "",
		customer: props.customer || "",
	}
	createError.value = ""
	showCreateForm.value = true
}

// Cancel create form
function cancelCreate() {
	showCreateForm.value = false
	createError.value = ""
	newContact.value = {
		name1: "",
		mobile: "",
		email: "",
		branch: props.branch || "",
		customer: props.customer || "",
	}
	// Clear the autocomplete selection
	searchText.value = ""
	if (autocompleteRef.value) {
		autocompleteRef.value.value = null
	}
}

// Check if form can be submitted
const canCreate = computed(() => {
	return newContact.value.name1 && newContact.value.name1.trim() !== ""
})

// Create new contact person
const createContactResource = createResource({
	url: `/api/resource/Customer Contact`,
	method: "POST",
	onSuccess(data) {
		console.log("Contact created successfully:", data)
	},
	onError(error) {
		console.error("Error creating contact:", error)
	},
})

async function createContactPerson() {
	if (!canCreate.value) {
		createError.value = __("Name is required")
		return
	}

	if (!props.branch) {
		createError.value = __("Branch is required")
		return
	}

	isCreating.value = true
	createError.value = ""

	try {
		const doc = {
			doctype: "Customer Contact",
			name1: newContact.value.name1.trim(),
			mobile: newContact.value.mobile || "",
			email: newContact.value.email || "",
			branch: props.branch,
		}
		
		// Include customer if available
		if (props.customer) {
			doc.customer = props.customer
		}

		// Use the API resource endpoint - send data directly
		await createContactResource.submit({ data: doc })
		
		// Show success message
		toast({
			title: __("Success"),
			text: __("Contact person created successfully."),
			icon: "check",
			iconClasses: "text-green-600",
		})
		
		// Reload options to include the new contact
		reloadOptions("")
		
		// Close the form
		showCreateForm.value = false
		createError.value = ""
		newContact.value = {
			name1: "",
			mobile: "",
			email: "",
			branch: props.branch || "",
			customer: props.customer || "",
		}
	} catch (error) {
		console.error("Error creating contact person:", error)
		// Handle different error formats
		if (error.exc_type === "ValidationError" || error.exc_type === "MandatoryError") {
			createError.value = error.message || __("Validation error. Please check all required fields.")
		} else if (error.messages && Array.isArray(error.messages)) {
			createError.value = error.messages[0] || __("Failed to create contact person")
		} else if (error.message) {
			createError.value = error.message
		} else {
			createError.value = __("Failed to create contact person. Please try again.")
		}
	} finally {
		isCreating.value = false
	}
}

// Watch for branch/customer changes to update newContact defaults and reload options
watch(
	() => props.branch,
	(newBranch) => {
		if (newBranch) {
			newContact.value.branch = newBranch
			// Reload options when branch changes
			reloadOptions(searchText.value || "")
		} else {
			// Clear options if no branch
			contactOptionsResource.data = []
		}
	},
	{ immediate: true }
)

watch(
	() => props.customer,
	(newCustomer) => {
		if (newCustomer) {
			newContact.value.customer = newCustomer
		}
	}
)

// Watch for modelValue changes to reload options if needed
watch(
	() => props.modelValue,
	(newValue) => {
		if (newValue && contactOptionsResource.data) {
			const exists = contactOptionsResource.data.some((opt) => opt.value === newValue)
			if (!exists && props.branch) {
				// Reload if the value doesn't exist in current options
				reloadOptions("")
			}
		}
	}
)
</script>
