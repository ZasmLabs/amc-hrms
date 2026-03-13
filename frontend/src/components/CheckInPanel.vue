<template>
	<div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
		<h2 class="text-lg font-bold text-gray-900">
			{{ __("Hey, {0} 👋", [employee?.data?.first_name]) }}
		</h2>

		<template v-if="settings.data?.allow_employee_checkin_from_mobile_app">
			<div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
				<span>
					{{ __("Last {0} was at {1}", [__(lastLogType), formatTimestamp(lastLog.time || lastLog.creation)]) }}
				</span>
				<span class="whitespace-pre"> &middot; </span>
				<router-link :to="{ name: 'EmployeeCheckinListView' }" v-slot="{ navigate }">
					<span @click="navigate" class="underline">View List</span>
				</router-link>
			</div>
			<Button
				class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
				id="open-checkin-modal"
				@click="handleEmployeeCheckin"
			>
				<template #prefix>
					<FeatherIcon
						:name="nextAction.action === 'IN' ? 'arrow-right-circle' : 'arrow-left-circle'"
						class="w-4"
					/>
				</template>
				{{ nextAction.label }}
			</Button>
		</template>

		<div v-else class="font-medium text-sm text-gray-500 mt-1.5">
			{{ dayjs().format("ddd, D MMMM, YYYY") }}
		</div>
	</div>

	<ion-modal
		v-if="settings.data?.allow_employee_checkin_from_mobile_app"
		ref="modal"
		trigger="open-checkin-modal"
		:initial-breakpoint="1"
		:breakpoints="[0, 1]"
		@didDismiss="onModalDismiss"
	>
		<div class="h-120 w-full flex flex-col items-center justify-center gap-5 p-4 mb-5">
			<div class="flex flex-col gap-1.5 mt-2 items-center justify-center">
				<div class="font-bold text-xl">
					{{ dayjs(checkinTimestamp).format("hh:mm:ss a") }}
				</div>
				<div class="font-medium text-gray-500 text-sm">
					{{ dayjs().format("D MMM, YYYY") }}
				</div>
			</div>

			<template v-if="settings.data?.allow_geolocation_tracking">
				<span v-if="locationStatus" class="font-medium text-gray-500 text-sm">
					{{ locationStatus }}
				</span>

				<div
					v-if="latitude !== null && longitude !== null"
					class="rounded border-4 translate-z-0 block overflow-hidden w-full h-170"
				>
					<iframe
						width="100%"
						height="170"
						frameborder="0"
						scrolling="no"
						marginheight="0"
						marginwidth="0"
						style="border: 0"
						:src="`https://maps.google.com/maps?q=${latitude},${longitude}&hl=en&z=15&amp;output=embed`"
					>
					</iframe>
				</div>
			</template>

			<Button
				:loading="checkins.insert.loading || isSubmitting"
				variant="solid"
				class="w-full py-5 text-sm disabled:bg-gray-700"
				@click="submitLog"
			>
				{{ __("Confirm {0}", [selectedAction.label]) }}
			</Button>
		</div>
	</ion-modal>
</template>

<script setup>
import { createResource, createListResource, toast, FeatherIcon } from "frappe-ui"
import { computed, inject, ref, onMounted, onBeforeUnmount, watch } from "vue"
import { IonModal, modalController } from "@ionic/vue"

import { formatTimestamp } from "@/utils/formatters"

const DOCTYPE = "Employee Checkin"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const __ = inject("$translate")
const checkinTimestamp = ref(null)
const latitude = ref(null)
const longitude = ref(null)
const locationStatus = ref("")
const isSubmitting = ref(false)
const selectedAction = ref({ action: "IN", label: __("Check In") })
const optimisticLastLog = ref(null)
const serverLastLog = ref(null)
const settings = createResource({
	url: "hrms.api.get_hr_settings",
	auto: true,
})

const checkins = createListResource({
	doctype: DOCTYPE,
	fields: ["name", "employee", "employee_name", "log_type", "time", "creation", "device_id"],
	filters: {},
	orderBy: "time desc",
})

const latestCheckin = createResource({
	url: "frappe.client.get_list",
})

const getActionForLastLog = (logType) => {
	return logType === "IN"
		? { action: "OUT", label: __("Check Out") }
		: { action: "IN", label: __("Check In") }
}

const reloadCheckins = () => {
	const employeeName = employee?.data?.name
	if (!employeeName) return
	checkins.filters.employee = employeeName
	checkins.reload()
	return latestCheckin
		.submit({
			doctype: DOCTYPE,
			fields: ["name", "log_type", "time", "creation"],
			filters: {
				employee: employeeName,
				docstatus: ["!=", 2],
			},
			order_by: "time desc",
			limit_page_length: 1,
		})
		.then((data) => {
			serverLastLog.value = Array.isArray(data) && data.length ? data[0] : null
			return serverLastLog.value
		})
		.catch(() => {
			return serverLastLog.value
		})
}

const lastLog = computed(() => {
	if (optimisticLastLog.value) return optimisticLastLog.value
	return serverLastLog.value
})

const lastLogType = computed(() => {
	return lastLog?.value?.log_type === "IN" ? "check-in" : "check-out"
})

const nextAction = computed(() => {
	return getActionForLastLog(lastLog?.value?.log_type)
})

function handleLocationSuccess(position) {
	latitude.value = position.coords.latitude
	longitude.value = position.coords.longitude

	locationStatus.value = [
		__("Latitude: {0}°", [Number(latitude.value).toFixed(5)]),
		__("Longitude: {0}°", [Number(longitude.value).toFixed(5)]),
	].join(", ")
}

function handleLocationError(error) {
	locationStatus.value = "Unable to retrieve your location"
	if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
	if (!navigator.geolocation) {
		locationStatus.value = __("Geolocation is not supported by your current browser")
	} else {
		locationStatus.value = __("Locating...")
		navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError)
	}
}

const handleEmployeeCheckin = () => {
	checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
	selectedAction.value = { ...nextAction.value }
	latitude.value = null
	longitude.value = null
	locationStatus.value = ""

	if (settings.data?.allow_geolocation_tracking) {
		fetchLocation()
	}
}

const onModalDismiss = () => {
	isSubmitting.value = false
	locationStatus.value = ""
	latitude.value = null
	longitude.value = null
}

const submitLog = async () => {
	if (isSubmitting.value || checkins.insert.loading) return

	if (!employee?.data?.name) {
		toast({
			title: __("Error"),
			text: __("Employee not loaded. Please try again."),
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
		return
	}

	if (settings.data?.allow_geolocation_tracking && !(latitude.value || longitude.value)) {
		toast({
			title: __("Location Required"),
			text: __("Please wait for location to be detected before confirming."),
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
		return
	}

	isSubmitting.value = true
	const latestLog = await reloadCheckins()
	const resolvedAction = getActionForLastLog(latestLog?.log_type)
	selectedAction.value = resolvedAction
	const logType = resolvedAction.action
	const actionLabel = logType === "IN" ? __("Check-in") : __("Check-out")
	const submitTimestamp = dayjs().format("YYYY-MM-DD HH:mm:ss")

	checkins.insert.submit(
		{
			employee: employee.data.name,
			log_type: logType,
			time: submitTimestamp,
			latitude: latitude.value,
			longitude: longitude.value,
		},
		{
			onSuccess() {
				optimisticLastLog.value = {
					log_type: logType,
					time: submitTimestamp,
					creation: submitTimestamp,
				}
				isSubmitting.value = false
				reloadCheckins().finally(() => {
					optimisticLastLog.value = null
				})
				modalController.dismiss()
				toast({
					title: __("Success"),
					text: __("{0} successful!", [actionLabel]),
					icon: "check-circle",
					position: "bottom-center",
					iconClasses: "text-green-500",
				})
			},
			onError(error) {
				isSubmitting.value = false
				let messages = error.messages || []

				for (const message of messages) {
					toast({
						title: __("Error"),
						text: message || __("{0} failed!", [actionLabel]),
						icon: "alert-circle",
						position: "bottom-center",
						iconClasses: "text-red-500",
					})
				}
			},
		}
	)
}

onMounted(() => {
	reloadCheckins()

	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype == DOCTYPE) reloadCheckins()
	})
})

onBeforeUnmount(() => {
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")
})

watch(
	() => employee?.data?.name,
	(name) => {
		if (name) reloadCheckins()
	},
	{ immediate: true }
)
</script>
