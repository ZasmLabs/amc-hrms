<template>
	<ion-page>
		<ion-header class="ion-no-border">
			<div class="w-full sm:w-96">
				<div
					class="flex flex-row bg-white shadow-sm py-4 px-3 items-center justify-between border-b"
				>
					<div class="flex flex-row items-center">
						<Button variant="ghost" class="!px-1 mr-1 hover:bg-white" @click="router.back()">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>
						<h2 class="text-xl font-semibold text-gray-900">
							{{ __("Service Calls") }}
						</h2>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content>
			<ion-refresher slot="fixed" @ionRefresh="handleRefresh($event)">
				<ion-refresher-content></ion-refresher-content>
			</ion-refresher>

			<div
				class="flex flex-col items-center mb-7 p-4 h-full w-full sm:w-96 overflow-y-auto"
			>
				<div class="w-full">
					<div
						class="flex flex-col bg-white rounded-lg shadow-sm mt-5"
						v-if="!serviceCalls.loading && serviceCalls.data?.length"
					>
						<router-link
							v-for="call in serviceCalls.data"
							:key="call.name"
							:to="{ name: 'ServiceCallDetailView', params: { id: call.name } }"
							v-slot="{ navigate }"
							class="block"
						>
							<div class="px-5 py-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors last:border-b-0">
								<ServiceCallItem
									:doc="call"
									:isTeamRequest="false"
									:workflowStateField="workflowStateField"
									@click="navigate"
								/>
							</div>
						</router-link>
					</div>
					<EmptyState
						:message="__('No service call found')"
						v-else-if="!serviceCalls.loading"
					/>

					<div v-if="serviceCalls.loading" class="flex mt-2 items-center justify-center">
						<LoadingIndicator class="w-8 h-8 text-gray-800" />
					</div>
				</div>
			</div>

		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonHeader, IonContent, IonRefresher, IonRefresherContent } from "@ionic/vue"
import { useRouter } from "vue-router"
import { inject, ref, onMounted } from "vue"
import { FeatherIcon, createResource, LoadingIndicator, Button } from "frappe-ui"

import ServiceCallItem from "@/components/ServiceCallItem.vue"
import EmptyState from "@/components/EmptyState.vue"
import useWorkflow from "@/composables/workflow"

const __ = inject("$translate")
const router = useRouter()
const workflowStateField = ref(null)

// Service Calls resource - fetch all service calls
const serviceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: () => ({
		limit: 50,
	}),
	auto: true,
	transform(data) {
		// Filter out Completed and Annulled workflow states
		if (!data) return data
		return data.filter((call) => {
			const workflowState = call.workflow_state || call.status || ""
			return workflowState !== "Completed" && workflowState !== "Annulled"
		})
	},
})

// Handle refresh
function handleRefresh(event) {
	setTimeout(() => {
		serviceCalls.reload()
		event.target.complete()
	}, 500)
}

// Get workflow state field
onMounted(async () => {
	const workflow = useWorkflow("Service Call")
	await workflow.workflowDoc.promise
	if (workflow.workflowDoc.data) {
		workflowStateField.value = workflow.getWorkflowStateField()
	}
})
</script>

