import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"

const transformServiceCallData = (data) => {
	return data.map((call) => {
		call.doctype = "Service Call"
		return call
	})
}

export const serviceCallSummary = createResource({
	url: "hrms.api.get_service_call_summary",
	params: () => ({
		employee: employeeResource.data?.name,
		technician: true,
	}),
	auto: true,
	cache: "hrms:service_call_summary",
})

export const myServiceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: () => ({
		employee: employeeResource.data?.name,
		technician: true,
		limit: 10,
	}),
	auto: true,
	cache: "hrms:my_service_calls",
	transform(data) {
		return transformServiceCallData(data)
	},
	onSuccess() {
		serviceCallSummary.reload()
	},
})

export const allServiceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: {
		limit: 10,
	},
	auto: true,
	cache: "hrms:all_service_calls",
	transform(data) {
		return transformServiceCallData(data)
	},
	onSuccess() {
		serviceCallSummary.reload()
	},
})

export const pendingServiceCalls = createResource({
	url: "hrms.api.get_service_calls",
	params: () => ({
		employee: employeeResource.data?.name,
		for_approval: true,
		limit: 10,
	}),
	auto: true,
	cache: "hrms:pending_service_calls",
	transform(data) {
		return transformServiceCallData(data)
	},
})

