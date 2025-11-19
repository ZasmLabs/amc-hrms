<template>
	<div class="flex flex-col w-full gap-5">
		<div class="text-lg text-gray-800 font-bold">{{ __("Service Call Summary") }}</div>
		<div
			class="flex flex-col gap-4 bg-white py-3 px-3.5 rounded-lg border-none"
		>
			<div class="flex flex-col gap-1.5">
				<span class="text-gray-600 text-base font-medium leading-5">
					{{ __("Total Service Calls") }}
				</span>
				<span class="text-gray-800 text-lg font-bold leading-6">
					{{ summary.data?.total ?? 0 }}
				</span>
			</div>

			<div class="flex flex-row justify-between">
				<div class="flex flex-col gap-1">
					<div class="flex flex-row gap-1 items-center">
						<span class="text-gray-600 text-sm font-medium leading-5">
							{{ __("Open") }}
						</span>
						<FeatherIcon name="circle" class="text-gray-400 h-3 w-3" />
					</div>
					<span class="text-gray-800 text-base font-semibold leading-6">
						{{ summary.data?.open ?? 0 }}
					</span>
				</div>
				<div class="flex flex-col gap-1">
					<div class="flex flex-row gap-1 items-center">
						<span class="text-gray-600 text-sm font-medium leading-5">
							{{ __("Assigned") }}
						</span>
						<FeatherIcon name="user-check" class="text-blue-500 h-3 w-3" />
					</div>
					<span class="text-gray-800 text-base font-semibold leading-6">
						{{ summary.data?.assigned ?? 0 }}
					</span>
				</div>
				<div class="flex flex-col gap-1">
					<div class="flex flex-row gap-1 items-center">
						<span class="text-gray-600 text-sm font-medium leading-5">
							{{ __("On Site") }}
						</span>
						<FeatherIcon name="map-pin" class="text-orange-500 h-3 w-3" />
					</div>
					<span class="text-gray-800 text-base font-semibold leading-6">
						{{ summary.data?.on_site ?? 0 }}
					</span>
				</div>
				<div class="flex flex-col gap-1">
					<div class="flex flex-row gap-1 items-center">
						<span class="text-gray-600 text-sm font-medium leading-5">
							{{ __("Closed") }}
						</span>
						<FeatherIcon name="check-circle" class="text-green-500 h-3 w-3" />
					</div>
					<span class="text-gray-800 text-base font-semibold leading-6">
						{{ summary.data?.closed ?? 0 }}
					</span>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import { inject } from "vue"

import { serviceCallSummary as summary } from "@/data/service_calls"

const __ = inject("$translate")
</script>

