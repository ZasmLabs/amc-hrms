const routes = [
	{
		name: "ServiceCallListView",
		path: "/service-calls",
		component: () => import("@/views/service_call/List.vue"),
	},
	{
		name: "ServiceCallMyAssignmentsView",
		path: "/service-calls/my-assignments",
		component: () => import("@/views/service_call/MyAssignments.vue"),
	},
	{
		name: "ServiceCallFormView",
		path: "/service-calls/new",
		component: () => import("@/views/service_call/Form.vue"),
	},
	{
		name: "ServiceCallDetailView",
		path: "/service-calls/:id",
		props: true,
		component: () => import("@/views/service_call/Form.vue"),
	},
]

export default routes

