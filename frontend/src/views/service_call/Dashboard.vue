<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-7">
				<!-- Service Call Summary -->
				<ServiceCallSummary />

				<!-- Create Service Call Button (Service Manager / System Manager only) -->
				<div v-if="showCreateButton" class="w-full">
					<router-link
						:to="{ name: 'ServiceCallFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="w-full py-5 text-base"
						>
							{{ __("Create Service Call") }}
						</Button>
					</router-link>
				</div>

				<!-- All Service Calls List -->
				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("All Service Calls") }}</div>
					<RequestList
						:component="markRaw(ServiceCallItem)"
						:items="allServiceCalls.data"
						:addListButton="true"
						listButtonRoute="ServiceCallListView"
					/>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { markRaw, inject, computed } from "vue"

import BaseLayout from "@/components/BaseLayout.vue"
import ServiceCallSummary from "@/components/ServiceCallSummary.vue"
import RequestList from "@/components/RequestList.vue"
import ServiceCallItem from "@/components/ServiceCallItem.vue"
import { Button } from "frappe-ui"

import { allServiceCalls } from "@/data/service_calls"
import { userResource } from "@/data/user"

const __ = inject("$translate")

// Only allow Service Managers (and System Managers) to create Service Calls
const showCreateButton = computed(() => {
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	return roles.includes("Service Manager") || roles.includes("System Manager")
})
</script>

