<template>
	<div class="flex flex-col mt-2">
		<div class="flex flex-row justify-between items-center">
			<h2 class="text-base font-semibold text-gray-800">{{ __("Cash Memo") }}</h2>
			<Button
				v-if="!isReadOnly"
				class="text-sm"
				icon="plus"
				variant="subtle"
				@click="addCashMemo"
			/>
		</div>

		<div
			v-if="cashMemoList && cashMemoList.length > 0"
			class="flex flex-col bg-white mt-5 rounded border overflow-auto"
		>
			<div
				class="flex flex-row p-3.5 items-center justify-between border-b"
				v-for="(item, idx) in cashMemoList"
				:key="idx"
			>
				<div class="flex flex-col w-full justify-center gap-2.5">
					<div class="text-base font-normal text-gray-800">
						{{ item.line_items || __("Line Item") }}
					</div>
					<div class="text-xs font-normal text-gray-500">
						<span v-if="item.quantity">{{ __("Qty: {0}", [item.quantity]) }}</span>
						<span v-if="item.rate" class="whitespace-pre"> &middot; {{ __("Rate: {0}", [formatCurrency(item.rate)]) }}</span>
						<span v-if="item.amount" class="whitespace-pre"> &middot; {{ __("Amount: {0}", [formatCurrency(item.amount)]) }}</span>
					</div>
				</div>
				<Button
					v-if="!isReadOnly"
					icon="x"
					variant="ghost"
					@click="removeCashMemo(idx)"
				/>
			</div>
		</div>
		<EmptyState v-else :message="__('No cash memo items')" :isTableField="true" />
	</div>
</template>

<script setup>
import { computed } from "vue"
import { inject } from "vue"
import { Button } from "frappe-ui"
import EmptyState from "./EmptyState.vue"
import { formatCurrency } from "@/utils/formatters"

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

const cashMemoList = computed(() => {
	return props.serviceCall.table_whpt || []
})

function addCashMemo() {
	if (!props.serviceCall.table_whpt) {
		props.serviceCall.table_whpt = []
	}
	props.serviceCall.table_whpt.push({
		line_items: "",
		quantity: 0,
		rate: 0,
		amount: 0,
	})
}

function removeCashMemo(idx) {
	props.serviceCall.table_whpt.splice(idx, 1)
}
</script>

