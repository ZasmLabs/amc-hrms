<template>
	<ListItem
		:isTeamRequest="props.isTeamRequest"
		:employee="props.doc.employee"
		:employeeName="props.doc.employee_name"
	>
		<template #left>
			<AttendanceIcon class="h-5 w-5 text-gray-500" />
			<div class="flex flex-col items-start gap-1.5">
				<div class="text-base font-normal text-gray-800">
					{{ __(props.doc.status) }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					<span>{{ attendanceDate }}</span>
					<span v-if="props.doc.shift" class="whitespace-pre"> &middot; {{ props.doc.shift }}</span>
				</div>
			</div>
		</template>
		<template #right>
			<Badge variant="outline" :theme="statusTheme" :label="__(props.doc.status)" size="md" />
			<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
		</template>
	</ListItem>
</template>

<script setup>
import { computed, inject } from "vue"
import { Badge, FeatherIcon } from "frappe-ui"

import ListItem from "@/components/ListItem.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"

const dayjs = inject("$dayjs")
const __ = inject("$translate")

const props = defineProps({
	doc: {
		type: Object,
	},
	isTeamRequest: {
		type: Boolean,
		default: false,
	},
})

const attendanceDate = computed(() => dayjs(props.doc.attendance_date).format("D MMM YYYY"))

const statusTheme = computed(() => {
	const map = {
		Present: "green",
		Absent: "red",
		"On Leave": "blue",
		"Half Day": "orange",
		"Work From Home": "purple",
	}
	return map[props.doc.status] || "gray"
})
</script>
