# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe import bold


class ServiceCallNotificationsMixin:
	"""Mixin class for Service Call specific notifications"""

	def notify_technicians_assigned(self):
		"""Notify all technicians when Service Call is assigned"""
		# Get current workflow state
		current_state = getattr(self, "workflow_state", None)
		
		# Check if workflow_state changed to "Assigned"
		# Try multiple methods to detect state change
		state_changed = False
		old_state = None
		
		# Method 1: Use has_value_changed if available
		if hasattr(self, "has_value_changed"):
			state_changed = self.has_value_changed("workflow_state")
			if state_changed and hasattr(self, "_doc_before_save") and self._doc_before_save:
				old_state = self._doc_before_save.get("workflow_state")
		
		# Method 2: Check doc_before_save directly
		if not state_changed and hasattr(self, "_doc_before_save") and self._doc_before_save:
			old_state = self._doc_before_save.get("workflow_state")
			state_changed = old_state != current_state
		
		# Method 3: Check if we're in a workflow transition (workflow_state just set)
		# If current_state is "Assigned" and we don't have old_state, assume it changed
		if not state_changed and current_state == "Assigned":
			# Check if this is a new document or if state was just set
			if not old_state or old_state != "Assigned":
				state_changed = True
		
		if state_changed and current_state == "Assigned":
			technicians = self.get_technician_users()
			
			if not technicians:
				return

			service_manager_name = self._get_user_name(frappe.session.user)
			customer_name = self._get_customer_name()

			for technician_user in technicians:
				if technician_user == frappe.session.user:
					continue  # Skip self-notification

				try:
					notification = frappe.new_doc("PWA Notification")
					notification.from_user = frappe.session.user
					notification.to_user = technician_user
					notification.message = (
						f"{bold(service_manager_name)} assigned you to Service Call {bold(self.name)} "
						f"for {bold(customer_name)}"
					)
					notification.reference_document_type = self.doctype
					notification.reference_document_name = self.name
					notification.insert(ignore_permissions=True)
				except Exception as e:
					frappe.log_error(f"Error creating notification for {technician_user}: {str(e)}")

	def notify_service_manager_status_update(self):
		"""Notify Service Manager when technician updates status"""
		if not self.has_value_changed("workflow_state"):
			return

		new_state = self.workflow_state

		# Only notify for specific state transitions
		notify_states = ["Accepted", "On Site", "Spare needed", "Close"]

		if new_state in notify_states:
			technician_user = frappe.session.user
			technician_name = self._get_user_name(technician_user)
			service_manager = self.owner  # Creator is Service Manager

			if technician_user == service_manager:
				return  # Skip if Service Manager is updating

			state_messages = {
				"Accepted": f"{bold(technician_name)} accepted Service Call {bold(self.name)}",
				"On Site": f"{bold(technician_name)} started work on Service Call {bold(self.name)}",
				"Spare needed": f"{bold(technician_name)} requested spare parts for Service Call {bold(self.name)}",
				"Close": f"{bold(technician_name)} completed Service Call {bold(self.name)}",
			}

			notification = frappe.new_doc("PWA Notification")
			notification.from_user = technician_user
			notification.to_user = service_manager
			notification.message = state_messages.get(
				new_state, f"Service Call {self.name} status updated to {new_state}"
			)
			notification.reference_document_type = self.doctype
			notification.reference_document_name = self.name
			notification.insert(ignore_permissions=True)

	def notify_technicians_reopened(self):
		"""Notify technicians when Service Call is reopened"""
		if self.has_value_changed("workflow_state") and self.workflow_state == "Reopen":
			technicians = self.get_technician_users()
			if not technicians:
				return

			service_manager_name = self._get_user_name(frappe.session.user)
			customer_name = self._get_customer_name()

			for technician_user in technicians:
				notification = frappe.new_doc("PWA Notification")
				notification.from_user = frappe.session.user
				notification.to_user = technician_user
				notification.message = (
					f"{bold(service_manager_name)} reopened Service Call {bold(self.name)} "
					f"for {bold(customer_name)}"
				)
				notification.reference_document_type = self.doctype
				notification.reference_document_name = self.name
				notification.insert(ignore_permissions=True)

	def notify_service_managers_created(self):
		"""Notify all Service Managers when a new Service Call is created"""
		# Only notify if workflow_state is "Open" (initial state)
		current_state = getattr(self, "workflow_state", None)
		if current_state != "Open":
			return
		
		# Get all Service Managers
		from frappe.utils.user import get_users_with_role
		service_managers = get_users_with_role("Service Manager")
		
		if not service_managers:
			return
		
		creator_name = self._get_user_name(frappe.session.user)
		customer_name = self._get_customer_name()
		
		for service_manager_user in service_managers:
			# Skip self-notification
			if service_manager_user == frappe.session.user:
				continue
			
			try:
				notification = frappe.new_doc("PWA Notification")
				notification.from_user = frappe.session.user
				notification.to_user = service_manager_user
				notification.message = (
					f"New Service Call {bold(self.name)} created by {bold(creator_name)} "
					f"for {bold(customer_name)}"
				)
				notification.reference_document_type = self.doctype
				notification.reference_document_name = self.name
				notification.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(f"Error creating notification for Service Manager {service_manager_user}: {str(e)}")

	def get_technician_users(self) -> list[str]:
		"""Get list of user IDs for all assigned technicians"""
		technician_users = []

		if hasattr(self, "technician_list") and self.technician_list:
			for tech in self.technician_list:
				if tech.employee:
					user_id = frappe.db.get_value("Employee", tech.employee, "user_id", cache=True)
					if user_id:
						technician_users.append(user_id)

		return list(set(technician_users))  # Remove duplicates

	def _get_user_name(self, user) -> str:
		"""Get full name of user, fallback to user ID"""
		if not user:
			return ""
		return frappe.db.get_value("User", user, "full_name", cache=True) or user

	def _get_customer_name(self) -> str:
		"""Get customer name, fallback to customer field value"""
		if not self.customer:
			return ""
		# Try to get customer name from AMC Customers or use the field value
		try:
			customer_name = frappe.db.get_value("AMC Customers", self.customer, "customer_name", cache=True)
			return customer_name or self.customer
		except Exception:
			return self.customer or ""


# Standalone function for doc_events hook - on_update
def send_service_call_notifications(doc, method=None):
	"""Hook function called when Service Call is updated"""
	try:
		# Create mixin instance and manually bind doc attributes
		mixin = ServiceCallNotificationsMixin()
		
		# Copy doc's attributes to mixin instance so methods can access them
		for attr in dir(doc):
			if not attr.startswith("_") and not callable(getattr(doc, attr)):
				try:
					setattr(mixin, attr, getattr(doc, attr))
				except:
					pass
		
		# Also copy important attributes that methods need
		mixin.doctype = doc.doctype
		mixin.name = doc.name
		mixin.workflow_state = getattr(doc, "workflow_state", None)
		mixin.technician_list = getattr(doc, "technician_list", [])
		mixin.customer = getattr(doc, "customer", None)
		mixin.owner = doc.owner
		
		# Copy doc_before_save if it exists
		if hasattr(doc, "_doc_before_save"):
			mixin._doc_before_save = doc._doc_before_save
		
		# Add has_value_changed method
		if hasattr(doc, "has_value_changed"):
			mixin.has_value_changed = lambda field: doc.has_value_changed(field)
		
		# Call notification methods
		mixin.notify_technicians_assigned()
		mixin.notify_service_manager_status_update()
		mixin.notify_technicians_reopened()
	except Exception as e:
		frappe.log_error(f"Error in ServiceCall notification methods for {getattr(doc, 'name', 'unknown')}: {str(e)}")


# Standalone function for doc_events hook - after_insert
def notify_service_call_created(doc, method=None):
	"""Hook function called when Service Call is created"""
	try:
		# Create mixin instance and manually bind doc attributes
		mixin = ServiceCallNotificationsMixin()
		
		# Copy important attributes that methods need
		mixin.doctype = doc.doctype
		mixin.name = doc.name
		mixin.workflow_state = getattr(doc, "workflow_state", None)
		mixin.customer = getattr(doc, "customer", None)
		mixin.owner = doc.owner
		
		# Call notification method for creation
		mixin.notify_service_managers_created()
	except Exception as e:
		frappe.log_error(f"Error in ServiceCall creation notification for {getattr(doc, 'name', 'unknown')}: {str(e)}")
