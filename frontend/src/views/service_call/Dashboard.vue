<template>
	<BaseLayout :pageTitle="__('Service Calls')">
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-7">
				<ServiceCallSummary />

				<div class="w-full">
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

				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("My Service Calls") }}</div>
					<RequestList
						:component="markRaw(ServiceCallItem)"
						:items="myServiceCalls.data"
						:addListButton="true"
						listButtonRoute="ServiceCallListView"
					/>
				</div>

				<div v-if="pendingServiceCalls.data && pendingServiceCalls.data.length > 0">
					<div class="text-lg text-gray-800 font-bold">{{ __("Pending Approvals") }}</div>
					<RequestList
						:component="markRaw(ServiceCallItem)"
						:items="pendingServiceCalls.data"
						:addListButton="true"
						listButtonRoute="ServiceCallListView"
					/>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { markRaw } from "vue"

import BaseLayout from "@/components/BaseLayout.vue"
import ServiceCallSummary from "@/components/ServiceCallSummary.vue"
import RequestList from "@/components/RequestList.vue"
import ServiceCallItem from "@/components/ServiceCallItem.vue"

import { myServiceCalls, pendingServiceCalls } from "@/data/service_calls"
</script>

