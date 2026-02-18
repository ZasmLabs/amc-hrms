<template>
	<BaseLayout :pageTitle="__('Expenses')">
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-5">
				<div class="w-full">
					<router-link
						:to="{ name: 'ExpenseClaimFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="w-full py-5 text-base"
						>
							{{ __("Claim an Expense") }}
						</Button>
					</router-link>
				</div>

				<TabButtons
					:buttons="TAB_BUTTONS"
					v-model="activeTab"
				/>

				<div v-if="isLoading" class="flex items-center justify-center py-8">
					<LoadingIndicator class="w-8 h-8 text-gray-800" />
				</div>

				<template v-else>
					<div
						class="flex flex-col bg-white rounded"
						v-if="activeItems?.length"
					>
						<router-link
							v-for="item in activeItems"
							:key="item.name"
							:to="{ name: 'ExpenseClaimDetailView', params: { id: item.name } }"
							v-slot="{ navigate }"
						>
							<div
								class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
								@click="navigate"
							>
								<ExpenseClaimItem
									:doc="item"
									:isTeamRequest="isTeamTab"
								/>
							</div>
						</router-link>
					</div>
					<EmptyState
						:message="__('No expenses found')"
						v-else
					/>
				</template>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue"
import { createResource, LoadingIndicator } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import TabButtons from "@/components/TabButtons.vue"
import ExpenseClaimItem from "@/components/ExpenseClaimItem.vue"

import { myClaims } from "@/data/claims"
import { employeeResource } from "@/data/employee"
import { userResource } from "@/data/user"

const __ = inject("$translate")

const TAB_BUTTONS = ["My Expenses", "Team Expenses"]
const activeTab = ref("My Expenses")

const isTeamTab = computed(() => activeTab.value === "Team Expenses")

const isServiceManager = computed(() => {
	const roles = Array.isArray(userResource.data?.roles) ? userResource.data.roles : []
	return roles.includes("Service Manager") || roles.includes("System Manager")
})

const teamExpenses = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Expense Claim",
		fields: [
			"name", "employee", "employee_name", "approval_status",
			"status", "expense_approver", "total_claimed_amount",
			"posting_date", "company",
		],
		filters: {
			employee: ["!=", employeeResource.data?.name],
			docstatus: ["!=", 2],
		},
		order_by: "posting_date desc",
		limit_page_length: 50,
	},
	transform(data) {
		return data.map((claim) => {
			claim.doctype = "Expense Claim"
			return claim
		})
	},
})

watch(isTeamTab, (val) => {
	if (val && isServiceManager.value && !teamExpenses.data) {
		teamExpenses.fetch()
	}
})

const isLoading = computed(() => {
	if (isTeamTab.value && isServiceManager.value) {
		return teamExpenses.loading
	}
	return false
})

const activeItems = computed(() => {
	if (isTeamTab.value) {
		return isServiceManager.value ? teamExpenses.data : []
	}
	return myClaims.data
})
</script>
