<template>
	<div class="flex flex-col mt-2">
		<div class="flex flex-row justify-between items-center">
			<h2 class="text-base font-semibold text-gray-800">{{ __("Technician List") }}</h2>
			<Button
				v-if="!isReadOnly"
				class="text-sm"
				icon="plus"
				variant="subtle"
				@click="addTechnician"
			/>
		</div>

		<div
			v-if="technicianList && technicianList.length > 0"
			class="flex flex-col bg-white mt-5 rounded border overflow-auto"
		>
			<div
				class="flex flex-row p-3.5 items-center justify-between border-b"
				v-for="(item, idx) in technicianList"
				:key="idx"
			>
				<div class="flex flex-col w-full justify-center gap-2.5">
					<div class="text-base font-normal text-gray-800">
						{{ item.employee_name || item.employee }}
					</div>
					<div class="text-xs font-normal text-gray-500">
						<span v-if="item.designation">{{ item.designation }}</span>
						<span v-if="item.department" class="whitespace-pre"> &middot; {{ item.department }}</span>
						<span v-if="item.mobile" class="whitespace-pre"> &middot; {{ item.mobile }}</span>
					</div>
				</div>
				<Button
					v-if="!isReadOnly"
					icon="x"
					variant="ghost"
					@click="removeTechnician(idx)"
				/>
			</div>
		</div>
		<EmptyState v-else :message="__('No technicians assigned')" :isTableField="true" />
	</div>
</template>

<script setup>
import { computed } from "vue"
import { inject } from "vue"
import { Button } from "frappe-ui"
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

const technicianList = computed(() => {
	return props.serviceCall.technician_list || []
})

function addTechnician() {
	if (!props.serviceCall.technician_list) {
		props.serviceCall.technician_list = []
	}
	props.serviceCall.technician_list.push({
		notify: true, // Default to checked (notify enabled)
		employee: "",
		employee_name: "",
		designation: "",
		department: "",
		data_jghu: "",
		date: "",
	})
}

function removeTechnician(idx) {
	props.serviceCall.technician_list.splice(idx, 1)
}
</script>

