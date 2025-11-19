"""
Setup script for Service Call prerequisites
Run this to create required roles and setup data
"""
import frappe


def setup_service_call_roles():
	"""Create Service Manager and Technician roles if they don't exist"""
	roles = ["Service Manager", "Technician"]
	
	for role_name in roles:
		if not frappe.db.exists("Role", role_name):
			role = frappe.new_doc("Role")
			role.role_name = role_name
			role.insert(ignore_permissions=True)
			frappe.db.commit()
			print(f"Created role: {role_name}")
		else:
			print(f"Role already exists: {role_name}")


def setup_sample_customer():
	"""Create a sample customer for testing"""
	customer_name = "Test Customer"
	
	if not frappe.db.exists("Customer", customer_name):
		customer = frappe.new_doc("Customer")
		customer.customer_name = customer_name
		customer.customer_type = "Company"
		customer.customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name") or "All Customer Groups"
		customer.territory = frappe.db.get_value("Territory", {"is_group": 0}, "name") or "All Territories"
		customer.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created customer: {customer_name}")
		return customer_name
	else:
		print(f"Customer already exists: {customer_name}")
		return customer_name


def setup_sample_contact(customer_name):
	"""Create a sample contact linked to customer"""
	contact_name = f"Contact for {customer_name}"
	
	if not frappe.db.exists("Contact", {"link_name": customer_name}):
		contact = frappe.new_doc("Contact")
		contact.first_name = "John"
		contact.last_name = "Doe"
		contact.mobile_no = "9876543210"
		contact.email_id = "john.doe@example.com"
		
		# Link to customer
		contact.append("links", {
			"link_doctype": "Customer",
			"link_name": customer_name
		})
		
		contact.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created contact: {contact.first_name} {contact.last_name}")
		return contact.name
	else:
		contact = frappe.get_doc("Contact", {"link_name": customer_name})
		print(f"Contact already exists: {contact.name}")
		return contact.name


def setup_technician_department():
	"""Create Technician department if it doesn't exist"""
	dept_name = "Technician - AA"
	
	if not frappe.db.exists("Department", dept_name):
		department = frappe.new_doc("Department")
		department.department_name = dept_name
		department.insert(ignore_permissions=True)
		frappe.db.commit()
		print(f"Created department: {dept_name}")
		return dept_name
	else:
		print(f"Department already exists: {dept_name}")
		return dept_name


@frappe.whitelist()
def setup_service_call_prerequisites():
	"""Main function to setup all prerequisites"""
	try:
		setup_service_call_roles()
		customer = setup_sample_customer()
		contact = setup_sample_contact(customer)
		department = setup_technician_department()
		
		return {
			"success": True,
			"message": "Service Call prerequisites setup completed",
			"data": {
				"customer": customer,
				"contact": contact,
				"department": department,
			}
		}
	except Exception as e:
		frappe.log_error(f"Error setting up Service Call prerequisites: {str(e)}")
		return {
			"success": False,
			"message": f"Error: {str(e)}"
		}

