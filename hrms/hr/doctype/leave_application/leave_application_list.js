frappe.listview_settings["Leave Application"] = {
	add_fields: [
		"leave_type",
		"employee",
		"employee_name",
		"total_leave_days",
		"from_date",
		"to_date",
	],
	has_indicator_for_draft: 1,
	get_indicator: function (doc) {
		const status_color = {
			Approved: "green",
			Rejected: "red",
			Open: "orange",
			Draft: "red",
			Cancelled: "red",
			Submitted: "blue",
		};

		const inferred_status =
			doc.docstatus === 0 ? "Draft" : doc.docstatus === 1 ? "Submitted" : "Cancelled";

		const status = doc.status
			? !doc.docstatus && ["Approved", "Rejected"].includes(doc.status)
				? "Draft"
				: doc.status
			: inferred_status;

		const indicator_filter = doc.status
			? "status,=," + doc.status
			: "docstatus,=," + (doc.docstatus || 0);

		return [__(status), status_color[status] || "gray", indicator_filter];
	},
};
