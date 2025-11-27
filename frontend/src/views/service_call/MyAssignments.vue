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
							{{ __("My Assignments") }}
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
						class="flex flex-col bg-white rounded-lg shadow-sm mt-6"
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
import { inject, ref, watch, onMounted } from "vue"
import { FeatherIcon, createResource, LoadingIndicator, Button } from "frappe-ui"

import ServiceCallItem from "@/components/ServiceCallItem.vue"
import EmptyState from "@/components/EmptyState.vue"
import { employeeResource } from "@/data/employee"
import useWorkflow from "@/composables/workflow"

const __ = inject("$translate")
const router = useRouter()
const workflowStateField = ref(null)

// Service Calls resource - only fetch assigned calls
const serviceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: () => {
		// Get employee name - this should always be available when reload() is called
		// because loadServiceCalls() verifies it first
		const employeeName = employeeResource.data?.name
		
		// This should never happen if loadServiceCalls() is working correctly,
		// but we add this check to prevent fetching all service calls
		if (!employeeName) {
			// Return params that will result in no results (empty list from API)
			// The API will return empty because technician=True but employee is missing
			return {
				employee: null,
				technician: true,
				limit: 50,
			}
		}
		
		return {
			employee: employeeName,
			technician: true,
			limit: 50,
		}
	},
	auto: false, // Don't auto-load, we'll trigger it manually after checking employee data
	transform(data) {
		// Additional frontend filtering as safety measure
		// Filter to only show service calls where logged-in employee is in technicians array
		const employeeName = employeeResource.data?.name
		if (employeeName && data) {
			return data.filter((call) => {
				// Must have technicians array and it must not be empty
				if (!call.technicians || call.technicians.length === 0) {
					return false
				}
				
				// Check if logged-in employee is in technicians
				return call.technicians.some(
					(tech) => tech.employee === employeeName
				)
			})
		}
		
		return data
	},
})

// Watch for employee resource to be loaded
watch(
	() => employeeResource.data?.name,
	(newName) => {
		if (newName) {
			loadServiceCalls()
		}
	}
)

// Function to load service calls only when employee data is available
function loadServiceCalls() {
	const employeeName = employeeResource.data?.name
	if (!employeeName) {
		return
	}
	
	// Double-check that employee data is still available before calling reload
	// The params function will be called during reload
	serviceCalls.reload()
}

// Handle refresh
function handleRefresh(event) {
	setTimeout(() => {
		loadServiceCalls()
		event.target.complete()
	}, 500)
}

// Get workflow state field and load service calls
onMounted(async () => {
	const workflow = useWorkflow("Service Call")
	await workflow.workflowDoc.promise
	if (workflow.workflowDoc.data) {
		workflowStateField.value = workflow.getWorkflowStateField()
	}
	
	// Wait for employee resource before loading service calls
	await employeeResource.promise
	
	// Verify employee data is available before loading
	if (employeeResource.data?.name) {
		loadServiceCalls()
	}
})
</script>

