from . import __version__ as app_version

app_name = "mobile_pro"
app_title = "Mobile Pro"
app_publisher = "Mobile Pro Team"
app_description = "Comprehensive business management platform for cellphone stores"
app_email = "support@mobilepro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mobile_pro/css/mobile_pro.css"
# app_include_js = "/assets/mobile_pro/js/mobile_pro.js"

# include js, css files in header of web template
# web_include_css = "/assets/mobile_pro/css/mobile_pro.css"
# web_include_js = "/assets/mobile_pro/js/mobile_pro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mobile_pro/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "mobile_pro.utils.jinja_methods",
#	"filters": "mobile_pro.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "mobile_pro.install.before_install"
# after_install = "mobile_pro.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "mobile_pro.uninstall.before_uninstall"
# after_uninstall = "mobile_pro.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mobile_pro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"mobile_pro.tasks.all"
#	],
#	"daily": [
#		"mobile_pro.tasks.daily"
#	],
#	"hourly": [
#		"mobile_pro.tasks.hourly"
#	],
#	"weekly": [
#		"mobile_pro.tasks.weekly"
#	],
#	"monthly": [
#		"mobile_pro.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "mobile_pro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "mobile_pro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "mobile_pro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["mobile_pro.utils.before_request"]
# after_request = ["mobile_pro.utils.after_request"]

# Job Events
# ----------
# before_job = ["mobile_pro.utils.before_job"]
# after_job = ["mobile_pro.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"mobile_pro.auth.validate"
# ]