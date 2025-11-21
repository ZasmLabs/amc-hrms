<template>
	<ion-tab-bar
		slot="bottom"
		class="bg-white shadow-md sm:w-96 py-2 pb-2 standalone:pb-safe-bottom"
	>
		<ion-tab-button
			v-for="item in filteredTabItems"
			:key="item.title"
			:tab="item.title"
			:href="item.route"
			:class="[
				'bg-white text-xs space-y-1.5 !hover:border-gray-300 !hover:text-gray-700 transition active:scale-95',
				route.path === item.route
					? 'border-gray-900 text-gray-800 font-semibold'
					: 'text-gray-600 font-normal',
			]"
		>
			<component :is="item.icon" class="h-5 w-5" />
			<div>{{ item.title }}</div>
		</ion-tab-button>
	</ion-tab-bar>
</template>

<script setup>
import { useRoute } from "vue-router"
import { computed, inject } from "vue"

import { IonTabBar, IonTabButton, IonLabel } from "@ionic/vue"

import HomeIcon from "@/components/icons/HomeIcon.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"
import ServiceCallIcon from "@/components/icons/ServiceCallIcon.vue"

const __ = inject("$translate")
const user = inject("$user")

const route = useRoute()

const allTabItems = [
	{
		icon: HomeIcon,
		title: __("Home"),
		route: "/home",
	},
	{
		icon: AttendanceIcon,
		title: __("Attendance"),
		route: "/dashboard/attendance",
	},
	{
		icon: LeaveIcon,
		title: __("Leaves"),
		route: "/dashboard/leaves",
	},
	{
		icon: ExpenseIcon,
		title: __("Expenses"),
		route: "/dashboard/expense-claims",
	},
	{
		icon: ServiceCallIcon,
		title: __("Service Call"),
		route: "/dashboard/service-calls",
		isServiceCall: true,
	},
]

// Filter tabs based on user roles
// Hide Service Call tab if user has "Technician" role but NOT "Service Manager" role
const filteredTabItems = computed(() => {
	// If user data is still loading, show all tabs
	if (user?.loading || !user?.data) {
		return allTabItems
	}

	const userRoles = Array.isArray(user.data?.roles) ? user.data.roles : []

	// Default behavior: show all tabs (including Service Call)
	// Hide Service Call tab ONLY if user has "Technician" role AND does NOT have "Service Manager" role
	const hasTechnicianRole = userRoles.includes("Technician")
	const hasServiceManagerRole = userRoles.includes("Service Manager")

	return allTabItems.filter((item) => {
		// If it's the Service Call tab, check role restrictions
		if (item.isServiceCall) {
			// Hide only if user has Technician role but NOT Service Manager role
			if (hasTechnicianRole && !hasServiceManagerRole) {
				return false
			}
		}
		// Show all other tabs
		return true
	})
})
</script>
