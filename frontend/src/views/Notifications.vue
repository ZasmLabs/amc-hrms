<template>
	<ion-page>
		<ion-content class="ion-padding">
			<div class="flex flex-col h-screen w-screen">
				<div class="w-full sm:w-96 mx-auto">
					<!-- Header -->
					<header
						class="flex flex-row bg-white shadow-sm py-4 px-4 items-center border-b sticky top-0 z-10"
					>
						<div class="flex flex-row items-center gap-2">
							<Button
								variant="ghost"
								class="!pl-0 hover:bg-white"
								@click="router.back()"
							>
								<FeatherIcon name="chevron-left" class="h-5 w-5" />
							</Button>
							<h2 class="text-xl font-semibold text-gray-900">
								{{ __("Notifications") }}
							</h2>
						</div>
					</header>

					<!-- Content -->
					<div class="flex flex-col gap-4 p-4">
						<!-- Unread Count and Action Buttons -->
						<div class="flex flex-row justify-between items-center flex-wrap gap-3">
							<div
								class="text-lg font-semibold text-gray-900"
								v-if="unreadNotificationsCount.data"
							>
								{{ __("{0} Unread", [unreadNotificationsCount.data]) }}
							</div>
							<div class="flex flex-wrap gap-2 ml-auto">
								<Button
									v-if="showSettingsLink"
									variant="outline"
									size="sm"
									@click="router.push({ name: 'Settings' })"
								>
									<template #prefix>
										<FeatherIcon name="settings" class="w-4 h-4" />
									</template>
									{{ __("Settings") }}
								</Button>
								<Button
									v-if="notifications.data?.length"
									variant="outline"
									size="sm"
									@click="clearAllNotifications.submit"
									:loading="clearAllNotifications.loading"
								>
									<template #prefix>
										<FeatherIcon name="trash-2" class="w-4 h-4" />
									</template>
									{{ __("Clear all") }}
								</Button>
								<Button
									v-if="unreadNotificationsCount.data"
									variant="outline"
									size="sm"
									@click="markAllAsRead.submit"
									:loading="markAllAsRead.loading"
								>
									<template #prefix>
										<FeatherIcon name="check-circle" class="w-4 h-4" />
									</template>
									{{ __("Mark all as read") }}
								</Button>
							</div>
						</div>

						<!-- Notifications List -->
						<div
							class="flex flex-col gap-2"
							v-if="notifications.data?.length"
						>
							<div
								class="flex flex-row items-start gap-3 p-4 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors group"
								v-for="item in notifications.data"
								:key="item.name"
							>
								<!-- Unread Indicator -->
								<div
									v-if="!item.read"
									class="w-2 h-2 bg-blue-500 rounded-full mt-2 shrink-0"
								></div>
								<div v-else class="w-2 shrink-0"></div>

								<!-- Avatar -->
								<EmployeeAvatar :userID="item.from_user" size="lg" />

								<!-- Notification Content -->
								<router-link
									:to="getItemRoute(item)"
									@click="markAsRead(item.name)"
									class="flex flex-col gap-1 flex-1 min-w-0"
								>
									<div
										class="text-sm leading-5 text-gray-900"
										v-html="item.message"
									></div>
									<div class="text-xs text-gray-500">
										{{ dayjs(item.creation).fromNow() }}
									</div>
								</router-link>

								<!-- Delete Button -->
								<Button
									variant="ghost"
									size="sm"
									class="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
									@click.stop="deleteNotification(item.name)"
									:loading="deletingNotifications.has(item.name)"
								>
									<FeatherIcon name="x" class="w-4 h-4 text-gray-400" />
								</Button>
							</div>
						</div>

						<!-- Load More -->
						<div
							v-if="notifications.data?.length && notifications.hasNextPage"
							class="flex justify-center pt-2"
						>
							<Button
								variant="outline"
								@click="loadMore"
							>
								{{ __("Load more") }}
							</Button>
						</div>

						<!-- Empty State -->
						<EmptyState
							v-else-if="!notifications.data?.length"
							:message="__('You have no notifications')"
						/>
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
