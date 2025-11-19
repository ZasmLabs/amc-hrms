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
							{{ isMyAssignmentsView ? __("My Assignments") : __("Service Calls") }}
						</h2>
					</div>

					<div class="flex flex-row gap-2" v-if="!isMyAssignmentsView">
						<Button
							id="show-filter-modal"
							icon="filter"
							variant="subtle"
							:class="[
								areFiltersApplied
									? '!border !border-gray-800 !bg-white !text-gray-900 !font-semibold'
									: '',
							]"
						/>
						<router-link
							:to="{ name: 'ServiceCallFormView' }"
							v-slot="{ navigate }"
						>
							<Button variant="solid" class="mr-2" @click="navigate">
								<template #prefix>
									<FeatherIcon name="plus" class="w-4" />
								</template>
								{{ __("New") }}
							</Button>
						</router-link>
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
					<TabButtons
						v-if="!isMyAssignmentsView"
						class="mt-5"
						:buttons="TAB_BUTTONS"
						v-model="activeTab"
					/>

					<div
						:class="[
							'flex flex-col bg-white rounded-lg shadow-sm',
							isMyAssignmentsView ? 'mt-6' : 'mt-5'
						]"
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

			<CustomIonModal v-if="!isMyAssignmentsView" trigger="show-filter-modal">
				<template #actionSheet>
					<ListFiltersActionSheet
						:filterConfig="FILTER_CONFIG"
						@applyFilters="applyFilters"
						@clearFilters="clearFilters"
						v-model:filters="filterMap"
					/>
				</template>
			</CustomIonModal>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonHeader, IonContent, IonRefresher, IonRefresherContent } from "@ionic/vue"
import { useRouter, useRoute } from "vue-router"
import { inject, ref, reactive, watch, computed, onMounted } from "vue"
import { FeatherIcon, createResource, LoadingIndicator, Button } from "frappe-ui"

import TabButtons from "@/components/TabButtons.vue"
import ServiceCallItem from "@/components/ServiceCallItem.vue"
import EmptyState from "@/components/EmptyState.vue"
import ListFiltersActionSheet from "@/components/ListFiltersActionSheet.vue"
import CustomIonModal from "@/components/CustomIonModal.vue"
import { employeeResource } from "@/data/employee"
import useWorkflow from "@/composables/workflow"

const __ = inject("$translate")
const router = useRouter()
const route = useRoute()

const TAB_BUTTONS = [__("All Service Calls"), __("My Assignments")]
// Initialize activeTab based on query parameter, default to first tab
// Check if query param matches the second tab (My Assignments)
const initialTab = route.query.tab === "My Assignments" || route.query.tab === TAB_BUTTONS[1] 
	? TAB_BUTTONS[1] 
	: TAB_BUTTONS[0]
const activeTab = ref(initialTab)
const areFiltersApplied = ref(false)
const filterMap = reactive({})
const workflowStateField = ref(null)

// Check if we're on the "My Assignments" view
const isMyAssignmentsView = computed(() => {
	return activeTab.value === TAB_BUTTONS[1] || route.query.tab === "My Assignments" || route.query.tab === TAB_BUTTONS[1]
})

const SERVICE_CALL_FIELDS = [
	"name",
	"date",
	"customer",
	"contacted_person",
	"mobile_no",
	"type",
	"address",
	"service_date",
	"workflow_state",
	"docstatus",
	"creation",
]

const FILTER_CONFIG = [
	{
		fieldname: "workflow_state",
		fieldtype: "Select",
		label: "Status",
		options: ["Open", "Assigned", "Accepted", "On Site", "Spare needed", "Close", "Reopen"],
	},
	{
		fieldname: "type",
		fieldtype: "Select",
		label: "Type",
		options: ["Preventive maintenance", "Breakdown", "Installation"],
	},
	{
		fieldname: "customer",
		fieldtype: "Link",
		label: "Customer",
		options: "Customer",
	},
	{
		fieldname: "date",
		fieldtype: "Date",
		label: "Date",
	},
	{
		fieldname: "service_date",
		fieldtype: "Date",
		label: "Service Date",
	},
]

// Initialize filters
function initializeFilters() {
	FILTER_CONFIG.forEach((filter) => {
		filterMap[filter.fieldname] = {
			condition: "=",
			value: null,
		}
	})
}
initializeFilters()

// Service Calls resource
const serviceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: () => {
		const isMyAssignments = activeTab.value === TAB_BUTTONS[1] || route.query.tab === "My Assignments" || route.query.tab === TAB_BUTTONS[1]
		const params = {
			limit: 50,
		}
		
		// For "My Assignments" tab, filter by technician
		if (isMyAssignments) {
			params.employee = employeeResource.data?.name
			params.technician = true
		}
		
		// Apply custom filters
		const filters = []
		for (const fieldname in filterMap) {
			const condition = filterMap[fieldname].condition
			const value = filterMap[fieldname].value
			if (value && condition) {
				// Note: We'll need to handle filtering on the backend
				// For now, we'll pass filter info if needed
			}
		}
		
		return params
	},
	auto: true,
	transform(data) {
		// Apply client-side filtering if needed
		let filtered = data || []
		
		for (const fieldname in filterMap) {
			const condition = filterMap[fieldname].condition
			const value = filterMap[fieldname].value
			if (value && condition) {
				if (condition === "=") {
					filtered = filtered.filter((doc) => doc[fieldname] === value)
				} else if (condition === "!=") {
					filtered = filtered.filter((doc) => doc[fieldname] !== value)
				}
			}
		}
		
		return filtered
	},
})

// Watch for tab changes
watch(
	() => activeTab.value,
	() => {
		serviceCalls.reload()
	}
)

// Handle refresh
function handleRefresh(event) {
	setTimeout(() => {
		serviceCalls.reload()
		event.target.complete()
	}, 500)
}

// Apply filters
function applyFilters() {
	serviceCalls.reload()
	areFiltersApplied.value = Object.values(filterMap).some(
		(filter) => filter.value !== null && filter.value !== ""
	)
}

// Clear filters
function clearFilters() {
	initializeFilters()
	serviceCalls.reload()
	areFiltersApplied.value = false
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

