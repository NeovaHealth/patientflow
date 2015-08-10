(function () {
    'use strict';
 
    var _t = openerp._t;
 
 
    openerp.Tour.register({
        id: 'referral_nurse_able_to_create_referral',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',
 

        steps: [
 
            {
                title:     _t("Login page"),
                element:   '.oe_topbar_name',
                content:   _t("You are Logged in as Taylor"),
                popover:   { next: _t("Next")}
            },
 
            {
                title:     _t("Referral form"),
                element:   '.oe_menu_text:contains("Referral Forms")',
                content:   _t("Click on referral forms"),
                popover:   { next: _t("Next")}
            },
 
            {
                title:     _t("Create Referral"),
                element:   '.oe_button.oe_list_add.oe_highlight:contains("Create")',
                content:   _t("Click on <b>Create</b> button to create referral"),
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Select Patient"),
                element:   '.oe_horizontal_separator.oe_clear:contains("Patient Details")',
                popover:   { next: _t("Next")},
                content:   _t("Select patient from drop down or enter patient details"),
                sampleText: 'Klocko, Lindell'
            },

            {
                title:     _t("Enter Symptoms"),
                element:   'textarea[name=symptoms_notes]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Symptoms"),
                sampleText: 'Test Symptom Notes'
            },
            {
                title:     _t("Enter Medical History"),
                element:   'textarea[name=medical_history_notes]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Medical History"),
                sampleText: 'Test Medical History Notes'
            },
            {
                title:     _t("Enter Allergies"),
                element:   'textarea[name=allergies]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Allergies"),
                sampleText: 'Test Allergies'
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save',
                content:   _t("Click on save button"),
                popover:   { next: _t("Next")}
            },

            {
                title:     _t("Referral Created"),
                waitFor:   ('td.oe_kanban_column:nth-child(1) div.oe_fold_column.oe_kanban_record').length + 1
            }
 
        ]
    });
 
}());
