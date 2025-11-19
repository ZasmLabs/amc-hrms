<template>
	<div class="flex flex-col mt-2">
		<div class="flex flex-row justify-between items-center">
			<h2 class="text-base font-semibold text-gray-800">{{ __("Reopen Call List") }}</h2>
		</div>

		<div
			v-if="reopenCallList && reopenCallList.length > 0"
			class="flex flex-col bg-white mt-5 rounded border overflow-auto"
		>
			<div
				class="flex flex-row p-3.5 items-center justify-between border-b"
				v-for="(item, idx) in reopenCallList"
				:key="idx"
			>
				<div class="flex flex-col w-full justify-center gap-2.5">
					<div class="text-base font-normal text-gray-800">
						{{ item.reopen_id || __("Reopen ID") }}
					</div>
					<div class="text-xs font-normal text-gray-500">
						<span v-if="item.reopened_on">{{ __("Reopened on: {0}", [item.reopened_on]) }}</span>
						<span v-if="item.reason" class="block mt-1">{{ item.reason }}</span>
					</div>
				</div>
			</div>
		</div>
		<EmptyState v-else :message="__('No reopen calls')" :isTableField="true" />
	</div>
</template>

<script setup>
import { computed } from "vue"
import { inject } from "vue"
import EmptyState from "./EmptyState.vue"

const __ = inject("$translate")

const props = defineProps({
	serviceCall: {
		type: Object,
		required: true,
	},
	isReadOnly: {
		type: Boolean,
		default: false,
	},
})

const reopenCallList = computed(() => {
	return props.serviceCall.reopen_call || []
})
</script>

