(function () {
    'use strict';

    var _t = openerp._t;
    openerp.Tour.register({
        id: 'junior_doctor_able_to_update_patient_clerking_in_progress_stage',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',
        steps: [
            {
                title:     _t("Login page Loaded"),
                element:   '.oe_topbar_name',
                content:   _t("Logged in as Junior Doctor"),
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Referral board is loaded, each patient is presented by index card"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Clerk patient"),
                content:   _t("Click on 'Clerk' button to clerk the patient"),
                element:   'td.oe_kanban_column:nth-child(3) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Diagnosis"),
                content:   _t("Diagnosis"),
                element:   'label:contains("Diagnosis:")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Enter Plans"),
                content:   _t("Enter Plans"),
                element:   'label:contains("Plan:")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Save"),
                content:   _t("Click on Save button to Save Diagnosis and Plans you have entered"),
                element:   '.oe_form_button_save',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("patient stage updated"),
                content:   _t(" Patient has moved to 'clerking in progress stage, Click on Referral Board'"),
                waitFor:   ('td.oe_kanban_column:nth-child(4) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Referral board is loaded, each patient is presented by index card"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   {next: _t("Next"), end:_t("End")}
            },
        ]
    });
}());