<template>
	<ListItem
		:isTeamRequest="props.isTeamRequest"
		:employee="props.doc.technicians?.[0]?.employee"
		:employeeName="props.doc.technicians?.[0]?.employee_name"
	>
		<template #left>
			<ServiceCallIcon class="h-5 w-5 text-gray-500" />
			<div class="flex flex-col items-start gap-1.5">
				<div class="text-base font-normal text-gray-800">
					{{ serviceCallTitle }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					<span>{{ customerName }}</span>
					<span v-if="serviceDate" class="whitespace-pre"> &middot; </span>
					<span v-if="serviceDate" class="whitespace-nowrap">
						{{ serviceDate }}
					</span>
				</div>
			</div>
		</template>
		<template #right>
			<Badge 
				variant="outline" 
				:theme="statusMap[status]" 
				:label="__(status, null, 'Service Call')" 
				size="md" 
			/>
			<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
		</template>
	</ListItem>
</template>

<script setup>
import { FeatherIcon, Badge } from "frappe-ui"
import { computed, inject } from "vue"

import ListItem from "@/components/ListItem.vue"
import ServiceCallIcon from "@/components/icons/ServiceCallIcon.vue"

const dayjs = inject("$dayjs")
const __ = inject("$translate")

const props = defineProps({
	doc: {
		type: Object,
		required: true,
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

const statusMap = {
	Open: "gray",
	Assigned: "blue",
	Accepted: "blue",
	"On Site": "orange",
	"Spare needed": "yellow",
	Close: "green",
	Reopen: "red",
}

const status = computed(() => {
	if (props.workflowStateField) {
		return props.doc[props.workflowStateField] || "Open"
	}
	return props.doc.workflow_state || "Open"
})

const serviceCallTitle = computed(() => {
	return `${props.doc.type || "Service Call"} - ${props.doc.name || ""}`
})

const customerName = computed(() => {
	return props.doc.customer || ""
})

const serviceDate = computed(() => {
	if (props.doc.service_date) {
		return dayjs(props.doc.service_date).format("D MMM")
	} else if (props.doc.date) {
		return dayjs(props.doc.date).format("D MMM")
	}
	return null
})
</script>

