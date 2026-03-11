<template>
	<ListItem
		:isTeamRequest="props.isTeamRequest"
		:employee="props.doc.employee"
		:employeeName="props.doc.employee_name"
	>
		<template #left>
			<LeaveIcon class="h-5 w-5 text-gray-500" />
			<div class="flex flex-col items-start gap-1.5">
				<div class="text-base font-normal text-gray-800">
					{{ __(props.doc.leave_type, null, "Leave Type") }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					<span>{{ props.doc.leave_dates || getLeaveDates(props.doc) }}</span>
					<span class="whitespace-pre"> &middot; </span>
					<span class="whitespace-nowrap">{{ __("{0}d", [props.doc.total_leave_days]) }}</span>
				</div>
			</div>
		</template>
		<template #right>
			<Badge variant="outline" :theme="colorMap[status]" :label="__(status, null, 'Leave Application')" size="md" />
			<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
		</template>
	</ListItem>
</template>

<script setup>
import { computed } from "vue"
import { FeatherIcon, Badge } from "frappe-ui"

import ListItem from "@/components/ListItem.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import { getLeaveDates } from "@/data/leaves"

const props = defineProps({
	doc: {
		type: Object,
	},
	isTeamRequest: {
		type: Boolean,
		default: false,
	},
	workflowStateField: {
		type: String,
		required: false,
	},
})

const status = computed(() => {
	const explicitStatus = props.workflowStateField
		? props.doc[props.workflowStateField]
		: props.doc.status

	if (explicitStatus) return explicitStatus

	if (props.doc.docstatus === 1) return "Submitted"
	if (props.doc.docstatus === 2) return "Cancelled"
	return "Draft"
})

const colorMap = {
	Approved: "green",
	Rejected: "red",
	Open: "orange",
	Submitted: "blue",
	Cancelled: "red",
	Draft: "gray",
}
</script>
