<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col items-center my-7 p-4 gap-7">
				<CheckInPanel />
				<QuickLinks :items="quickLinks" :title="__('Quick Links')" />
				<RequestPanel />
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { inject, markRaw } from "vue"

import CheckInPanel from "@/components/CheckInPanel.vue"
import QuickLinks from "@/components/QuickLinks.vue"
import BaseLayout from "@/components/BaseLayout.vue"
import RequestPanel from "@/components/RequestPanel.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import ServiceCallIcon from "@/components/icons/ServiceCallIcon.vue"

const __ = inject("$translate")

const quickLinks = [
	{
		icon: markRaw(ServiceCallIcon),
		title: __("Service Call"),
		route: "ServiceCallMyAssignmentsView",
	},
	{
		icon: markRaw(ExpenseIcon),
		title: __("Claim an Expense"),
		route: "ExpenseClaimFormView",
	},
	{
		icon: markRaw(LeaveIcon),
		title: __("Apply Leave"),
		route: "LeaveApplicationFormView",
	},
	{
		icon: markRaw(AttendanceIcon),
		title: __("Mark Attendance"),
		route: "AttendanceRequestFormView",
	},
]
</script>
