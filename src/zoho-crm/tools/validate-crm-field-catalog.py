#!/usr/bin/env python3
"""Validate the governed GH Real Estate Zoho CRM per-module field catalogs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
API_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
VERIFIED_FIELD_STATUSES = {
    "verified_live_mcp",
    "verified_repo_runtime",
    "verified_repo_live_integration",
}
VERIFIED_MODULE_STATUSES = {
    "verified_live_mcp",
    "verified_standard_zoho",
    "verified_standard_zoho_and_repo_runtime",
    "verified_repo_live_integration",
}
REQUIRED_CURRENT_MODULES = {
    "Leads",
    "Zillow Intake Events",
    "Properties",
    "Contacts",
    "Rental Applications",
    "Units",
    "Leases",
    "Maintenance Requests",
    "Inspections",
    "Notices",
    "Vendors",
    "Tasks",
    "Equipment",
    "Lease Documents / Addenda",
    "Storage Units",
    "Utilities",
    "Condition Reports",
}
KNOWN_SOURCE_IDS = {
    "REPO_ZILLOW_FIELD_MAP",
    "REPO_ZILLOW_RUNTIME_DEFAULTS",
    "REPO_UNIT_ROUTING",
    "MATRIX_2026-07-08",
    "SETUP_SPEC",
    "LIVE_CRM_MCP_2026-07-24",
    "LIVE_CRM_MCP_2026-07-25",
}
LIVE_MCP_SOURCE_IDS = {
    "LIVE_CRM_MCP_2026-07-24",
    "LIVE_CRM_MCP_2026-07-25",
}
REQUIRED_COLUMNS = {
    "module_display_label",
    "module_type",
    "module_api_name",
    "module_api_name_status",
    "field_label",
    "field_type",
    "api_name",
    "api_name_status",
    "proposed_api_name",
    "disposition",
    "required",
    "help_text",
    "picklist_scope",
    "picklist_values_and_colors",
    "phase",
    "section",
    "notes",
    "source_ids",
}
GOVERNED_LIVE_SNAPSHOT_COUNT = 178
GOVERNED_LIVE_SNAPSHOT_SHA256 = (
    "1b9d4876ab14d069aac5894b894f7beb1614582850caf90caf110cf39be5a60a"
)

# Immutable production readbacks captured on 2026-07-24 and 2026-07-25. These
# entries are intentionally explicit: plausible API-name edits must not
# silently rewrite the repository's record of fields already created, reused,
# or reconciled in live CRM.
DEALS_CREATED_LIVE_MANIFEST = (
    ("Co-Applicant 1", "Co_Applicant_1", "Rental Application Information"),
    ("Co-Applicant 2", "Co_Applicant_2", "Rental Application Information"),
    ("Source Lead", "Source_Lead", "Rental Application Information"),
    ("Unit", "Unit", "Rental Application Information"),
    (
        "Application Received At",
        "Application_Received_At",
        "Rental Application Information",
    ),
    ("Addenda Required", "Addenda_Required", "Rental Application Information"),
    (
        "Approved Lease Commencement Date",
        "Approved_Lease_Commencement_Date",
        "Rental Application Information",
    ),
    (
        "Approved Lease Term End Date",
        "Approved_Lease_Term_End_Date",
        "Rental Application Information",
    ),
    (
        "Approved Possession Date",
        "Approved_Possession_Date",
        "Rental Application Information",
    ),
    (
        "Approved Security Deposit",
        "Approved_Security_Deposit",
        "Rental Application Information",
    ),
    (
        "Attorney Review Required?",
        "Attorney_Review_Required",
        "Rental Application Information",
    ),
    ("Decision", "Decision", "Rental Application Information"),
    ("Decision Date", "Decision_Date", "Rental Application Information"),
    (
        "Nonstandard Terms?",
        "Nonstandard_Terms",
        "Rental Application Information",
    ),
    (
        "Nonstandard Terms Notes",
        "Nonstandard_Terms_Notes",
        "Rental Application Information",
    ),
)

LEASE_CREATED_LIVE_MANIFEST = (
    ("Agreement Date", "Agreement_Date", "Lease Dates"),
    (
        "Attorney Review Required?",
        "Attorney_Review_Required",
        "Contract Controls",
    ),
    ("Nonstandard Terms Notes", "Nonstandard_Terms_Notes", "Contract Controls"),
    ("Nonstandard Terms?", "Nonstandard_Terms", "Contract Controls"),
    ("Addenda Required", "Addenda_Required", "Contract Controls"),
    (
        "Total Monthly Pet Rent Amount",
        "Total_Monthly_Pet_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Next Total Monthly Rent Due Date",
        "Next_Total_Monthly_Rent_Due_Date",
        "Monthly Charges",
    ),
    (
        "Base Storage Unit Rent Amount",
        "Base_Storage_Unit_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Total Monthly Storage Rent Amount",
        "Total_Monthly_Storage_Rent_Amount",
        "Monthly Charges",
    ),
    (
        "Total Due Before Possession",
        "Total_Due_Before_Possession",
        "Initial Amounts",
    ),
    (
        "Prorated Rent Start Date",
        "Prorated_Rent_Start_Date",
        "Initial Amounts",
    ),
    (
        "Prorated Rent End Date",
        "Prorated_Rent_End_Date",
        "Initial Amounts",
    ),
    (
        "Prorated Pet Rent Amount",
        "Prorated_Pet_Rent_Amount",
        "Initial Amounts",
    ),
    (
        "Prorated Storage Unit Rent Amount",
        "Prorated_Storage_Unit_Rent_Amount",
        "Initial Amounts",
    ),
    (
        "Holding Deposit Credit Applied",
        "Holding_Deposit_Credit_Applied",
        "Initial Amounts",
    ),
    (
        "Tenant 2 Email Snapshot",
        "Tenant_2_Email_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 2 Legal Name Snapshot",
        "Tenant_2_Legal_Name_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 3 Email Snapshot",
        "Tenant_3_Email_Snapshot",
        "Additional Tenants",
    ),
    (
        "Tenant 3 Legal Name Snapshot",
        "Tenant_3_Legal_Name_Snapshot",
        "Additional Tenants",
    ),
    (
        "Pet Security Deposit Amount",
        "Pet_Security_Deposit_Amount",
        "Initial Amounts",
    ),
    (
        "Premises Apartment Number",
        "Premises_Apartment_Number",
        "Premises Snapshot",
    ),
    ("Premises City", "Premises_City", "Premises Snapshot"),
    ("Premises State", "Premises_State", "Premises Snapshot"),
    (
        "Premises Street Line 1",
        "Premises_Street_Line_1",
        "Premises Snapshot",
    ),
    ("Premises ZIP Code", "Premises_ZIP_Code", "Premises Snapshot"),
    ("Property", "Property", "Relationships"),
    ("Rental Application", "Rental_Application", "Relationships"),
    ("Tenant 2", "Tenant_2", "Relationships"),
    ("Tenant 3", "Tenant_3", "Relationships"),
    ("Unit", "Unit", "Relationships"),
    ("Lease Type", "Lease_Type", "Lease Identity and Status"),
    ("Previous Lease", "Previous_Lease", "Relationships"),
    ("Guarantor", "Guarantor", "Relationships"),
)

LEASE_REUSED_LIVE_MANIFEST = (
    ("Move-In Date", "Move_In_Date", "Lease Dates"),
    ("Lease Name", "Name", "Lease Identity and Status"),
    ("Lease Status", "Lease_Status", "Lease Identity and Status"),
    ("Security Deposit", "Security_Deposit", "Initial Amounts"),
    ("Tenant", "Tenant", "Relationships"),
    ("Lease End Date", "Lease_End_Date", "Lease Dates"),
    ("Lease Start Date", "Lease_Start_Date", "Lease Dates"),
)

LEASE_PLACED_LIVE_MANIFEST = (
    LEASE_CREATED_LIVE_MANIFEST + LEASE_REUSED_LIVE_MANIFEST
)
CONTACTS_RECONCILED_LIVE_MANIFEST = (
    ("Preferred Name", "Preferred_Name", "Contact Identity & Role"),
    (
        "Email Operational Consent?",
        "Email_Operational_Consent",
        "Communication & Consent",
    ),
    (
        "SMS Operational Consent?",
        "SMS_Operational_Consent",
        "Communication & Consent",
    ),
    ("Primary Language", "Primary_Language", "Communication & Consent"),
    ("Current Lease", "Current_Lease", "Removed from Active Layout"),
    ("Current Unit", "Current_Unit", "Removed from Active Layout"),
    (
        "Portal Invite Sent At",
        "Portal_Invite_Sent_At",
        "Portal & Integrations",
    ),
    (
        "Portal Invite Status",
        "Portal_Invite_Status",
        "Portal & Integrations",
    ),
    (
        "WorkDrive Person Folder URL",
        "WorkDrive_Person_Folder_URL",
        "Portal & Integrations",
    ),
)
CONTACTS_SECOND_PASS_LIVE_MANIFEST = (
    ("Name", "Name1", "Removed from Active Layout"),
    ("F. Name", "F_Name", "Removed from Active Layout"),
    ("L. Name", "L_Name", "Removed from Active Layout"),
    ("Parent Property", "Parent_Property", "Removed from Active Layout"),
    ("Property Type", "Account_Type", "Removed from Active Layout"),
)
PROPERTIES_RECONCILED_LIVE_MANIFEST = (
    (
        "Owner / Landlord Legal Name",
        "Owner_Landlord_Legal_Name",
        "Property Identity & Status",
    ),
    ("Property Code", "Property_Code", "Property Identity & Status"),
    ("Property Status", "Property_Status", "Property Identity & Status"),
    ("County", "County", "Property Address & Legal Notice"),
    ("Notice Email", "Notice_Email", "Property Address & Legal Notice"),
    (
        "Emergency Maintenance Phone",
        "Emergency_Maintenance_Phone",
        "Owner & Emergency Contact",
    ),
    (
        "Default Lease Template Version",
        "Default_Lease_Template_Version",
        "Leasing & Integrations",
    ),
    (
        "WorkDrive Property Folder URL",
        "WorkDrive_Property_Folder_URL",
        "Leasing & Integrations",
    ),
)
PROPERTIES_SECOND_PASS_LIVE_MANIFEST = (
    ("Parent Property", "Parent_Account", "Removed from Active Layout"),
)
UNITS_RECONCILED_LIVE_MANIFEST = (
    ("Current Lease", "Current_Lease", "Occupancy & Current Tenancy"),
    (
        "Current Lease End Date",
        "Current_Lease_End_Date",
        "Occupancy & Current Tenancy",
    ),
    (
        "Move-In Checklist Status",
        "Move_In_Checklist_Status",
        "Occupancy & Current Tenancy",
    ),
    (
        "Next Lease Start Date",
        "Next_Lease_Start_Date",
        "Occupancy & Current Tenancy",
    ),
    ("Available Date", "Available_Date", "Rent & Availability"),
    ("Current Base Rent", "Current_Base_Rent", "Rent & Availability"),
    ("Default Storage Area", "Default_Storage_Area", "Rent & Availability"),
    ("Security Deposit Default", "Security_Deposit_Default", "Rent & Availability"),
    ("Storage Available?", "Storage_Available", "Rent & Availability"),
    ("Target Market Rent", "Target_Market_Rent", "Rent & Availability"),
    ("Market Status", "Market_Status", "Rent & Availability"),
    ("Furnished?", "Furnished", "Physical Details"),
    ("Parking Spaces", "Parking_Spaces", "Physical Details"),
    (
        "Zillow Listing Active?",
        "Zillow_Listing_Active",
        "Zillow Listing & Routing",
    ),
    ("Zillow Listing URL", "Zillow_Listing_URL", "Zillow Listing & Routing"),
)
UNITS_REUSED_LIVE_MANIFEST = (
    ("Unit I.D.", "Unit_I_D", "Unit Summary"),
    ("Unit Status", "Unit_Status", "Unit Summary"),
    (
        "Current Tenant",
        "Current_Tenant",
        "Occupancy & Current Tenancy",
    ),
    ("Bathrooms", "Bathrooms", "Unit Details"),
    ("Bedrooms", "Bedrooms", "Unit Details"),
    ("Square Feet", "Square_Feet", "Unit Details"),
    (
        "Zoho WorkDrive Folder URL",
        "Zoho_WorkDrive_Folder_URL",
        "Files & Integrations",
    ),
)
DEALS_RECONCILED_LIVE_MANIFEST = (
    ("Application Reviewer", "Application_Reviewer", "Application Identity"),
    ("Household Size", "Household_Size", "Application Intake"),
    ("Pets Requested?", "Pets_Requested", "Application Intake"),
    (
        "Requested Lease Term Months",
        "Requested_Lease_Term_Months",
        "Application Intake",
    ),
    ("Storage Requested?", "Storage_Requested", "Application Intake"),
    (
        "Zoho Creator Application ID",
        "Zoho_Creator_Application_ID",
        "Integrations",
    ),
)
DEALS_SECOND_PASS_LIVE_MANIFEST = (
    ("Requested Pet Count", "Requested_Pet_Count", "Application Intake"),
    (
        "Requested Storage Unit Count",
        "Requested_Storage_Unit_Count",
        "Application Intake",
    ),
)
CASES_RECONCILED_LIVE_MANIFEST = (
    ("Lease", "Lease", "Relationships"),
    ("Unit", "Unit", "Relationships"),
    ("Assigned Vendor", "Assigned_Vendor", "Access & Scheduling"),
    (
        "Assigned Vendor Contact",
        "Assigned_Vendor_Contact",
        "Access & Scheduling",
    ),
    ("Access Permission", "Access_Permission", "Access & Scheduling"),
    (
        "Pets / Animals Need Secured?",
        "Pets_Animals_Need_Secured",
        "Access & Scheduling",
    ),
    ("Reported At", "Reported_At", "Access & Scheduling"),
    ("Scheduled Date/Time", "Scheduled_Date_Time", "Access & Scheduling"),
    ("Creator Ticket ID", "Creator_Ticket_ID", "Files & Evidence"),
    (
        "Photos / Files Folder URL",
        "Photos_Files_Folder_URL",
        "Files & Evidence",
    ),
    ("Photos Received?", "Photos_Received", "Files & Evidence"),
    ("Emergency?", "Emergency", "Request Identity"),
    ("Maintenance Category", "Maintenance_Category", "Request Identity"),
)
CASES_STANDARD_PICKLIST_LIVE_MANIFEST = (
    ("Case Origin", "Case_Origin", "Request Identity"),
    ("Priority", "Priority", "Request Identity"),
    ("Status", "Status", "Request Identity"),
)
INSPECTIONS_RECONCILED_LIVE_MANIFEST = (
    ("Inspection Type", "Inspection_Type", "Inspection Identity"),
    ("Property", "Property", "Inspection Identity"),
    ("Unit", "Unit", "Inspection Identity"),
    ("Lease", "Lease", "Inspection Identity"),
    ("Primary Tenant", "Primary_Tenant", "Inspection Identity"),
    ("Status", "Status", "Inspection Identity"),
    ("Inspection Date", "Inspection_Date", "Timing & Responsibility"),
    ("Due Date", "Due_Date", "Timing & Responsibility"),
    ("Completed Date", "Completed_Date", "Timing & Responsibility"),
    ("Completed By", "Completed_By", "Timing & Responsibility"),
    (
        "Joint Inspection Completed?",
        "Joint_Inspection_Completed",
        "Timing & Responsibility",
    ),
    (
        "Related Maintenance Request",
        "Related_Maintenance_Request",
        "Issues & Follow-Up",
    ),
    ("Repair Requested?", "Repair_Requested", "Issues & Follow-Up"),
    (
        "Checklist Form URL",
        "Checklist_Form_URL",
        "Documents & Signatures",
    ),
    (
        "Signed Checklist PDF URL",
        "Signed_Checklist_PDF_URL",
        "Documents & Signatures",
    ),
    ("Photos Folder URL", "Photos_Folder_URL", "Documents & Signatures"),
    ("Tenant Signed?", "Tenant_Signed", "Documents & Signatures"),
    ("Landlord Signed?", "Landlord_Signed", "Documents & Signatures"),
)
INSPECTIONS_REUSED_LIVE_MANIFEST = (
    ("Inspection Name", "Name", "Inspection Identity"),
)
LEASE_ADDITIONAL_LIVE_MANIFEST = (
    (
        "First Full Month Base Rent Amount",
        "First_Full_Month_Base_Rent_Amount",
        "Initial Amounts",
    ),
)
VENDORS_RECONCILED_LIVE_MANIFEST = (
    (
        "Vendor Status",
        "Vendor_Status",
        "Vendor Identity & Classification",
    ),
)
TASKS_RECONCILED_LIVE_MANIFEST = (
    ("Task Category", "Task_Category", "Routing & Handoff"),
    (
        "Important for PM Handoff?",
        "Important_for_PM_Handoff",
        "Routing & Handoff",
    ),
)
TASKS_STANDARD_PICKLIST_LIVE_MANIFEST = (
    ("Priority", "Priority", "Task Information"),
)
STORAGE_UNITS_RECONCILED_LIVE_MANIFEST = (
    ("Property", "Property_Record", "Relationships"),
    ("Unit", "Unit", "Relationships"),
    ("Lease Record", "Lease_Record", "Relationships"),
)
UTILITIES_RECONCILED_LIVE_MANIFEST = (
    ("Property Record", "Property_Record", "Authoritative Relationships"),
    ("Unit Record", "Unit_Record", "Authoritative Relationships"),
)
CONDITION_REPORTS_RECONCILED_LIVE_MANIFEST = (
    ("Inspection", "Inspection", "Relationships"),
    ("Property", "Property", "Relationships"),
    ("Unit", "Unit", "Relationships"),
    ("Lease", "Lease", "Relationships"),
    ("Tenant", "Tenant", "Relationships"),
)

JULY_24_RECONCILIATION_CREATED_COUNT = sum(
    len(manifest)
    for manifest in (
        CONTACTS_RECONCILED_LIVE_MANIFEST,
        PROPERTIES_RECONCILED_LIVE_MANIFEST,
        UNITS_RECONCILED_LIVE_MANIFEST,
        DEALS_RECONCILED_LIVE_MANIFEST,
        CASES_RECONCILED_LIVE_MANIFEST,
        INSPECTIONS_RECONCILED_LIVE_MANIFEST,
        LEASE_ADDITIONAL_LIVE_MANIFEST,
        VENDORS_RECONCILED_LIVE_MANIFEST,
        TASKS_RECONCILED_LIVE_MANIFEST,
        STORAGE_UNITS_RECONCILED_LIVE_MANIFEST,
        UTILITIES_RECONCILED_LIVE_MANIFEST,
        CONDITION_REPORTS_RECONCILED_LIVE_MANIFEST,
    )
)
JULY_24_STANDARD_PICKLIST_RECONCILED_COUNT = (
    len(CASES_STANDARD_PICKLIST_LIVE_MANIFEST)
    + len(TASKS_STANDARD_PICKLIST_LIVE_MANIFEST)
)
JULY_24_REUSED_LIVE_COUNT = (
    len(UNITS_REUSED_LIVE_MANIFEST)
    + len(INSPECTIONS_REUSED_LIVE_MANIFEST)
)
JULY_25_RECONCILIATION_CREATED_COUNT = len(DEALS_SECOND_PASS_LIVE_MANIFEST)
JULY_25_RECONCILIATION_DISCOVERED_COUNT = (
    len(CONTACTS_SECOND_PASS_LIVE_MANIFEST)
    + len(PROPERTIES_SECOND_PASS_LIVE_MANIFEST)
)

GOVERNED_LIVE_MANIFEST = (
    (
        "Rental Applications",
        "Deals",
        DEALS_CREATED_LIVE_MANIFEST
        + DEALS_RECONCILED_LIVE_MANIFEST
        + DEALS_SECOND_PASS_LIVE_MANIFEST,
    ),
    (
        "Leases",
        "Leases",
        LEASE_PLACED_LIVE_MANIFEST + LEASE_ADDITIONAL_LIVE_MANIFEST,
    ),
    (
        "Contacts",
        "Contacts",
        CONTACTS_RECONCILED_LIVE_MANIFEST + CONTACTS_SECOND_PASS_LIVE_MANIFEST,
    ),
    (
        "Properties",
        "Accounts",
        PROPERTIES_RECONCILED_LIVE_MANIFEST
        + PROPERTIES_SECOND_PASS_LIVE_MANIFEST,
    ),
    (
        "Units",
        "Units",
        UNITS_RECONCILED_LIVE_MANIFEST + UNITS_REUSED_LIVE_MANIFEST,
    ),
    (
        "Maintenance Requests",
        "Cases",
        CASES_RECONCILED_LIVE_MANIFEST
        + CASES_STANDARD_PICKLIST_LIVE_MANIFEST,
    ),
    (
        "Inspections",
        "Inspections",
        INSPECTIONS_RECONCILED_LIVE_MANIFEST
        + INSPECTIONS_REUSED_LIVE_MANIFEST,
    ),
    ("Vendors", "Vendors", VENDORS_RECONCILED_LIVE_MANIFEST),
    (
        "Tasks",
        "Tasks",
        TASKS_RECONCILED_LIVE_MANIFEST
        + TASKS_STANDARD_PICKLIST_LIVE_MANIFEST,
    ),
    (
        "Storage Units",
        "Storage_Units",
        STORAGE_UNITS_RECONCILED_LIVE_MANIFEST,
    ),
    ("Utilities", "Utilities", UTILITIES_RECONCILED_LIVE_MANIFEST),
    (
        "Condition Reports",
        "Condition_Reports",
        CONDITION_REPORTS_RECONCILED_LIVE_MANIFEST,
    ),
)

GOVERNED_LIVE_FIELD_TYPE_GROUPS = {
    "Rental Applications": {
        "Lookup": ("Co-Applicant 1", "Co-Applicant 2", "Source Lead", "Unit"),
        "Date/Time": ("Application Received At",),
        "Multi-Select Pick List": ("Addenda Required",),
        "Date": (
            "Approved Lease Commencement Date",
            "Approved Lease Term End Date",
            "Approved Possession Date",
            "Decision Date",
        ),
        "Currency": ("Approved Security Deposit",),
        "Checkbox": (
            "Attorney Review Required?",
            "Nonstandard Terms?",
            "Pets Requested?",
            "Storage Requested?",
        ),
        "Pick List": ("Decision",),
        "Multi-Line": ("Nonstandard Terms Notes",),
        "User": ("Application Reviewer",),
        "Number": (
            "Household Size",
            "Requested Lease Term Months",
            "Requested Pet Count",
            "Requested Storage Unit Count",
        ),
        "Single Line": ("Zoho Creator Application ID",),
    },
    "Leases": {
        "Date": (
            "Agreement Date",
            "Next Total Monthly Rent Due Date",
            "Prorated Rent Start Date",
            "Prorated Rent End Date",
            "Move-In Date",
            "Lease End Date",
            "Lease Start Date",
        ),
        "Checkbox": ("Attorney Review Required?", "Nonstandard Terms?"),
        "Multi-Line": ("Nonstandard Terms Notes",),
        "Multi-Select Pick List": ("Addenda Required",),
        "Currency": (
            "Total Monthly Pet Rent Amount",
            "Base Storage Unit Rent Amount",
            "Total Monthly Storage Rent Amount",
            "Total Due Before Possession",
            "Prorated Pet Rent Amount",
            "Prorated Storage Unit Rent Amount",
            "Holding Deposit Credit Applied",
            "Pet Security Deposit Amount",
            "Security Deposit",
            "First Full Month Base Rent Amount",
        ),
        "Email": ("Tenant 2 Email Snapshot", "Tenant 3 Email Snapshot"),
        "Single Line": (
            "Tenant 2 Legal Name Snapshot",
            "Tenant 3 Legal Name Snapshot",
            "Premises Apartment Number",
            "Premises City",
            "Premises State",
            "Premises Street Line 1",
            "Premises ZIP Code",
        ),
        "Lookup": (
            "Property",
            "Rental Application",
            "Tenant 2",
            "Tenant 3",
            "Unit",
            "Previous Lease",
            "Guarantor",
            "Tenant",
        ),
        "Pick List": ("Lease Type", "Lease Status"),
        "Single Line / Module Name": ("Lease Name",),
    },
    "Contacts": {
        "Single Line": (
            "Preferred Name",
            "Parent Property",
            "Property Type",
        ),
        "Formula - Text": ("Name", "F. Name", "L. Name"),
        "Checkbox": (
            "Email Operational Consent?",
            "SMS Operational Consent?",
        ),
        "Pick List": ("Primary Language", "Portal Invite Status"),
        "Lookup": ("Current Lease", "Current Unit"),
        "Date/Time": ("Portal Invite Sent At",),
        "URL": ("WorkDrive Person Folder URL",),
    },
    "Properties": {
        "Single Line": (
            "Owner / Landlord Legal Name",
            "Property Code",
            "County",
            "Default Lease Template Version",
        ),
        "Pick List": ("Property Status",),
        "Email": ("Notice Email",),
        "Phone": ("Emergency Maintenance Phone",),
        "URL": ("WorkDrive Property Folder URL",),
        "Standard Lookup - Accounts": ("Parent Property",),
    },
    "Units": {
        "Lookup": ("Current Lease", "Current Tenant"),
        "Date": (
            "Current Lease End Date",
            "Next Lease Start Date",
            "Available Date",
        ),
        "Pick List": (
            "Move-In Checklist Status",
            "Market Status",
            "Unit Status",
        ),
        "Currency": (
            "Current Base Rent",
            "Security Deposit Default",
            "Target Market Rent",
        ),
        "Single Line": ("Default Storage Area",),
        "Checkbox": (
            "Furnished?",
            "Storage Available?",
            "Zillow Listing Active?",
        ),
        "Number": ("Parking Spaces", "Bedrooms", "Square Feet"),
        "Decimal": ("Bathrooms",),
        "URL": ("Zillow Listing URL", "Zoho WorkDrive Folder URL"),
        "Auto-Number": ("Unit I.D.",),
    },
    "Maintenance Requests": {
        "Lookup": (
            "Lease",
            "Unit",
            "Assigned Vendor",
            "Assigned Vendor Contact",
        ),
        "Pick List": ("Access Permission", "Maintenance Category"),
        "Checkbox": (
            "Pets / Animals Need Secured?",
            "Photos Received?",
            "Emergency?",
        ),
        "Date/Time": ("Reported At", "Scheduled Date/Time"),
        "Single Line": ("Creator Ticket ID",),
        "URL": ("Photos / Files Folder URL",),
        "Pick List / Standard": ("Case Origin", "Priority", "Status"),
    },
    "Inspections": {
        "Pick List": ("Inspection Type", "Status"),
        "Lookup": (
            "Property",
            "Unit",
            "Lease",
            "Primary Tenant",
            "Related Maintenance Request",
        ),
        "Date": ("Inspection Date", "Due Date", "Completed Date"),
        "User": ("Completed By",),
        "Checkbox": (
            "Joint Inspection Completed?",
            "Repair Requested?",
            "Tenant Signed?",
            "Landlord Signed?",
        ),
        "URL": (
            "Checklist Form URL",
            "Signed Checklist PDF URL",
            "Photos Folder URL",
        ),
        "Single Line / Module Name": ("Inspection Name",),
    },
    "Vendors": {
        "Pick List": ("Vendor Status",),
    },
    "Tasks": {
        "Pick List": ("Task Category",),
        "Checkbox": ("Important for PM Handoff?",),
        "Pick List / Standard": ("Priority",),
    },
    "Storage Units": {
        "Lookup": ("Property", "Unit", "Lease Record"),
    },
    "Utilities": {
        "Lookup": ("Property Record", "Unit Record"),
    },
    "Condition Reports": {
        "Lookup": ("Inspection", "Property", "Unit", "Lease", "Tenant"),
    },
}
GOVERNED_LIVE_FIELD_TYPES = {
    (module_label, field_label): field_type
    for module_label, type_groups in GOVERNED_LIVE_FIELD_TYPE_GROUPS.items()
    for field_type, field_labels in type_groups.items()
    for field_label in field_labels
}

GOVERNED_LIVE_LOOKUP_TARGETS = {
    ("Rental Applications", "Co-Applicant 1"): "Contacts",
    ("Rental Applications", "Co-Applicant 2"): "Contacts",
    ("Rental Applications", "Source Lead"): "Leads",
    ("Rental Applications", "Unit"): "Units",
    ("Leases", "Property"): "Accounts",
    ("Leases", "Rental Application"): "Deals",
    ("Leases", "Tenant 2"): "Contacts",
    ("Leases", "Tenant 3"): "Contacts",
    ("Leases", "Unit"): "Units",
    ("Leases", "Previous Lease"): "Leases",
    ("Leases", "Guarantor"): "Contacts",
    ("Leases", "Tenant"): "Contacts",
    ("Contacts", "Current Lease"): "Leases",
    ("Contacts", "Current Unit"): "Units",
    ("Units", "Current Lease"): "Leases",
    ("Units", "Current Tenant"): "Contacts",
    ("Maintenance Requests", "Lease"): "Leases",
    ("Maintenance Requests", "Unit"): "Units",
    ("Maintenance Requests", "Assigned Vendor"): "Vendors",
    ("Maintenance Requests", "Assigned Vendor Contact"): "Contacts",
    ("Inspections", "Property"): "Accounts",
    ("Inspections", "Unit"): "Units",
    ("Inspections", "Lease"): "Leases",
    ("Inspections", "Primary Tenant"): "Contacts",
    ("Inspections", "Related Maintenance Request"): "Cases",
    ("Storage Units", "Property"): "Accounts",
    ("Storage Units", "Unit"): "Units",
    ("Storage Units", "Lease Record"): "Leases",
    ("Utilities", "Property Record"): "Accounts",
    ("Utilities", "Unit Record"): "Units",
    ("Condition Reports", "Inspection"): "Inspections",
    ("Condition Reports", "Property"): "Accounts",
    ("Condition Reports", "Unit"): "Units",
    ("Condition Reports", "Lease"): "Leases",
    ("Condition Reports", "Tenant"): "Contacts",
}

ADDENDA_REQUIRED_CHOICES = (
    "Lead-Based Paint=#DB2777 | Ordinary Pet=#0F766E | Storage=#7C3AED | "
    "Guaranty/Cosigner=#0891B2 | Roommate=#4F46E5 | HOA/Handbook=#65A30D | "
    "Other=#EA580C"
)
GOVERNED_LIVE_CHOICES = {
    ("Rental Applications", "Decision"): (
        "Pending=#D97706 | Approved=#16A34A | "
        "Approved with Conditions=#EA580C | Denied=#DC2626 | "
        "Withdrawn=#6B7280 | Duplicate=#6B7280 | No Response=#6B7280"
    ),
    ("Rental Applications", "Addenda Required"): ADDENDA_REQUIRED_CHOICES,
    ("Leases", "Lease Type"): "Original=#2563EB | Renewal=#16A34A",
    ("Leases", "Addenda Required"): ADDENDA_REQUIRED_CHOICES,
    ("Leases", "Lease Status"): (
        "Contract in Progress=#7C3AED | Draft Lease Data=#AF38FA | "
        "Ready For Contract=#7C3AED | Signed - Future=#16A34A | "
        "Active=#16A34A | Contract Requested=#F8E199 | "
        "Contract Drafting=#90A9FD | Month-to-Month=#2563EB | "
        "Non-Renewing=#EA580C | Sent For Signature=#F5C72F | "
        "Signed - Pending Move-In=#F5C72F | Terminated=#DC2626 | "
        "Expired=#92400E | Lease Active=#67C480 | Moved Out=#6B7280 | "
        "Renewal Pending=#D97706 | Archived=#6B7280 | Notice Given=#EB4D4D | "
        "Ended=#666666 | Cancelled=#666666 | Draft=#2563EB"
    ),
    ("Contacts", "Primary Language"): (
        "English=UNCOLORED | Spanish=UNCOLORED | Ukrainian=UNCOLORED | "
        "Russian=UNCOLORED | Other=UNCOLORED"
    ),
    ("Contacts", "Portal Invite Status"): (
        "Not Invited=UNCOLORED | Invite Ready=UNCOLORED | "
        "Invited=UNCOLORED | Accepted=UNCOLORED | Failed=UNCOLORED | "
        "Disabled=UNCOLORED"
    ),
    ("Properties", "Property Status"): (
        "Active=UNCOLORED | Inactive=UNCOLORED | Archived=UNCOLORED"
    ),
    ("Units", "Move-In Checklist Status"): (
        "Not Started=UNCOLORED | Sent=UNCOLORED | In Progress=UNCOLORED | "
        "Completed=UNCOLORED | Overdue=UNCOLORED | Not Applicable=UNCOLORED"
    ),
    ("Units", "Market Status"): (
        "Not Listed=UNCOLORED | Listed=UNCOLORED | "
        "Application Pending=UNCOLORED | Lease Pending=UNCOLORED | "
        "Leased=UNCOLORED | Renovation Hold=UNCOLORED"
    ),
    ("Units", "Unit Status"): (
        "Occupied=#67C480 | Vacant - Ready=#F5C72F | "
        "Vacant - Needs Turnover=#EB4D4D | Under Renovation=#168AEF | "
        "Reserved=#C4F0B3 | Inactive=#666666"
    ),
    ("Maintenance Requests", "Access Permission"): (
        "Permission Granted=UNCOLORED | Appointment Required=UNCOLORED | "
        "Tenant Must Be Present=UNCOLORED | "
        "Emergency Access Only=UNCOLORED | Unknown=UNCOLORED"
    ),
    ("Maintenance Requests", "Maintenance Category"): (
        "Plumbing=UNCOLORED | Electrical=UNCOLORED | HVAC=UNCOLORED | "
        "Appliance=UNCOLORED | Pest=UNCOLORED | Lock/Key=UNCOLORED | "
        "Water Leak=UNCOLORED | Noise/Rule Issue=UNCOLORED | "
        "Common Area=UNCOLORED | Exterior/Grounds=UNCOLORED | "
        "Laundry=UNCOLORED | Other=UNCOLORED"
    ),
    ("Inspections", "Inspection Type"): (
        "Move-In=UNCOLORED | Move-Out=UNCOLORED | Annual=UNCOLORED | "
        "Pre-Renewal=UNCOLORED | Post-Repair=UNCOLORED | "
        "Owner Walkthrough=UNCOLORED | Other=UNCOLORED"
    ),
    ("Inspections", "Status"): (
        "Not Started=UNCOLORED | Scheduled=UNCOLORED | "
        "Sent to Tenant=UNCOLORED | In Progress=UNCOLORED | "
        "Tenant Submitted=UNCOLORED | Landlord Review=UNCOLORED | "
        "Follow-Up Required=UNCOLORED | Completed=UNCOLORED | "
        "Overdue=UNCOLORED | Cancelled=UNCOLORED | Archived=UNCOLORED"
    ),
    ("Vendors", "Vendor Status"): (
        "Active=UNCOLORED | Inactive=UNCOLORED | Archived=UNCOLORED"
    ),
    ("Tasks", "Task Category"): (
        "Lease Renewal=UNCOLORED | Rent Follow-Up=UNCOLORED | "
        "Maintenance Follow-Up=UNCOLORED | Inspection=UNCOLORED | "
        "Vendor Follow-Up=UNCOLORED | PM Handoff=UNCOLORED | "
        "Accounting=UNCOLORED | Legal/Notice=UNCOLORED | "
        "Admin=UNCOLORED | Other=UNCOLORED"
    ),
    ("Maintenance Requests", "Case Origin"): (
        "Email=UNCOLORED | Phone=UNCOLORED | Web=UNCOLORED | "
        "Tenant Portal=UNCOLORED | Text=UNCOLORED | "
        "Landlord Created=UNCOLORED | Inspection=UNCOLORED"
    ),
    ("Maintenance Requests", "Priority"): (
        "High=UNCOLORED | Medium=UNCOLORED | Low=UNCOLORED | "
        "Emergency=UNCOLORED | Normal=UNCOLORED"
    ),
    ("Maintenance Requests", "Status"): (
        "New=UNCOLORED | Escalated=UNCOLORED | On Hold=UNCOLORED | "
        "Closed=UNCOLORED | Triage=UNCOLORED | Scheduled=UNCOLORED | "
        "Waiting on Tenant=UNCOLORED | Waiting on Vendor=UNCOLORED | "
        "In Progress=UNCOLORED | Completed=UNCOLORED | Cancelled=UNCOLORED"
    ),
    ("Tasks", "Priority"): (
        "High=UNCOLORED | Highest=UNCOLORED | Low=UNCOLORED | "
        "Lowest=UNCOLORED | Normal=UNCOLORED | Emergency=UNCOLORED"
    ),
}

LIVE_UNCOLORED_PICKLIST_SCOPES = {
    "module_local_live_uncolored",
    "standard_module_live_uncolored",
    "global_live_uncolored",
}
GOVERNED_LIVE_CHOICE_SCOPES = {
    ("Rental Applications", "Decision"): "local_module",
    ("Rental Applications", "Addenda Required"): "local_module",
    ("Leases", "Lease Type"): "local_module",
    ("Leases", "Addenda Required"): "local_module",
    ("Leases", "Lease Status"): "local_module",
    ("Contacts", "Primary Language"): "module_local_live_uncolored",
    ("Contacts", "Portal Invite Status"): "module_local_live_uncolored",
    ("Properties", "Property Status"): "global_live_uncolored",
    ("Units", "Move-In Checklist Status"): "module_local_live_uncolored",
    ("Units", "Market Status"): "module_local_live_uncolored",
    ("Units", "Unit Status"): "local_module",
    (
        "Maintenance Requests",
        "Access Permission",
    ): "module_local_live_uncolored",
    (
        "Maintenance Requests",
        "Maintenance Category",
    ): "module_local_live_uncolored",
    ("Inspections", "Inspection Type"): "module_local_live_uncolored",
    ("Inspections", "Status"): "module_local_live_uncolored",
    ("Vendors", "Vendor Status"): "global_live_uncolored",
    ("Tasks", "Task Category"): "module_local_live_uncolored",
    ("Maintenance Requests", "Case Origin"): "standard_module_live_uncolored",
    ("Maintenance Requests", "Priority"): "standard_module_live_uncolored",
    ("Maintenance Requests", "Status"): "standard_module_live_uncolored",
    ("Tasks", "Priority"): "standard_module_live_uncolored",
}

GOVERNED_LIVE_SENTINEL_READBACK = {
    ("Maintenance Requests", "Case Origin"): (
        "Exact live readback order including platform sentinel: "
        "-None-, Email, Phone, Web, Tenant Portal, Text, Landlord Created, "
        "Inspection."
    ),
    ("Maintenance Requests", "Priority"): (
        "Exact live readback order including platform sentinel: "
        "-None-, High, Medium, Low, Emergency, Normal."
    ),
    ("Units", "Unit Status"): (
        "Exact live readback order including platform sentinel: "
        "-None-, Occupied, Vacant - Ready, Vacant - Needs Turnover, "
        "Under Renovation, Reserved, Inactive."
    ),
}

# Fail-closed policy notes for live fields whose existence does not establish
# synchronization, legal consent, signature evidence, or financial authority.
GOVERNED_POLICY_NOTE_REQUIREMENTS = {
    ("Contacts", "Email Operational Consent?"): (
        "history tracking is off",
        "no consent source/timestamp/revocation evidence",
        "Never use as marketing-consent proof or sole messaging authorization",
    ),
    ("Contacts", "SMS Operational Consent?"): (
        "history tracking is off",
        "no consent source/timestamp/revocation evidence",
        "Never use as marketing-consent proof or sole messaging authorization",
    ),
    ("Contacts", "Current Lease"): (
        "Non-authoritative convenience field",
        "no sync automation is verified",
        "Leases owns tenancy and lease history",
        "Zoho Books owns invoice/payment/balance truth",
        "Do not treat this value as automatically current",
    ),
    ("Contacts", "Current Unit"): (
        "Non-authoritative convenience field",
        "no sync automation is verified",
        "Leases owns tenancy and lease history",
        "Zoho Books owns invoice/payment/balance truth",
        "Do not treat this value as automatically current",
    ),
    ("Rental Applications", "Zoho Creator Application ID"): (
        "optional Single Line field",
        "verified uniqueness is not enabled",
        "Prohibited as the sole upsert/idempotency key",
        "collision/duplicate handling",
        "post-write readback",
    ),
    ("Units", "Current Lease"): (
        "Non-authoritative convenience field",
        "no sync automation is verified",
        "Leases owns tenancy and lease history",
        "Zoho Books owns invoice/payment/balance truth",
        "Do not treat this value as automatically current",
    ),
    ("Units", "Current Lease End Date"): (
        "Non-authoritative convenience snapshot",
        "no sync automation is verified",
        "Leases owns tenancy and lease history",
        "Zoho Books owns invoice/payment/balance truth",
        "Do not treat this value as automatically current",
    ),
    ("Units", "Current Base Rent"): (
        "Optional editable planning snapshot only",
        "no sync automation is verified",
        "Never use as payment/Books evidence or an enforceable tenant amount",
        "never copy or charge it automatically",
        "Leases owns tenancy and lease history",
        "Zoho Books owns invoice/payment/balance truth",
        "furnished/deposit-cap review where applicable",
    ),
    ("Units", "Security Deposit Default"): (
        "Optional editable planning/default snapshot only",
        "Never use as payment/Books evidence or an enforceable tenant amount",
        "never copy or charge it automatically",
        "furnished/deposit-cap review where applicable",
    ),
    ("Maintenance Requests", "Creator Ticket ID"): (
        "optional Single Line field",
        "verified uniqueness is not enabled",
        "Prohibited as the sole upsert/idempotency key",
        "collision/duplicate handling",
        "post-write readback",
    ),
    ("Inspections", "Tenant Signed?"): (
        "Manual operational checkbox only",
        "no Zoho Sign evidence integration is verified",
        "Never treat as signature or enforcement proof",
    ),
    ("Inspections", "Landlord Signed?"): (
        "Manual operational checkbox only",
        "no Zoho Sign evidence integration is verified",
        "Never treat as signature or enforcement proof",
    ),
}

# Exact global-picklist associations represented by verified live CSV rows.
# Other associations remain governed by the separate global-picklist registry.
GLOBAL_LIVE_PICKLIST_ASSOCIATIONS = {
    ("Properties", "State"): "States",
    ("Properties", "Property Status"): "GH_Lifecycle_Status",
    ("Vendors", "Vendor Status"): "GH_Lifecycle_Status",
}

# These reviewed live-reuse and ownership decisions prevent future catalog
# consumers from treating duplicate-prone historical proposals as build work.
NO_DUPLICATE_DECISIONS = {
    ("Contacts", "Preferred Contact Method"): (
        "blocked_ambiguous",
        "blocked_ambiguous",
    ),
    ("Contacts", "Secondary Phone"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Contacts", "Contact Role Type"): (
        "blocked_ambiguous",
        "blocked_ambiguous",
    ),
    ("Contacts", "Contact Status"): (
        "blocked_ambiguous",
        "blocked_ambiguous",
    ),
    ("Contacts", "Legal First Name"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Contacts", "Legal Last Name"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Contacts", "Legal Middle Name"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Contacts", "Zoho Books Customer ID"): (
        "blocked_ambiguous",
        "blocked_ambiguous",
    ),
    ("Contacts", "Zoho Contracts Counterparty ID"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Properties", "Notice Phone"): (
        "blocked_ambiguous",
        "blocked_ambiguous",
    ),
    ("Properties", "Property Manager Name"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Properties", "Property Manager User"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Properties", "Property Type"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Units", "Occupancy Status"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Units", "WorkDrive Unit Folder"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Inspections", "Inspection PDF Link"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Inspections", "Photo Folder Link"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Inspections", "Inspection Status"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
    ("Inspections", "Tenant Contact"): (
        "superseded_by_verified_live_mcp_field",
        "do_not_create",
    ),
}


def parse_args() -> argparse.Namespace:
    default_path = (
        Path(__file__).resolve().parents[1]
        / "field-maps"
        / "crm-module-fields"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "catalog_dir",
        nargs="?",
        type=Path,
        default=default_path,
        help=f"Directory containing per-module CSV files (default: {default_path})",
    )
    return parser.parse_args()


def validate_api_name(value: str, path: str, errors: list[str]) -> None:
    if value and not API_NAME_RE.fullmatch(value):
        errors.append(f"{path}: invalid Zoho API-name format: {value!r}")


def parse_choices(
    value: str,
    path: str,
    errors: list[str],
    *,
    allow_uncolored: bool = False,
) -> list[tuple[str, str]]:
    if not value.strip():
        return []
    choices: list[tuple[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value.split(" | "), start=1):
        item = raw.strip()
        if "=" not in item:
            errors.append(f"{path}: choice {index} must use Label=#RRGGBB")
            continue
        label, color = item.rsplit("=", 1)
        label = label.strip()
        color = color.strip()
        if not label:
            errors.append(f"{path}: choice {index} has an empty label")
        folded = label.casefold()
        if folded in seen:
            errors.append(f"{path}: duplicate choice label {label!r}")
        seen.add(folded)
        if color == "UNCOLORED" and allow_uncolored:
            pass
        elif not HEX_COLOR_RE.fullmatch(color):
            errors.append(f"{path}: choice {label!r} has invalid color {color!r}")
        choices.append((label, color.upper()))
    return choices


def load_catalog_dir(path: Path) -> list[tuple[Path, dict[str, str]]]:
    if not path.is_dir():
        raise ValueError(f"catalog directory not found: {path}")
    csv_paths = sorted(path.glob("*.csv"))
    if not csv_paths:
        raise ValueError(f"no module CSV files found in: {path}")

    loaded: list[tuple[Path, dict[str, str]]] = []
    for csv_path in csv_paths:
        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                missing = sorted(REQUIRED_COLUMNS.difference(headers))
                if missing:
                    raise ValueError(
                        f"{csv_path}: missing required columns: {', '.join(missing)}"
                    )
                rows = []
                for row_number, row in enumerate(reader, start=2):
                    if None in row:
                        raise ValueError(
                            f"{csv_path}: row {row_number} has extra CSV columns"
                        )
                    if any(value is None for value in row.values()):
                        raise ValueError(
                            f"{csv_path}: row {row_number} has missing CSV columns"
                        )
                    rows.append(
                        {key: (value or "").strip() for key, value in row.items()}
                    )
        except csv.Error as exc:
            raise ValueError(f"{csv_path}: invalid CSV: {exc}") from exc
        if not rows:
            raise ValueError(f"{csv_path}: must contain at least one field row")
        labels = {row["module_display_label"] for row in rows}
        if len(labels) != 1:
            raise ValueError(
                f"{csv_path}: expected exactly one module label, found {sorted(labels)}"
            )
        loaded.extend((csv_path, row) for row in rows)
    return loaded


def governed_live_snapshot_digest(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
) -> tuple[int, str]:
    """Return a deterministic digest of every governed live-readback CSV fact."""

    columns = sorted(REQUIRED_COLUMNS)
    rows = [
        {column: row[column] for column in columns}
        for _, row in rows_with_paths
        if row["api_name_status"] == "verified_live_mcp"
    ]
    rows.sort(
        key=lambda row: (
            row["module_display_label"].casefold(),
            row["field_label"].casefold(),
            row["api_name"],
        )
    )
    payload = json.dumps(
        rows,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return len(rows), hashlib.sha256(payload).hexdigest()


def validate_governed_live_snapshot(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Fail on any drift in the complete sanitized governed live snapshot."""

    count, digest = governed_live_snapshot_digest(rows_with_paths)
    if count != GOVERNED_LIVE_SNAPSHOT_COUNT:
        errors.append(
            "governed live snapshot: expected "
            f"{GOVERNED_LIVE_SNAPSHOT_COUNT} verified_live_mcp rows, found {count}"
        )
    if digest != GOVERNED_LIVE_SNAPSHOT_SHA256:
        errors.append(
            "governed live snapshot: canonical CSV facts drifted "
            f"(expected {GOVERNED_LIVE_SNAPSHOT_SHA256}, found {digest})"
        )


def validate_governed_live_manifest(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Protect the exact governed production field identities and placements."""

    manifest_keys = {
        (module_label, field_label)
        for module_label, _, manifest in GOVERNED_LIVE_MANIFEST
        for field_label, _, _ in manifest
    }
    if set(GOVERNED_LIVE_FIELD_TYPES) != manifest_keys:
        errors.append(
            "validator invariant: governed live field-type coverage does not "
            "exactly match the governed manifest"
        )
    lookup_keys = {
        key
        for key, field_type in GOVERNED_LIVE_FIELD_TYPES.items()
        if field_type == "Lookup"
    }
    if set(GOVERNED_LIVE_LOOKUP_TARGETS) != lookup_keys:
        errors.append(
            "validator invariant: governed live lookup-target coverage does not "
            "exactly match the 2026-07-24 lookup fields"
        )
    choice_keys = {
        key
        for key, field_type in GOVERNED_LIVE_FIELD_TYPES.items()
        if field_type
        in {"Pick List", "Pick List / Standard", "Multi-Select Pick List"}
    }
    if set(GOVERNED_LIVE_CHOICES) != choice_keys:
        errors.append(
            "validator invariant: governed live choice coverage does not exactly "
            "match the governed choice fields"
        )
    if set(GOVERNED_LIVE_CHOICE_SCOPES) != choice_keys:
        errors.append(
            "validator invariant: governed live choice-scope coverage does not "
            "exactly match the governed choice fields"
        )
    if not set(GOVERNED_LIVE_SENTINEL_READBACK).issubset(choice_keys):
        errors.append(
            "validator invariant: governed live sentinel evidence references "
            "a field outside the governed choice manifest"
        )
    if not set(GOVERNED_POLICY_NOTE_REQUIREMENTS).issubset(manifest_keys):
        errors.append(
            "validator invariant: governed policy-note evidence references "
            "a field outside the governed live manifest"
        )

    rows_by_field: dict[
        tuple[str, str], list[tuple[Path, dict[str, str]]]
    ] = defaultdict(list)
    for csv_path, row in rows_with_paths:
        key = (
            row["module_display_label"].casefold(),
            row["field_label"].casefold(),
        )
        rows_by_field[key].append((csv_path, row))

    for module_label, module_api_name, manifest in GOVERNED_LIVE_MANIFEST:
        for field_label, api_name, section in manifest:
            key = (module_label.casefold(), field_label.casefold())
            matches = rows_by_field.get(key, [])
            manifest_path = (
                f"governed live manifest: {module_label}.{field_label}"
            )
            if not matches:
                errors.append(f"{manifest_path}: required catalog row is missing")
                continue
            if len(matches) != 1:
                errors.append(
                    f"{manifest_path}: expected exactly one catalog row, "
                    f"found {len(matches)}"
                )
                continue

            csv_path, row = matches[0]
            expected_values = {
                "module_display_label": module_label,
                "module_api_name": module_api_name,
                "field_label": field_label,
                "field_type": GOVERNED_LIVE_FIELD_TYPES[
                    (module_label, field_label)
                ],
                "api_name": api_name,
                "api_name_status": "verified_live_mcp",
                "disposition": "governed_current",
                "section": section,
            }
            for column, expected in expected_values.items():
                actual = row[column]
                if actual != expected:
                    errors.append(
                        f"{csv_path.name}: {manifest_path}.{column}: "
                        f"expected {expected!r}, found {actual!r}"
                    )

            source_ids = {
                item.strip()
                for item in row["source_ids"].split(",")
                if item.strip()
            }
            if source_ids.isdisjoint(LIVE_MCP_SOURCE_IDS):
                errors.append(
                    f"{csv_path.name}: {manifest_path}.source_ids: "
                    "expected a governed LIVE_CRM_MCP evidence source"
                )

            lookup_target = GOVERNED_LIVE_LOOKUP_TARGETS.get(
                (module_label, field_label)
            )
            if lookup_target is not None:
                lookup_pattern = (
                    rf"\blookup (?:target |to ){re.escape(lookup_target)}\b"
                )
                if not re.search(lookup_pattern, row["notes"], re.IGNORECASE):
                    errors.append(
                        f"{csv_path.name}: {manifest_path}.notes: expected "
                        f"readback evidence for lookup target {lookup_target!r}"
                    )

            expected_choices = GOVERNED_LIVE_CHOICES.get(
                (module_label, field_label)
            )
            if (
                expected_choices is not None
                and row["picklist_values_and_colors"] != expected_choices
            ):
                errors.append(
                    f"{csv_path.name}: {manifest_path}."
                    "picklist_values_and_colors: exact live choices/order/colors "
                    "drifted"
                )
            expected_choice_scope = GOVERNED_LIVE_CHOICE_SCOPES.get(
                (module_label, field_label)
            )
            if (
                expected_choice_scope is not None
                and row["picklist_scope"] != expected_choice_scope
            ):
                errors.append(
                    f"{csv_path.name}: {manifest_path}.picklist_scope: expected "
                    f"{expected_choice_scope!r}, found {row['picklist_scope']!r}"
                )
            expected_sentinel_readback = GOVERNED_LIVE_SENTINEL_READBACK.get(
                (module_label, field_label)
            )
            if (
                expected_sentinel_readback is not None
                and expected_sentinel_readback not in row["notes"]
            ):
                errors.append(
                    f"{csv_path.name}: {manifest_path}.notes: expected exact "
                    "platform-sentinel readback order"
                )
            for required_note in GOVERNED_POLICY_NOTE_REQUIREMENTS.get(
                (module_label, field_label),
                (),
            ):
                if required_note not in row["notes"]:
                    errors.append(
                        f"{csv_path.name}: {manifest_path}.notes: expected "
                        f"policy warning {required_note!r}"
                    )


def validate_no_duplicate_decisions(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Keep reviewed duplicate-prone proposals out of future build manifests."""

    rows_by_field: dict[
        tuple[str, str], list[tuple[Path, dict[str, str]]]
    ] = defaultdict(list)
    for csv_path, row in rows_with_paths:
        key = (
            row["module_display_label"].casefold(),
            row["field_label"].casefold(),
        )
        rows_by_field[key].append((csv_path, row))

    for (module_label, field_label), (
        expected_status,
        expected_disposition,
    ) in NO_DUPLICATE_DECISIONS.items():
        key = (module_label.casefold(), field_label.casefold())
        matches = rows_by_field.get(key, [])
        decision_path = f"no-duplicate decision: {module_label}.{field_label}"
        if not matches:
            errors.append(f"{decision_path}: required catalog row is missing")
            continue
        if len(matches) != 1:
            errors.append(
                f"{decision_path}: expected exactly one catalog row, "
                f"found {len(matches)}"
            )
            continue

        csv_path, row = matches[0]
        if row["api_name_status"] != expected_status:
            errors.append(
                f"{csv_path.name}: {decision_path}.api_name_status: expected "
                f"{expected_status!r}, found {row['api_name_status']!r}"
            )
        if row["disposition"] != expected_disposition:
            errors.append(
                f"{csv_path.name}: {decision_path}.disposition: expected "
                f"{expected_disposition!r}, found {row['disposition']!r}"
            )
        source_ids = {
            item.strip()
            for item in row["source_ids"].split(",")
            if item.strip()
        }
        if "LIVE_CRM_MCP_2026-07-24" not in source_ids:
            errors.append(
                f"{csv_path.name}: {decision_path}.source_ids: expected "
                "LIVE_CRM_MCP_2026-07-24"
            )
        if "do not create" not in row["notes"].casefold():
            errors.append(
                f"{csv_path.name}: {decision_path}.notes: expected explicit "
                "do-not-create instruction"
            )


def validate_global_live_picklist_associations(
    rows_with_paths: list[tuple[Path, dict[str, str]]],
    errors: list[str],
) -> None:
    """Protect exact global-set ownership for live choice rows in the CSVs."""

    rows_by_field: dict[
        tuple[str, str], list[tuple[Path, dict[str, str]]]
    ] = defaultdict(list)
    observed_global_scope: set[tuple[str, str]] = set()
    for csv_path, row in rows_with_paths:
        key = (row["module_display_label"], row["field_label"])
        rows_by_field[key].append((csv_path, row))
        if (
            row["api_name_status"] == "verified_live_mcp"
            and row["picklist_scope"] == "global_live_uncolored"
        ):
            observed_global_scope.add(key)

    expected_keys = set(GLOBAL_LIVE_PICKLIST_ASSOCIATIONS)
    if observed_global_scope != expected_keys:
        errors.append(
            "global live picklist association invariant: CSV global-scope "
            f"keys {sorted(observed_global_scope)!r} do not match governed "
            f"keys {sorted(expected_keys)!r}"
        )

    for key, global_api_name in GLOBAL_LIVE_PICKLIST_ASSOCIATIONS.items():
        module_label, field_label = key
        matches = rows_by_field.get(key, [])
        association_path = (
            f"global live picklist association: {module_label}.{field_label}"
        )
        if not matches:
            errors.append(f"{association_path}: required catalog row is missing")
            continue
        if len(matches) != 1:
            errors.append(
                f"{association_path}: expected exactly one catalog row, "
                f"found {len(matches)}"
            )
            continue

        csv_path, row = matches[0]
        if row["api_name_status"] != "verified_live_mcp":
            errors.append(
                f"{csv_path.name}: {association_path}.api_name_status: "
                "expected 'verified_live_mcp'"
            )
        if row["picklist_scope"] != "global_live_uncolored":
            errors.append(
                f"{csv_path.name}: {association_path}.picklist_scope: "
                "expected 'global_live_uncolored'"
            )
        if global_api_name not in row["notes"]:
            errors.append(
                f"{csv_path.name}: {association_path}.notes: expected global "
                f"picklist API name {global_api_name!r}"
            )
        source_ids = {
            item.strip()
            for item in row["source_ids"].split(",")
            if item.strip()
        }
        if "LIVE_CRM_MCP_2026-07-24" not in source_ids:
            errors.append(
                f"{csv_path.name}: {association_path}.source_ids: expected "
                "LIVE_CRM_MCP_2026-07-24"
            )


def validate_rows(rows_with_paths: list[tuple[Path, dict[str, str]]]) -> list[str]:
    errors: list[str] = []
    module_facts: dict[str, tuple[str, str, str]] = {}
    module_display_names: set[str] = set()
    field_labels: dict[str, set[str]] = defaultdict(set)
    verified_api_names: dict[str, set[str]] = defaultdict(set)
    row_numbers: dict[Path, int] = defaultdict(lambda: 1)

    for csv_path, row in rows_with_paths:
        row_numbers[csv_path] += 1
        path = f"{csv_path.name}:row {row_numbers[csv_path]}"
        module_label = row["module_display_label"]
        module_type = row["module_type"]
        module_api_name = row["module_api_name"]
        module_api_status = row["module_api_name_status"]
        field_label = row["field_label"]
        field_type = row["field_type"]
        api_name = row["api_name"]
        api_status = row["api_name_status"]
        proposed_api_name = row["proposed_api_name"]
        disposition = row["disposition"]
        help_text = row["help_text"]
        source_ids = [item for item in row["source_ids"].split(",") if item]

        for column, value in (
            ("module_display_label", module_label),
            ("module_type", module_type),
            ("module_api_name_status", module_api_status),
            ("field_label", field_label),
            ("field_type", field_type),
            ("api_name_status", api_status),
            ("disposition", disposition),
            ("help_text", help_text),
        ):
            if not value:
                errors.append(f"{path}.{column}: required value is blank")

        if not source_ids:
            errors.append(f"{path}.source_ids: at least one source ID is required")
        for source_id in source_ids:
            if source_id not in KNOWN_SOURCE_IDS:
                errors.append(f"{path}.source_ids: unknown source ID {source_id!r}")

        if len(help_text) > 255:
            errors.append(
                f"{path}.help_text: {len(help_text)} characters exceeds GH maximum 255"
            )

        validate_api_name(module_api_name, f"{path}.module_api_name", errors)
        validate_api_name(api_name, f"{path}.api_name", errors)
        validate_api_name(proposed_api_name, f"{path}.proposed_api_name", errors)

        if module_api_status in VERIFIED_MODULE_STATUSES and not module_api_name:
            errors.append(f"{path}: verified module status requires module_api_name")
        if api_status in VERIFIED_FIELD_STATUSES and not api_name:
            errors.append(f"{path}: verified field status requires api_name")
        if (
            api_status == "verified_live_mcp"
            and not LIVE_MCP_SOURCE_IDS.intersection(source_ids)
        ):
            errors.append(
                f"{path}: verified_live_mcp requires "
                "a governed LIVE_CRM_MCP source ID"
            )
        if api_status == "proposed_unverified" and not proposed_api_name:
            errors.append(f"{path}: proposed_unverified requires proposed_api_name")
        if api_status == "not_proposed_unverified" and api_name:
            errors.append(f"{path}: not_proposed_unverified must not claim api_name")

        module_key = module_label.casefold()
        module_display_names.add(module_label)
        module_fact = (module_type, module_api_name, module_api_status)
        previous_fact = module_facts.setdefault(module_key, module_fact)
        if previous_fact != module_fact:
            errors.append(f"{path}: module metadata conflicts with earlier rows")

        folded_label = field_label.casefold()
        if folded_label in field_labels[module_key]:
            errors.append(f"{path}.field_label: duplicate {field_label!r} in module")
        field_labels[module_key].add(folded_label)

        if api_status in VERIFIED_FIELD_STATUSES and api_name:
            folded_api = api_name.casefold()
            if folded_api in verified_api_names[module_key]:
                errors.append(
                    f"{path}.api_name: duplicate verified API name {api_name!r} in module"
                )
            verified_api_names[module_key].add(folded_api)

        choices = parse_choices(
            row["picklist_values_and_colors"],
            f"{path}.picklist_values_and_colors",
            errors,
            allow_uncolored=(
                api_status == "verified_live_mcp"
                and row["picklist_scope"] in LIVE_UNCOLORED_PICKLIST_SCOPES
            ),
        )
        is_choice_type = "pick" in field_type.casefold() or "multi-select" in field_type.casefold()
        if is_choice_type and not choices:
            errors.append(f"{path}: choice field is missing choices and #RRGGBB colors")
        if choices and not row["picklist_scope"]:
            errors.append(f"{path}: choice field is missing picklist_scope")

        if row["required"].casefold() not in {"true", "false"}:
            errors.append(f"{path}.required: expected true or false")

    missing_modules = sorted(REQUIRED_CURRENT_MODULES.difference(module_display_names))
    if missing_modules:
        errors.append(f"catalog is missing current modules: {', '.join(missing_modules)}")
    validate_governed_live_snapshot(rows_with_paths, errors)
    validate_governed_live_manifest(rows_with_paths, errors)
    validate_global_live_picklist_associations(rows_with_paths, errors)
    validate_no_duplicate_decisions(rows_with_paths, errors)
    return errors


def main() -> int:
    args = parse_args()
    try:
        rows_with_paths = load_catalog_dir(args.catalog_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = validate_rows(rows_with_paths)
    if errors:
        print(
            f"CRM field catalog validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    rows = [row for _, row in rows_with_paths]
    module_count = len({row["module_display_label"].casefold() for row in rows})
    picklist_count = sum(bool(row["picklist_values_and_colors"]) for row in rows)
    api_status_counts = Counter(row["api_name_status"] for row in rows)
    print(
        "CRM field catalog valid: "
        f"{module_count} modules, {len(rows)} fields, {picklist_count} choice fields."
    )
    print("Field API-name statuses:")
    for status, count in sorted(api_status_counts.items()):
        print(f"- {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
