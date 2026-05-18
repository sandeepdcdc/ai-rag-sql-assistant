business_schema = {

    "dc_patient_billing": [
        "patient_id",
        "p_first_name",
        "p_last_name",
        "branch_id",
        "branch_name",
        "billing_date"
    ],

    "dc_branch": [
        "branch_id",
        "branch_name",
        "state_id",
        "city_name",
        "is_active"
    ],

    "dc_states": [
        "state_id",
        "state_name"
    ],

    "dc_patients": [
        "patient_id",
        "patient_status_id",
        "branch_id",
        "full_name",
        "gender",
        "mobile_no",
        "dob",
        "status_id",
        "inactive_reason_id"
    ],

    "dc_patient_permission": [
        "patient_id",
        "dialysis_per_week"
    ]
}

relationships = """

1. dc_patient_billing.branch_id = dc_branch.branch_id

2. dc_branch.state_id = dc_states.state_id

3. dc_patients.branch_id = dc_branch.branch_id

4. dc_patient_permission.patient_id = dc_patients.patient_id

5. dc_patient_billing.patient_id = dc_patients.patient_id

"""