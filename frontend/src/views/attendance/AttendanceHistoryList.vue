<template>
	<ion-page>
		<ListView
			doctype="Attendance"
			:pageTitle="__('Attendance History')"
			:fields="ATTENDANCE_FIELDS"
			:filterConfig="FILTER_CONFIG"
			:showFilterButton="false"
			:serviceManagerTeamScope="true"
		/>
	</ion-page>
</template>

<script setup>
import { IonPage } from "@ionic/vue"
import ListView from "@/components/ListView.vue"
import { inject } from "vue"

const __ = inject("$translate")

const ATTENDANCE_FIELDS = [
	"name",
	"employee",
	"employee_name",
	"attendance_date",
	"status",
	"shift",
	"working_hours",
]

const FILTER_CONFIG = []
</script>
