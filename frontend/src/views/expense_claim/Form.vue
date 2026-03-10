<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields.data"
				doctype="Expense Claim"
				v-model="expenseClaim"
				:isSubmittable="true"
				:fields="formFields.data"
				:id="props.id"
				:tabbedView="true"
				:tabs="visibleTabs"
				:showAttachmentView="true"
				@validateForm="validateForm"
			>
				<!-- Child Tables -->
				<template #expenses="{ isFormReadOnly }">
					<ExpensesTable
						v-model:expenseClaim="expenseClaim"
						:currency="currency"
						:isReadOnly="isReadOnly || isFormReadOnly"
						@addExpenseItem="addExpenseItem"
						@updateExpenseItem="updateExpenseItem"
						@deleteExpenseItem="deleteExpenseItem"
					/>
				</template>
			</FormView>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent } from "@ionic/vue"
import { createResource } from "frappe-ui"
import { computed, ref, watch, inject } from "vue"

import FormView from "@/components/FormView.vue"
import ExpensesTable from "@/components/ExpensesTable.vue"

import { getCompanyCurrency } from "@/data/currencies"


const dayjs = inject("$dayjs")
const userResource = inject("$user")

const today = dayjs().format("YYYY-MM-DD")
const isReadOnly = ref(false)

const sessionEmployee = inject("$employee")
const currEmployee = ref(sessionEmployee.data.name)
const employeeCompany = ref(sessionEmployee.data.company)

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const tabs = [
	{ name: "Expenses", lastField: "expenses" },
	{ name: "Totals", lastField: "cost_center" },
]
const showTotalsTab = ref(Boolean(props.id))
const visibleTabs = computed(() =>
	showTotalsTab.value ? tabs : tabs.filter((tab) => tab.name !== "Totals")
)

// object to store form data
const expenseClaim = ref({
	employee: currEmployee,
	company: employeeCompany,
})

const currency = computed(() => getCompanyCurrency(expenseClaim.value.company))
const hasServiceManagerRole = computed(() => {
	const roles = Array.isArray(userResource?.data?.roles) ? userResource.data.roles : []
	return roles.includes("Service Manager")
})

// get form fields
const formFields = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Expense Claim" },
	transform(data) {
		let fields = getFilteredFields(data)

		const transformedFields = fields.map((field) => {
			if (field.fieldname === "posting_date") field.default = today
			return applyFilters(field)
		})

		syncConditionalFieldVisibility(transformedFields)
		return transformedFields
	},
	onSuccess(_data) {
		expenseApproverDetails.reload()
		companyDetails.reload()
	},
})
formFields.reload()

const expenseApproverDetails = createResource({
	url: "hrms.api.get_expense_approval_details",
	params: { employee: currEmployee.value },
	onSuccess(data) {
		setExpenseApprover(data)
	},
})

const companyDetails = createResource({
	url: "hrms.api.get_company_cost_center_and_expense_account",
	params: { company: expenseClaim.value.company },
	onSuccess(data) {
		expenseClaim.value.cost_center = data?.cost_center
		expenseClaim.value.payable_account =
			data?.default_expense_claim_payable_account
	},
})

// form scripts
watch(
	() => expenseClaim.value.employee,
	(employee_id) => {
		if (props.id && employee_id !== currEmployee.value) {
			// if employee is not the current user, set form as read only
			setFormReadOnly()
		}
		currEmployee.value = employee_id
		expenseApproverDetails.fetch({ employee: currEmployee.value })
	}
)
watch(
	() => expenseClaim.value.company,
	(company) => {
		employeeCompany.value = company
		companyDetails.fetch({ company: employeeCompany.value })
	}
)

watch(
	() => expenseClaim.value.cost_center,
	() => {
		expenseClaim?.value?.expenses?.forEach((expense) => {
			expense.cost_center = expenseClaim.value.cost_center
		})
	}
)

watch(
	() => expenseClaim.value.expenses?.length || 0,
	(length) => {
		if (length > 0) {
			showTotalsTab.value = true
		}
	}
)

watch(
	() => expenseClaim.value.is_paid,
	() => {
		syncConditionalFieldVisibility(formFields.data)
	}
)
watch(
	() => hasServiceManagerRole.value,
	() => {
		syncConditionalFieldVisibility(formFields.data)
	}
)

// helper functions
function getFilteredFields(fields) {
	// reduce noise from the form view by excluding unnecessary fields
	// and keep create/edit field visibility consistent.
	const excludeFields = [
		"naming_series",
		"task",
		"project",
		"taxes_and_charges_sb",
		"advance_payments_sb",
		"taxes",
		"advances",
		"total_taxes_and_charges",
		"total_advance_amount",
		"department",
		"remark",
		"clearance_date",
		"more_details",
		"status",
		"delivery_trip",
		"vehicle_log",
	]

	if (!props.id) {
		excludeFields.push(
			"transactions_section",
			"total_sanctioned_amount",
			"grand_total",
			"total_claimed_amount",
			"total_amount_reimbursed"
		)
	}

	return fields.filter((field) => !excludeFields.includes(field.fieldname))
}

function applyFilters(field) {
	if (field.fieldname === "payable_account") {
		field.linkFilters = {
			report_type: "Balance Sheet",
			account_type: "Payable",
			company: expenseClaim.value.company,
			is_group: 0,
		}
	} else if (field.fieldname === "cost_center") {
		field.linkFilters = {
			company: expenseClaim.value.company,
			is_group: 0,
		}
	}

	return field
}

function syncConditionalFieldVisibility(fields) {
	if (!fields?.length) return

	const modeOfPaymentField = fields.find((field) => field.fieldname === "mode_of_payment")
	if (modeOfPaymentField) {
		modeOfPaymentField.hidden = !Boolean(expenseClaim.value.is_paid)
	}

	const approvalStatusField = fields.find((field) => field.fieldname === "approval_status")
	if (approvalStatusField) {
		approvalStatusField.hidden = !hasServiceManagerRole.value
	}
}

function setExpenseApprover(data) {
	const expense_approver = formFields.data?.find(
		(field) => field.fieldname === "expense_approver"
	)
	if (!expense_approver) return

	const employeeName = data?.employee_name || expenseClaim.value.employee_name || currEmployee.value
	expense_approver.reqd = data?.is_mandatory
	expense_approver.documentList = (data?.department_approvers || []).map(
		(approver) => ({
			label: approver.full_name
				? `${approver.name} : ${approver.full_name}`
				: approver.name,
			value: approver.name,
		})
	)

	if (!data?.expense_approver) {
		expenseClaim.value.expense_approver = null
		frappe.msgprint(__("Please set the Expense Approver for the {0}", [employeeName]))
		return
	}

	expenseClaim.value.expense_approver = data?.expense_approver
	expenseClaim.value.expense_approver_name = data?.expense_approver_name
}

function addExpenseItem(item) {
	if (!expenseClaim.value.expenses) expenseClaim.value.expenses = []
	expenseClaim.value.expenses.push(item)
	calculateTotals()
}

function updateExpenseItem(item, idx) {
	expenseClaim.value.expenses[idx] = item
	calculateTotals()
}

function deleteExpenseItem(idx) {
	expenseClaim.value.expenses.splice(idx, 1)
	calculateTotals()
}

function calculateTotals() {
	let total_claimed_amount = 0
	let total_sanctioned_amount = 0

	expenseClaim.value?.expenses?.forEach((item) => {
		total_claimed_amount += parseFloat(item.amount)
		total_sanctioned_amount += parseFloat(item.sanctioned_amount)
	})

	expenseClaim.value.total_claimed_amount = total_claimed_amount
	expenseClaim.value.total_sanctioned_amount = total_sanctioned_amount
	calculateGrandTotal()
}

function calculateGrandTotal() {
	expenseClaim.value.grand_total = parseFloat(expenseClaim.value.total_sanctioned_amount || 0)
}

function setFormReadOnly() {
	if (props.id && expenseClaim.value.expense_approver !== currEmployee.value) return
	formFields.data.map((field) => (field.read_only = true))
	isReadOnly.value = true
}

function validateForm() {
	expenseClaim?.value?.expenses?.forEach((expense) => {
		expense.cost_center = expenseClaim.value.cost_center
	})
}
</script>
