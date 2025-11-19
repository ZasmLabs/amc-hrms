<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields.data"
				doctype="Service Call"
				v-model="serviceCall"
				:isSubmittable="true"
				:fields="formFields.data"
				:id="props.id"
				:tabbedView="tabs && tabs.length > 0"
				:tabs="tabs"
				:showAttachmentView="true"
			>
				<!-- Child Tables - Optional custom implementations -->
				<template #technician_list="{ isFormReadOnly }">
					<TechnicianListTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>

				<template #table_whpt="{ isFormReadOnly }">
					<CashMemoTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>

				<template #reopen_call="{ isFormReadOnly }">
					<ReopenCallListTable
						v-model:serviceCall="serviceCall"
						:isReadOnly="isFormReadOnly"
					/>
				</template>
			</FormView>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent } from "@ionic/vue"
import { createResource } from "frappe-ui"
import { ref, computed } from "vue"
import { inject } from "vue"

import FormView from "@/components/FormView.vue"
import TechnicianListTable from "@/components/TechnicianListTable.vue"
import CashMemoTable from "@/components/CashMemoTable.vue"
import ReopenCallListTable from "@/components/ReopenCallListTable.vue"

const __ = inject("$translate")
const dayjs = inject("$dayjs")

const today = dayjs().format("YYYY-MM-DD")

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const tabs = computed(() => {
	const tabList = []
	if (formFields.data) {
		// Find tab fields
		const serviceReportTab = formFields.data.find((f) => f.fieldname === "service_request_form_tab")
		const cashMemoTab = formFields.data.find((f) => f.fieldname === "cash_memo_tab")
		const reopenLogTab = formFields.data.find((f) => f.fieldname === "reopen_log_tab")

		if (serviceReportTab) {
			tabList.push({ name: "Service Report", lastField: "customer_sign" })
		}
		if (cashMemoTab) {
			tabList.push({ name: "Cash Memo", lastField: "table_whpt" })
		}
		if (reopenLogTab) {
			tabList.push({ name: "Reopen Log", lastField: "reopen_call" })
		}
	}
	return tabList.length > 0 ? tabList : null
})

// object to store form data
const serviceCall = ref({
	date: today,
	service_date: today,
})

// get form fields
const formFields = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Service Call" },
	transform(data) {
		return getFilteredFields(data).map((field) => {
			if (field.fieldname === "date" || field.fieldname === "service_date") {
				field.default = today
			}
			return applyFilters(field)
		})
	},
})
formFields.reload()

// helper functions
function getFilteredFields(fields) {
	// Exclude unnecessary fields
	const excludeFields = ["amended_from"]
	
	// For new documents, exclude some read-only fields
	if (!props.id) {
		excludeFields.push("workflow_state")
	}

	return fields.filter((field) => !excludeFields.includes(field.fieldname))
}

function applyFilters(field) {
	// Apply link filters if needed
	if (field.fieldname === "contacted_person" && field.linkFilters) {
		// Link filters are already set in the doctype
	}
	
	return field
}
</script>

