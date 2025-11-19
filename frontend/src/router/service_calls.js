const routes = [
	{
		name: "ServiceCallListView",
		path: "/service-calls",
		component: () => import("@/views/service_call/List.vue"),
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

