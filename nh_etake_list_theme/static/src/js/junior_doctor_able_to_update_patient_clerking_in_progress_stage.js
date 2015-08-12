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
                title:     _t("Referral Board Loaded"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Clerk patient(click on 'Clerk'  button)"),
                element:   'td.oe_kanban_column:nth-child(3) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Enter Diagnosis"),
                element:   '.oe_form_label.oe_align_right label[for=oe-field-input-23]',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Enter Plans"),
                element:   'label[for=oe-field-input-36].oe_form_label.oe_align_right',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("patient stage updated to 'clerking in progress stage' "),
                waitFor:   ('td.oe_kanban_column:nth-child(4) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next")}
            }
        ]
    });
}());