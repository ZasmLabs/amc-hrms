<template>
	<BaseLayout :pageTitle="__('Leaves & Holidays')">
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-5">
				<template v-if="isServiceManager">
					<router-link
						:to="{ name: 'LeaveApplicationFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="w-full py-5 text-base"
						>
							{{ __("Apply Leave") }}
						</Button>
					</router-link>

					<TabButtons
						:buttons="TAB_BUTTONS"
						v-model="activeTab"
					/>
					<RequestList
						:component="markRaw(LeaveRequestItem)"
						:items="activeItems"
						:teamRequests="isTeamTab"
					/>
				</template>

				<template v-else>
					<router-link
						:to="{ name: 'LeaveApplicationFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="w-full py-5 text-base"
						>
							{{ __("Apply Leave") }}
						</Button>
					</router-link>

					<div class="text-lg text-gray-800 font-bold">
						{{ __("My Recent Leaves") }}
					</div>
					<RequestList
						:component="markRaw(LeaveRequestItem)"
						:items="myLeaves.data"
					/>
				</template>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, markRaw, ref, watch } from "vue"
import { createResource } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import RequestList from "@/components/RequestList.vue"
import LeaveRequestItem from "@/components/LeaveRequestItem.vue"
import TabButtons from "@/components/TabButtons.vue"

import { myLeaves, getLeaveDates } from "@/data/leaves"
import { employeeResource } from "@/data/employee"
import { userResource } from "@/data/user"

const __ = inject("$translate")
const TAB_BUTTONS = ["My Leaves", "Team Leaves"]
const activeTab = ref("My Leaves")

const isServiceManager = computed(() => {
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	return roles.includes("Service Manager") || roles.includes("System Manager")
})

const isTeamTab = computed(() => activeTab.value === "Team Leaves")

const teamLeaves = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Leave Application",
		fields: [
			"name",
			"docstatus",
			"employee",
			"employee_name",
			"leave_type",
			"status",
			"from_date",
			"to_date",
			"total_leave_days",
			"creation",
		],
		filters: {
			employee: ["!=", employeeResource.data?.name],
			docstatus: ["!=", 2],
		},
		order_by: "creation desc",
		limit_page_length: 20,
	},
	transform(data) {
		return data.map((leave) => {
			leave.leave_dates = getLeaveDates(leave)
			leave.doctype = "Leave Application"
			return leave
		})
	},
	auto: false,
})

const activeItems = computed(() =>
	isServiceManager.value && isTeamTab.value ? teamLeaves.data : myLeaves.data
)

watch(
	() => [isServiceManager.value, isTeamTab.value],
	([canManageTeam, teamTabSelected]) => {
		if (canManageTeam && teamTabSelected && !teamLeaves.data) {
			teamLeaves.reload()
		}
	},
	{ immediate: true }
)
</script>
