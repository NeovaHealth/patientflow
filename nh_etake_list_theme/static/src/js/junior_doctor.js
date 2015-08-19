(function () {
    'use strict';

    var _t = openerp._t;
    openerp.Tour.register({
        id: 'junior_doctor',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',
        steps: [
            {
                title:     _t("Login"),
                element:   '.oe_topbar_name',
                content:   _t("You are logged in as a Junior Doctor"),
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("The <b>Referral Board</b> shows each patient represented by an index card in their current referral stage"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Click on Arrived Button"),
                element:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")},
                content: _t("Notify patient arrival by clicking on <b>Arrived</b>  button")

            },
            {
               title:     _t("patient arrival updated"),
               waitFor:   ('td.oe_kanban_column:nth-child(3) div.oe_fold_column.oe_kanban_record').length + 1,
               popover:   { next: _t("Next"), end: _t('End')},
               content: _t("patient arrival updated and patient is in To be clerked stage")

            },
            {
                title:     _t("Clerk patient"),
                content:   _t("Click on: <b>Clerk</b> button to clerk a patient. The patient will moved to the <b>Clerking in Progress</b> stage"),
                element:   'td.oe_kanban_column:nth-child(3) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Diagnosis"),
                content:   _t("Enter Diagnosis as free text"),
                element:   'label:contains("Diagnosis:")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Enter Plans"),
                content:   _t("Enter Plans as free text"),
                element:   'label:contains("Plan:")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Save"),
                content:   _t("Click on <b>Save</b> button to save the Diagnosis and Plans you have entered"),
                element:   '.oe_form_button_save',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Edit"),
                content:   _t("Click on <b>Edit</b> button if you wish to edit Diagnosis and Plan when patient is in <b>Clerking in Progress</b> stage"),
                element:   '.oe_button.oe_form_button_edit',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Save"),
                content:   _t("Click on Save button to save the updated Diagnosis and Plans you have entered"),
                element:   '.oe_form_button_save',
                popover:   {  next: _t("Next")}
            },
            {
                title:     _t("Create Tasks"),
                content:   _t("Click on <b>Create Task</b> button"),
                element:   'span:contains("Create Task")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Task Name"),
                content:   _t("Enter Task Name, Example: Urine Test"),
                placement: 'left',
                element:   'label:contains("Task Name")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Blocking Task "),
                content:   _t("Tick the checkbox if you wish to create blocking tasks i.e. tasks which need to be finished before patient discharge."),
                element:   'label:contains("Blocking")',
                placement: 'left',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Submit"),
                content:   _t("Click <b>Submit</b> to create Task"),
                element:   'span:contains("Submit")',
                placement: 'left',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Complete Clerking"),
                content:   _t("Click on: <b>Complete Clerking</b> button to complete clerking.<br>Completing clerking will move patient to the <b>Senior Review</b> stage'"),
                element:   'span:contains("Complete Clerking")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Click on: <b>Referral Board</b>"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Patient stage updated"),
                content:   _t(" Patient has moved to <b>Senior Review</b> stage"),
                waitfor:   ('td.oe_kanban_column:nth-child(5) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next"), End: _t("End")}
            }
        ]
    });
}());