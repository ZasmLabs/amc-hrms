<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields"
				ref="formRef"
				doctype="Service Call"
				v-model="serviceCall"
				:isSubmittable="!!props.id"
				:fields="formFields"
				:id="props.id"
				:tabbedView="tabs && tabs.length > 0"
				:tabs="tabs"
				:showAttachmentView="false"
			>
				<!-- Custom Technicians dropdown (single-select) -->
				<template #technician_list="{ isFormReadOnly }">
					<div class="flex flex-col gap-1.5 mt-2">
						<span class="block text-sm leading-5 text-gray-700">
							{{ __("Technicians") }}
						</span>
						<Autocomplete
							v-model="selectedTechnician"
							:placeholder="__('Select Technician')"
							:options="technicianOptions"
							:disabled="isFormReadOnly"
						/>
					</div>
				</template>

				<!-- Cash Memo Table -->
				<template #table_whpt="{ isFormReadOnly }">
					<CashMemoTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>

				<!-- Reopen Call Table - Only show for existing documents -->
				<template v-if="props.id" #reopen_call="{ isFormReadOnly }">
					<ReopenCallListTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>

				<!-- Custom Contact Person Field with Create functionality -->
				<template #contact_person="{ isFormReadOnly }">
					<ContactPersonField
						:modelValue="serviceCall.contact_person"
						@update:modelValue="(val) => serviceCall.contact_person = val"
						:branch="serviceCall.branch"
						:customer="serviceCall.customer"
						:isReadOnly="isFormReadOnly"
					/>
				</template>
			</FormView>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent } from "@ionic/vue"
import { createResource, Autocomplete } from "frappe-ui"
import { ref, computed, watch, onMounted } from "vue"
import { inject } from "vue"

import FormView from "@/components/FormView.vue"
import CashMemoTable from "@/components/CashMemoTable.vue"
import ReopenCallListTable from "@/components/ReopenCallListTable.vue"
import ContactPersonField from "@/components/ContactPersonField.vue"
import { userResource } from "@/data/user"

const __ = inject("$translate")
const dayjs = inject("$dayjs")

const today = dayjs().format("YYYY-MM-DD")

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const tabs = computed(() => {
	// Don't show tabs for new documents (first stage creation)
	if (!props.id) {
		return null
	}
	
	const tabList = []
	if (formFields.value) {
		// Find tab fields
		const serviceReportTab = formFields.value.find((f) => f.fieldname === "service_request_form_tab")
		const cashMemoTab = formFields.value.find((f) => f.fieldname === "cash_memo_tab")
		const reopenLogTab = formFields.value.find((f) => f.fieldname === "reopen_log_tab")

		if (serviceReportTab) {
			tabList.push({ name: "Service Report", lastField: "customer_sign" })
		}
		if (cashMemoTab) {
			tabList.push({ name: "Cash Memo", lastField: "table_whpt" })
		}
		if (reopenLogTab) {
			tabList.push({ name: "Reopen Log", lastField: "reopen_call" })
		}
	}
	return tabList.length > 0 ? tabList : null
})

// object to store form data
const serviceCall = ref({
	technician_list: [],
})

// currently selected technician in dropdown
const selectedTechnician = ref(null)
const isTechnicianInitializing = ref(false)

// Flag to track if form is being initialized/reloaded (to prevent watchers from clearing fields)
const isFormInitializing = ref(false)

// Technicians dropdown: employees with department = "Technician - AA" and status = "Active"
const techniciansResource = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Employee",
		fields: ["name", "employee_name", "first_name", "designation", "department", "cell_number"],
		filters: {
			department: "Technician - AA",
			status: "Active",
		},
		limit_page_length: 1000,
	},
	auto: true,
})

const technicianOptions = computed(() => {
	if (!techniciansResource.data) return []

	return techniciansResource.data.map((emp) => ({
		label: emp.employee_name || emp.first_name || emp.name,
		value: emp.name,
		employee: emp,
	}))
})

// When a technician is selected from the dropdown, update technician_list
function handleTechnicianSelect(selected) {
	if (!selected || !selected.value) {
		return
	}

	const emp = techniciansResource.data?.find((e) => e.name === selected.value)
	if (!emp) return

	// For now, set a single technician row in technician_list
	serviceCall.value.technician_list = [
		{
			employee: emp.name,
			employee_name: emp.employee_name || emp.first_name || emp.name,
			designation: emp.designation || "",
			department: emp.department || "",
			data_jghu: emp.cell_number || "",
			date: today,
		},
	]
}

// Watch the selected technician and update technician_list when it changes.
// We skip updates when we're just initializing from an existing document.
watch(
	() => selectedTechnician.value,
	(val) => {
		// Ignore changes triggered during initialization
		if (isTechnicianInitializing.value) {
			isTechnicianInitializing.value = false
			return
		}

		if (!val) {
			return
		}

		handleTechnicianSelect(val)
	}
)

// When opening an existing Service Call, pre-select the technician
// in the dropdown based on the current technician_list so that the
// UI reflects the already assigned technician.
watch(
	() => serviceCall.value.technician_list,
	(list) => {
		if (!props.id || !Array.isArray(list) || !list.length) {
			return
		}

		const firstTech = list[0]

		// If a technician is already selected and matches, do nothing
		if (selectedTechnician.value && selectedTechnician.value.value === firstTech.employee) {
			return
		}

		// Mark that we're initializing so the selectedTechnician watcher
		// doesn't treat this as a user-driven change.
		isTechnicianInitializing.value = true

		selectedTechnician.value = {
			label: firstTech.employee_name || firstTech.employee,
			value: firstTech.employee,
			employee: {
				name: firstTech.employee,
				employee_name: firstTech.employee_name,
				designation: firstTech.designation,
				department: firstTech.department,
				cell_number: firstTech.data_jghu,
			},
		}
	},
	{ deep: true }
)

// Fetch Customer List with custom format: "CUST-0001 : [Customer Name]"
const customerList = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Customer List",
		fields: ["name", "customer_name"],
		limit_page_length: 1000,
	},
	transform(data) {
		return data.map((customer) => ({
			label: `${customer.name} : ${customer.customer_name || customer.name}`,
			value: customer.name,
		}))
	},
	auto: true,
})

// Note: We don't need separate resources for branchList and contactedPersonList
// because the Link component handles its own data fetching via frappe.desk.search.search_link
// using the linkFilters we set in the formFields computed property

// get form fields
const formFieldsResource = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Service Call" },
})

// Computed property to make fields reactive to customerList and serviceCall changes
// Include resource data and serviceCall values in dependencies to make it reactive
const formFields = computed(() => {
	if (!formFieldsResource.data) return null
	
	// Access resource data and serviceCall values to make computed reactive to changes
	const _customerListData = customerList.data
	const _selectedCustomer = serviceCall.value.customer
	const _selectedBranch = serviceCall.value.branch
	
	console.log("[FormFields] Recomputing with customer:", _selectedCustomer, "branch:", _selectedBranch)
	
	const fields = getFilteredFields(formFieldsResource.data).map((field) => {
		// Create a copy of the field to avoid mutating the original
		const fieldCopy = { ...field }
		
		// Update customer field with documentList when customerList is loaded
		if (fieldCopy.fieldname === "customer" && fieldCopy.options === "Customer List") {
			if (_customerListData) {
				fieldCopy.documentList = _customerListData
			}
		}
		
		// Update branch field - use Link component with dynamic filters
		if (fieldCopy.fieldname === "branch") {
			// Don't set documentList - let it use Link component
			// But update linkFilters to use actual customer value
			if (_selectedCustomer) {
				fieldCopy.linkFilters = {
					customer: _selectedCustomer
				}
				console.log("[FormFields] Branch field - Setting linkFilters with customer:", _selectedCustomer)
			} else {
				// If no customer, set impossible filter to show empty
				fieldCopy.linkFilters = {
					customer: "__NO_CUSTOMER__"
				}
				console.log("[FormFields] Branch field - No customer selected, using empty filter")
			}
		}
		
		// Update contacted_person field - use Link component with dynamic filters
		if (fieldCopy.fieldname === "contacted_person") {
			// Don't set documentList - let it use Link component
			// But update linkFilters to use actual branch value
			if (_selectedBranch) {
				fieldCopy.linkFilters = {
					branch: _selectedBranch
				}
				console.log("[FormFields] Contacted Person field - Setting linkFilters with branch:", _selectedBranch)
			} else {
				// If no branch, set impossible filter to show empty
				fieldCopy.linkFilters = {
					branch: "__NO_BRANCH__"
				}
				console.log("[FormFields] Contacted Person field - No branch selected, using empty filter")
			}
		}
		
		// Update contact_person field - use Link component with dynamic filters
		// Note: This field uses a custom component (ContactPersonField) which handles the Link component internally
		// We still set linkFilters here for consistency, but the custom component will use its own filters
		if (fieldCopy.fieldname === "contact_person") {
			if (_selectedBranch) {
				fieldCopy.linkFilters = {
					branch: _selectedBranch
				}
				console.log("[FormFields] Contact Person field - Setting linkFilters with branch:", _selectedBranch)
			} else {
				// If no branch, set impossible filter to show empty
				fieldCopy.linkFilters = {
					branch: "__NO_BRANCH__"
				}
				console.log("[FormFields] Contact Person field - No branch selected, using empty filter")
			}
		}
		
		return fieldCopy
	})
	
	return fields
})
formFieldsResource.reload()

// Watch for customer changes to clear dependent fields
// Only clear if it's a user-initiated change, not during form initialization/reload
watch(
	() => serviceCall.value.customer,
	(newCustomer, oldCustomer) => {
		console.log("[Customer Watcher] Customer changed:", { old: oldCustomer, new: newCustomer, isInitializing: isFormInitializing.value })
		
		// Skip clearing during initialization/reload
		if (isFormInitializing.value) {
			console.log("[Customer Watcher] Skipping clear - form is initializing")
			return
		}
		
		// Only clear if customer actually changed and old value existed (user change, not initial load)
		if (newCustomer !== oldCustomer && oldCustomer !== undefined && oldCustomer !== null && oldCustomer !== "") {
			// Clear branch and contacted_person when customer changes
			serviceCall.value.branch = ""
			serviceCall.value.contacted_person = ""
			console.log("[Customer Watcher] Cleared branch and contacted_person")
		}
	},
	{ immediate: false }
)

// Watch for branch changes to clear dependent fields
// Only clear if it's a user-initiated change, not during form initialization/reload
watch(
	() => serviceCall.value.branch,
	(newBranch, oldBranch) => {
		console.log("[Branch Watcher] Branch changed:", { old: oldBranch, new: newBranch, isInitializing: isFormInitializing.value })
		
		// Skip clearing during initialization/reload
		if (isFormInitializing.value) {
			console.log("[Branch Watcher] Skipping clear - form is initializing")
			return
		}
		
		// Only clear if branch actually changed and old value existed (user change, not initial load)
		if (newBranch !== oldBranch && oldBranch !== undefined && oldBranch !== null && oldBranch !== "") {
			// Clear contacted_person when branch changes
			serviceCall.value.contacted_person = ""
			console.log("[Branch Watcher] Cleared contacted_person")
		}
	},
	{ immediate: false }
)

// Watch for document loading/reloading to set initialization flag
// This prevents watchers from clearing fields during form initialization
watch(
	() => props.id,
	(newId, oldId) => {
		// When transitioning from new doc (no id) to existing doc (has id), we're initializing
		if (!oldId && newId) {
			console.log("[Form Init] Document ID appeared, setting initialization flag")
			isFormInitializing.value = true
			// Reset flag after a short delay to allow form to load
			setTimeout(() => {
				isFormInitializing.value = false
				console.log("[Form Init] Initialization complete, clearing flag")
			}, 500)
		}
	},
	{ immediate: false }
)

// Watch for when serviceCall gets populated with document data (after save/reload)
// This happens when FormView updates the modelValue after documentResource loads
watch(
	() => serviceCall.value?.name,
	(newName, oldName) => {
		// When name appears or changes (document loaded/reloaded), set initialization flag
		if (newName && newName !== oldName && props.id) {
			console.log("[Form Init] Document name appeared/changed, setting initialization flag")
			isFormInitializing.value = true
			// Reset flag after form has time to update all fields
			setTimeout(() => {
				isFormInitializing.value = false
				console.log("[Form Init] Reload complete, clearing flag")
			}, 500)
		}
	},
	{ immediate: false }
)

// helper functions
function getFilteredFields(fields) {
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	const hasTechnicianRole = roles.includes("Technician")
	const currentState = serviceCall.value?.workflow_state || ""

	// For new documents (creation stage) - Service Manager only
	if (!props.id) {
		// Service Manager sees the 10 basic fields during creation
		// Also include address if available (it's fetched from branch)
		const allowedFields = [
			"naming_series",
			"date",
			"customer",
			"branch",
			"address",
			"contacted_person",
			"mobile_no",
			"email",
			"type",
			"special_instruction",
			"technician_list",
		]
		const filtered = fields.filter((field) => allowedFields.includes(field.fieldname))
		return filtered.sort((a, b) => {
			const indexA = allowedFields.indexOf(a.fieldname)
			const indexB = allowedFields.indexOf(b.fieldname)
			return indexA - indexB
		})
	}

	// For existing documents:
	if (hasTechnicianRole) {
		// Technician role:
		// - In "Assigned" state: show only 9 basic fields (no technician_list, no service details)
		// - After "Accept Call" (any other state): show ALL fields EXCEPT technician_list
		// - Technician List should NEVER be visible to Technician at any stage
		if (currentState === "Assigned") {
			const technicianBasicFields = [
				"naming_series",
				"date",
				"customer",
				"branch",
				"address",
				"contacted_person",
				"mobile_no",
				"email",
				"type",
				"special_instruction",
			]
			const filtered = fields.filter((field) =>
				technicianBasicFields.includes(field.fieldname)
			)
			return filtered.sort((a, b) => {
				const indexA = technicianBasicFields.indexOf(a.fieldname)
				const indexB = technicianBasicFields.indexOf(b.fieldname)
				return indexA - indexB
			})
		}

		// For all other states (after "Accept Call"), technician sees all fields EXCEPT technician_list
		// IMPORTANT: We must preserve the original field order and include ALL structural fields
		// (Section Break, Tab Break, Column Break) to ensure sections and tabs work correctly
		const filtered = fields.filter((field) => {
			// Always include structural fields (Section Break, Tab Break, Column Break)
			// These are needed for proper rendering of sections and tabs
			if (field.fieldtype === "Section Break" || 
			    field.fieldtype === "Tab Break" || 
			    field.fieldtype === "Column Break") {
				return true
			}
			// Exclude only technician_list
			return field.fieldname !== "technician_list"
		})
		
		// Ensure we preserve the original field order (filter already does this, but being explicit)
		return filtered
	} else {
		// Service Manager / Others:
		// - Once Service Call is created and assigned (any state after creation): show ALL fields
		// - This means after the document has an ID, Service Manager always sees all fields
		return fields
	}
}

function applyFilters(field) {
	// Apply link filters if needed
	if (field.fieldname === "contacted_person" && field.linkFilters) {
		// Link filters are already set in the doctype
	}
	
	return field
}
</script>

