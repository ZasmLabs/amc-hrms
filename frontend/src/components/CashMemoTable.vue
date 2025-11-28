<template>
	<div class="flex flex-col mt-2 gap-4">
		<div class="flex flex-row justify-between items-center">
			<h2 class="text-base font-semibold text-gray-800">{{ __("Cash Memo") }}</h2>
			<Button
				v-if="!isReadOnly"
				class="text-sm"
				icon="plus"
				variant="subtle"
				@click="addCashMemo"
			>
				{{ __("Add Item") }}
			</Button>
		</div>

		<div
			v-if="cashMemoList && cashMemoList.length > 0"
			class="flex flex-col gap-4"
		>
			<div
				class="flex flex-col p-4 bg-white rounded-lg border border-gray-200 gap-4"
				v-for="(item, idx) in cashMemoList"
				:key="idx"
			>
				<!-- Row Header with No. and Delete -->
				<div class="flex flex-row justify-between items-center">
					<div class="flex items-center gap-2">
						<span class="text-sm font-medium text-gray-600">{{ __("No.") }}</span>
						<span class="text-base font-semibold text-gray-800">{{ idx + 1 }}</span>
					</div>
					<Button
						v-if="!isReadOnly"
						icon="x"
						variant="ghost"
						size="sm"
						@click="removeCashMemo(idx)"
						:title="__('Remove Item')"
					/>
				</div>

				<!-- Line Items -->
				<div class="flex flex-col gap-1.5">
					<label class="block text-sm leading-5 text-gray-700">
						{{ __("Line Items") }}
					</label>
					<Input
						type="text"
						:value="item.line_items || ''"
						:placeholder="__('Enter line item description')"
						@input="(v) => updateField(idx, 'line_items', v)"
						:disabled="isReadOnly"
						class="w-full"
					/>
				</div>

				<!-- Quantity and Rate Row -->
				<div class="grid grid-cols-2 gap-4">
					<div class="flex flex-col gap-1.5">
						<label class="block text-sm leading-5 text-gray-700">
							{{ __("Quantity") }}
						</label>
						<Input
							type="number"
							:value="item.quantity || 0"
							:placeholder="__('Qty')"
							@input="(v) => updateQuantity(idx, v)"
							:disabled="isReadOnly"
							class="w-full"
							min="0"
							step="1"
						/>
					</div>
					<div class="flex flex-col gap-1.5">
						<label class="block text-sm leading-5 text-gray-700">
							{{ __("Rate") }}
						</label>
						<Input
							type="number"
							:value="item.rate || 0"
							:placeholder="__('Rate')"
							@input="(v) => updateRate(idx, v)"
							:disabled="isReadOnly"
							class="w-full"
							min="0"
							step="0.01"
						/>
					</div>
				</div>

				<!-- Amount (Auto-calculated) -->
				<div class="flex flex-col gap-1.5">
					<label class="block text-sm leading-5 text-gray-700">
						{{ __("Amount") }}
					</label>
					<Input
						type="text"
						:value="formatCurrency(item.amount || 0)"
						:disabled="true"
						class="w-full bg-gray-50"
						readonly
					/>
				</div>
			</div>
		</div>
		<EmptyState v-else :message="__('No cash memo items. Click Add Item to add one.')" :isTableField="true" />
	</div>
</template>

<script setup>
import { computed } from "vue"
import { inject } from "vue"
import { Button, Input } from "frappe-ui"
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

function updateField(idx, fieldname, value) {
	if (!props.serviceCall.table_whpt[idx]) return
	props.serviceCall.table_whpt[idx][fieldname] = value
	calculateAmount(idx)
}

function updateQuantity(idx, value) {
	const quantity = parseFloat(value) || 0
	updateField(idx, "quantity", quantity)
}

function updateRate(idx, value) {
	const rate = parseFloat(value) || 0
	updateField(idx, "rate", rate)
}

function calculateAmount(idx) {
	if (!props.serviceCall.table_whpt[idx]) return
	const item = props.serviceCall.table_whpt[idx]
	const quantity = parseFloat(item.quantity) || 0
	const rate = parseFloat(item.rate) || 0
	item.amount = quantity * rate
}
</script>

