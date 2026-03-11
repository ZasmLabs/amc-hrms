<template>
	<BaseLayout pageTitle="Attendance">
		<template #body>
			<div class="flex flex-col h-full p-4 pt-7 pb-7 overflow-hidden">
				<div class="flex flex-col gap-4 shrink-0">
					<div class="flex justify-end">
						<router-link :to="{ name: 'AttendanceHistoryListView' }" v-slot="{ navigate }">
							<div
								@click="navigate"
								class="text-sm text-gray-800 font-semibold cursor-pointer underline underline-offset-2"
							>
								{{ __("View Attendance History") }}
							</div>
						</router-link>
					</div>
					<div class="w-full">
						<router-link :to="{ name: 'AttendanceRequestFormView' }" v-slot="{ navigate }">
							<Button @click="navigate" variant="solid" class="w-full py-5 text-base">
								{{ __("Mark Attendance") }}
							</Button>
						</router-link>
					</div>
					<TabButtons v-if="isServiceManager" :buttons="TAB_BUTTONS" v-model="activeTab" />
					<div v-else class="text-lg text-gray-800 font-bold">
						{{ __("My Attendance Requests") }}
					</div>
				</div>
				<div class="flex-1 overflow-y-auto">
					<RequestList
						:component="markRaw(AttendanceRequestItem)"
						:items="activeItems"
						:teamRequests="isServiceManager && isTeamTab"
					/>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, markRaw, ref } from "vue"

import BaseLayout from "@/components/BaseLayout.vue"
import AttendanceRequestItem from "@/components/AttendanceRequestItem.vue"
import RequestList from "@/components/RequestList.vue"
import TabButtons from "@/components/TabButtons.vue"

import { myAttendanceRequests, teamAttendanceRequests } from "@/data/attendance"
import { userResource } from "@/data/user"

const __ = inject("$translate")
const TAB_BUTTONS = ["My Requests", "Team Requests"]
const activeTab = ref("My Requests")

const isServiceManager = computed(() => {
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	return roles.includes("Service Manager")
})

const isTeamTab = computed(() => activeTab.value === "Team Requests")
const activeItems = computed(() =>
	isServiceManager.value && isTeamTab.value
		? teamAttendanceRequests?.data
		: myAttendanceRequests?.data
)
</script>
