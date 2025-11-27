<template>
	<div class="flex flex-col gap-1.5">
		<!-- Label -->
		<span
			:class="[
				props.reqd ? `after:content-['_*'] after:text-red-600` : ``,
				`block text-sm leading-5 text-gray-700`,
			]"
		>
			{{ __("Technician List") }}
		</span>

		<!-- Add Technician Dropdown -->
		<div v-if="!isReadOnly" class="flex flex-row items-center gap-2">
			<Autocomplete
				:key="selectedTechniciansList.length"
				:placeholder="__('Select Technician')"
				:options="availableTechnicians"
				:modelValue="null"
				:disabled="isReadOnly"
				@update:modelValue="addTechnician"
				class="flex-1"
			/>
		</div>

		<!-- Display selected technicians -->
		<div v-if="selectedTechniciansList.length > 0" class="flex flex-col gap-2 mt-2">
			<div
				v-for="(tech, idx) in selectedTechniciansList"
				:key="idx"
				class="flex flex-row items-center justify-between p-2 bg-gray-50 rounded border"
			>
				<div class="flex flex-col">
					<span class="text-sm font-medium text-gray-800">
						{{ tech.employee_name || tech.employee }}
					</span>
					<span class="text-xs text-gray-500">
						{{ tech.designation || "" }}
						<span v-if="tech.department" class="whitespace-pre"> &middot; {{ tech.department }}</span>
					</span>
				</div>
				<Button
					v-if="!isReadOnly"
					icon="x"
					variant="ghost"
					size="sm"
					@click="removeTechnician(idx)"
				/>
			</div>
		</div>
		<div v-else-if="!isReadOnly" class="text-sm text-gray-500 mt-1">
			{{ __("No technicians selected") }}
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue"
import { inject } from "vue"
import { Autocomplete, Button, createResource } from "frappe-ui"

const __ = inject("$translate")
const dayjs = inject("$dayjs")

const props = defineProps({
	modelValue: {
		type: Array,
		default: () => [],
	},
	reqd: {
		type: Boolean,
		default: false,
	},
	isReadOnly: {
		type: Boolean,
		default: false,
	},
})

const emit = defineEmits(["update:modelValue"])

// Fetch technicians (employees with department = "Technician - AA" and status = "Active")
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

// Get available technicians (excluding already selected ones)
const availableTechnicians = computed(() => {
	if (!techniciansResource.data) return []
	
	const selectedEmployeeIds = (props.modelValue || []).map((tech) => tech.employee)
	
	return techniciansResource.data
		.filter((emp) => !selectedEmployeeIds.includes(emp.name))
		.map((emp) => ({
			label: `${emp.employee_name || emp.first_name || emp.name} (${emp.name})`,
			value: emp.name,
			employee: emp,
		}))
})

// Track selected technicians
const selectedTechniciansList = computed(() => {
	return props.modelValue || []
})

// Add technician
function addTechnician(selected) {
	if (!selected || !selected.value) return
	
	const employeeData = techniciansResource.data.find((emp) => emp.name === selected.value)
	if (!employeeData) return
	
	// Check if already selected
	const existing = props.modelValue || []
	if (existing.some((tech) => tech.employee === employeeData.name)) {
		return
	}
	
	const newTechnician = {
		employee: employeeData.name,
		employee_name: employeeData.employee_name || employeeData.first_name || employeeData.name,
		designation: employeeData.designation || "",
		department: employeeData.department || "",
		data_jghu: employeeData.cell_number || "",
		date: dayjs().format("YYYY-MM-DD"),
	}
	
	const updated = [...existing, newTechnician]
	emit("update:modelValue", updated)
}

// Remove technician
function removeTechnician(idx) {
	const updated = [...selectedTechniciansList.value]
	updated.splice(idx, 1)
	emit("update:modelValue", updated)
}
</script>

