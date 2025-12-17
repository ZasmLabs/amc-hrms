<template>
	<ion-page>
		<ion-content class="ion-padding">
			<div class="flex flex-col h-screen w-screen">
				<div class="w-full sm:w-96">
					<header
						class="flex flex-row bg-white shadow-sm py-4 px-3 items-center justify-between border-b sticky top-0 z-10"
					>
						<div class="flex flex-row items-center">
							<Button
								variant="ghost"
								class="!pl-0 hover:bg-white"
								@click="router.back()"
							>
								<FeatherIcon name="chevron-left" class="h-5 w-5" />
							</Button>
							<h2 class="text-xl font-semibold text-gray-900">{{ __("Notifications") }} </h2>
						</div>
					</header>

					<div class="flex flex-col gap-4 mt-5 p-4">
						<div class="flex flex-row justify-between items-center">
							<div
								class="text-lg text-gray-800 font-semibold"
								v-if="unreadNotificationsCount.data"
							>
								{{ __("{0} Unread", [unreadNotificationsCount.data]) }}
							</div>
							<div class="flex ml-auto gap-1">
								<Button
									v-if="showSettingsLink"
									variant="outline"
									@click="router.push({ name: 'Settings' })"
								>
									<template #prefix>
										<FeatherIcon name="settings" class="w-4" />
									</template>
									{{ __("Settings") }}
								</Button>
								<Button
									v-if="notifications.data?.length"
									variant="outline"
									@click="clearAllNotifications.submit"
									:loading="clearAllNotifications.loading"
								>
									<template #prefix>
										<FeatherIcon name="trash-2" class="w-4" />
									</template>
									{{ __("Clear all") }}
								</Button>
								<Button
									v-if="unreadNotificationsCount.data"
									variant="outline"
									@click="markAllAsRead.submit"
									:loading="markAllAsRead.loading"
								>
									<template #prefix>
										<FeatherIcon name="check-circle" class="w-4" />
									</template>
									{{ __("Mark all as read") }}
								</Button>
							</div>
						</div>

						<div
							class="flex flex-col bg-white rounded"
							v-if="notifications.data?.length"
						>
							<div
								:class="[
									'flex flex-row items-start p-4 justify-between border-b before:mt-3 group',
									`before:content-[''] before:mr-2 before:shrink-0 before:w-1.5 before:h-1.5 before:rounded-full`,
									item.read ? 'bg-white-500' : 'before:bg-blue-500',
								]"
								v-for="item in notifications.data"
								:key="item.name"
							>
								<router-link
									:to="getItemRoute(item)"
									@click="markAsRead(item.name)"
									class="flex flex-row items-start grow"
								>
									<EmployeeAvatar :userID="item.from_user" size="lg" />
									<div class="flex flex-col gap-0.5 grow ml-3">
										<div
											class="text-sm leading-5 font-normal text-gray-800"
											v-html="item.message"
										></div>
										<div class="text-xs font-normal text-gray-500">
											{{ dayjs(item.creation).fromNow() }}
										</div>
									</div>
								</router-link>
								<Button
									variant="ghost"
									class="opacity-0 group-hover:opacity-100 transition-opacity ml-2"
									@click.stop="deleteNotification(item.name)"
									:loading="deletingNotifications.has(item.name)"
								>
									<FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
								</Button>
							</div>
							
						</div>
						<div v-if="notifications.data?.length && notifications.hasNextPage" class="flex">
							<Button
								variant="outline"
								class="ml-auto"
								@click="loadMore"
							>
								{{ __('Load more') }}
							</Button>
						</div>
						<EmptyState v-else-if="!notifications.data" :message="__('You have no notifications')" />
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonContent, IonPage } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createResource, FeatherIcon } from "frappe-ui"

import { computed, inject, onMounted, ref } from "vue"
import EmployeeAvatar from "@/components/EmployeeAvatar.vue"
import EmptyState from "@/components/EmptyState.vue"

import {
	unreadNotificationsCount,
	notifications,
	arePushNotificationsEnabled,
} from "@/data/notifications"

const dayjs = inject("$dayjs")
const router = useRouter()
const __ = inject("$translate")
const currentStart = ref(0)
const pageLength = 10


const allowPushNotifications = computed(
	() =>
		window.frappe?.boot.push_relay_server_url &&
		arePushNotificationsEnabled.data
)

const showSettingsLink = computed(
	() => window.frappe?.boot.push_relay_server_url
)

const markAllAsRead = createResource({
	url: "hrms.api.mark_all_notifications_as_read",
	onSuccess() {
		notifications.reload()
		unreadNotificationsCount.reload()
	},
})

const clearAllNotifications = createResource({
	url: "hrms.api.delete_all_notifications",
	onSuccess() {
		notifications.reload()
		unreadNotificationsCount.reload()
	},
})

const deletingNotifications = ref(new Set())

function markAsRead(name) {
	notifications.setValue.submit(
		{ name, read: 1 },
		{
			onSuccess: () => {
				unreadNotificationsCount.reload()
			},
		}
	)
}

function deleteNotification(name) {
	if (deletingNotifications.value.has(name)) return
	
	deletingNotifications.value.add(name)
	
	const deleteResource = createResource({
		url: "hrms.api.delete_notification",
		makeParams: () => ({ name }),
		onSuccess() {
			deletingNotifications.value.delete(name)
			notifications.reload()
			unreadNotificationsCount.reload()
		},
		onError() {
			deletingNotifications.value.delete(name)
		},
	})
	
	deleteResource.reload()
}

function getItemRoute(item) {
	return {
		name: `${item.reference_document_type.replace(/\s+/g, "")}DetailView`,
		params: { id: item.reference_document_name },
	}
}

onMounted(() => {
	notifications.start = 0,
	notifications.pageLength = 10,
	notifications.fetch()
})

function loadMore() {
	currentStart.value += pageLength
	notifications.start = currentStart.value
	notifications.pageLength = pageLength
	notifications.list.fetch()
}
</script>
