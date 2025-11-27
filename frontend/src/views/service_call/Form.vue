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

				<!-- Child Tables - Only show for existing documents -->
				<template v-if="props.id" #table_whpt="{ isFormReadOnly }">
					<CashMemoTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>

				<template v-if="props.id" #reopen_call="{ isFormReadOnly }">
					<ReopenCallListTable
						v-model:serviceCall="serviceCall"
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
		
		return fieldCopy
	})
	
	return fields
})
formFieldsResource.reload()

// Watch for customer changes to clear dependent fields
watch(
	() => serviceCall.value.customer,
	(newCustomer, oldCustomer) => {
		console.log("[Customer Watcher] Customer changed:", { old: oldCustomer, new: newCustomer })
		if (newCustomer !== oldCustomer) {
			// Clear branch and contacted_person when customer changes
			serviceCall.value.branch = ""
			serviceCall.value.contacted_person = ""
			console.log("[Customer Watcher] Cleared branch and contacted_person")
		}
	},
	{ immediate: false }
)

// Watch for branch changes to clear dependent fields
watch(
	() => serviceCall.value.branch,
	(newBranch, oldBranch) => {
		console.log("[Branch Watcher] Branch changed:", { old: oldBranch, new: newBranch })
		if (newBranch !== oldBranch) {
			// Clear contacted_person when branch changes
			serviceCall.value.contacted_person = ""
			console.log("[Branch Watcher] Cleared contacted_person")
		}
	},
	{ immediate: false }
)

// helper functions
function getFilteredFields(fields) {
	// For new documents (first stage creation), only show specific fields
	if (!props.id) {
		const allowedFields = [
			"naming_series",
			"date",
			"customer",
			"branch",
			"contacted_person",
			"mobile_no",
			"email",
			"type",
			"special_instruction",
			"technician_list",
		]
		// Filter and sort fields to maintain correct order
		const filtered = fields.filter((field) => allowedFields.includes(field.fieldname))
		// Sort by the order in allowedFields array
		return filtered.sort((a, b) => {
			const indexA = allowedFields.indexOf(a.fieldname)
			const indexB = allowedFields.indexOf(b.fieldname)
			return indexA - indexB
		})
	}
	
	// For existing documents:
	// - Technician role:
	//    - When workflow_state = "Assigned": show only the 10 basic fields (no technician_list, no service details)
	//    - After "Accept Call" (but not "Close"): show all fields EXCEPT technician_list
	//    - When workflow_state = "Close": show only the 10 basic fields (no service details, no technician_list)
	// - Service Manager / Others:
	//    - When workflow_state = "Assigned": show ALL fields INCLUDING technician_list (can perform all actions)
	//    - When workflow_state = "Open": show only the 10 basic fields INCLUDING technician_list
	//    - When workflow_state = "Close": show ALL fields INCLUDING technician_list
	//    - Otherwise: show only the 10 basic fields INCLUDING technician_list
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	const hasTechnicianRole = roles.includes("Technician")
	const currentState = serviceCall.value?.workflow_state || ""

	if (hasTechnicianRole) {
		// In "Assigned" state, technician should see only the 10 basic fields (no service details, no technician dropdown)
		if (currentState === "Assigned") {
			const technicianBasicFields = [
				"naming_series",
				"date",
				"customer",
				"branch",
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

		// In "Close" state, technician should see only the 10 basic fields (no service details, no technician dropdown)
		if (currentState === "Close") {
			const technicianBasicFields = [
				"naming_series",
				"date",
				"customer",
				"branch",
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

		// For all other states (after "Accept Call", but not "Close"), 
		// technician sees all fields except technician_list
		return fields.filter((field) => field.fieldname !== "technician_list")
	} else {
		// Service Manager / Others: Check if state is "Assigned", "Open", or "Close"
		if (currentState === "Assigned") {
			// In "Assigned" state, show ALL fields including technician_list (Service Manager can perform all actions)
			return fields
		} else if (currentState === "Open") {
			// In "Open" state, show the same fields as first step (10 basic fields) with all data filled in
			const allowedFields = [
				"naming_series",
				"date",
				"customer",
				"branch",
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
		} else if (currentState === "Close") {
			// In "Close" state, show ALL fields including technician_list
			return fields
		} else {
			// Otherwise: only the basic fields including technician_list
			const allowedFields = [
				"naming_series",
				"date",
				"customer",
				"branch",
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

