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
                title:     _t("Login"),
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
                content:   _t("Click on 'Clerk' button to clerk the patient, patient will moved to clerking in progress stage'"),
                element:   'td.oe_kanban_column:nth-child(3) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Diagnosis"),
                content:   _t("Enter Diagnosis"),
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
                content:   _t(" Patient has moved to 'clerking in progress stage'"),
                waitFor:   ('td.oe_kanban_column:nth-child(4) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Edit"),
                content:   _t("Click on 'Edit' button if you wish to edit Diagnosis and Plan when patient is in 'Clerking in Progress' stage"),
                element:   '.oe_button.oe_form_button_edit',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Save"),
                content:   _t("Click on Save button to Save Diagnosis and Plans you have entered"),
                element:   '.oe_form_button_save',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Create Tasks"),
                content:   _t("Click on create Task"),
                element:   'span:contains("Create Task")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Task Name"),
                content:   _t("Click on create Task"),
                waitFor:   'label:contains("Task Name")',
                popover:   { fixed: true }
            },
            {
                title:     _t("Blocking Task "),
                content:   _t("Tick the checkbox if you wish to create blocking tasks, i.e tasks which needs to be finished before patient discharge"),
                waitFor:   'label:contains("Blocking")',
                popover:   { fixed: true }
            },
            {
                title:     _t("Submit"),
                content:   _t("Click on create Task"),
                element:   'span:contains("Submit")',
                placement: 'left',
                popover:   { fixed: true }
            },
            {
                title:     _t("Complete Clerking"),
                content:   _t("Click on 'Complete Clerking button to complete clerking, if you complete clerking patient will be moved to senior review stage'"),
                element:   'span:contains("Submit")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("patient stage updated"),
                content:   _t(" Patient has moved to 'Senior Review stage'"),
                waitFor:   ('td.oe_kanban_column:nth-child(5) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Click on <b>Referral Board</b> to go back to referral board"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   {next: _t("Next"), end:_t("End")}
            },
        ]
    });
}());