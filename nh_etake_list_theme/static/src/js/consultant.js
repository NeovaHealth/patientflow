/**
 * Created by amipatel on 18/08/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;
    openerp.Tour.register({
        id: 'consultant',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',

        // TODO : identify menu by data-menu attr or text node ?
        steps: [
            {
                title:     _t("Login page"),
                element:   '.oe_topbar_name',
                content:   _t("You are Logged in as Consultant"),
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Referral form"),
                element:   '.oe_menu_text:contains("Referral Forms")',
                content:   _t("Click on <b>Referral forms</b> button to create new referral"),
                popover:   { next: _t("Next")}
            },
            //Create Referral
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
                sampleText: 'Klocko, Lindell',
                //alignment:  Top
            },
            {
                title:     _t("Enter Symptoms"),
                element:   'textarea[name=symptoms_notes]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Symptoms as free text"),
                sampleText: 'Test Symptom Notes'
            },
            {
                title:     _t("Enter Medical History"),
                element:   'textarea[name=medical_history_notes]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Medical History as free text"),
                sampleText: 'Test Medical History Notes'
            },
            {
                title:     _t("Enter Allergies"),
                element:   'textarea[name=allergies]',
                popover:   { next: _t("Next")},
                content:   _t("Enter Allergies as free text"),
                sampleText: 'Test Allergies'
                //alignment: Top
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save',
                content:   _t("Click on <b>Save</b> button"),
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Go to Referral Board"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")},
                content:   _t("<p>If patient referral is created successfully then an index card with patient details is created in the <b>Referral</b> column on the <b>Referral Board</b> page</p>")
            },
            {
                title:     _t("Referral Created"),
                waitFor:   ('td.oe_kanban_column:nth-child(1) div.oe_fold_column.oe_kanban_record').length + 1,
                content:   _t("Patient referral is presented with index card in <b>Referral</b> coulmn.<br>Click on the patient index card from <b>Referral</b> column to accept/reject referral "),
                popover:   { next: _t("Next"), end:_t("End")}
            },
            //Accept Referral
            {
                title:     _t("Accept Referral"),
                element:   '.oe_button.oe_form_button span:contains("Accept")',
                popover:   { next: _t("Next")},
                content:   _t("Click on <b>accept</b> button to accept referral")
            },
            {
                title:     _t("Enter To come in Location"),
                element:   'label:contains("Location To Come In")',
                content:   _t("Enter patient's To come in Location or select location from drop down"),
                placement: 'left',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Click on Submit button"),
                element:   '.oe_button.oe_form_button span:contains("Submit")',
                content:   _t("Click on <b>Submit</b> button.<br>Accepting Patient Referral will move patient <b>To come in stage</b>,"),
                placement: 'left',
                popover:   { next: _t("Next")}
            },
            /*
            {
                title:     _t("Patient has moved to 'To Come in' stage"),
                waitfor:   ('td.oe_kanban_column:nth-child(2) div.oe_fold_column.oe_kanban_record').length + 1,
                content:   _t("After accepting patient referral, Patient will be moved to <b>To Come in</b> stage"),
                placement: 'left',
                popover:   { next: _t("Next")}
            },*/
            //patient arrival
            {
                title:     _t("Click on Arrived Button"),
                element:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")},
                content: _t(" Notify patient arrival by clicking on the <b>Arrived</b>  button")

            },
            {
               title:     _t("patient arrival updated"),
               waitFor:   ('td.oe_kanban_column:nth-child(3) div.oe_fold_column.oe_kanban_record').length + 1,
               popover:   { next: _t("Next"), end: _t('End')},
               content: _t("patient arrival updated and patient is in <b>To be clerked stage</b>")

            },
            //Clerking in progress
            {
                title:     _t("Clerk patient"),
                content:   _t("Click on: <b>Clerk</b> button to clerk a patient. The patient will moved to the <b>Clerking in Progress</b> stage'"),
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
                content:   _t("Click on <b>Save</b> button to save the updated Diagnosis and Plans you have entered"),
                element:   '.oe_form_button_save',
                popover:   { next: _t("Next")}
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
            //complete clerking
            {
                title:     _t("Complete Clerking in progress"),
                content:   _t("Click on: <b>Complete Clerking</b> button to complete clerking. Completing clerking will move patient to the <b>Senior Review</b> stage'"),
                element:   '.oe_button.oe_form_button span:contains("Complete Clerking")',
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
                content:   _t("Patient has moved to <b>Senior Review</b> stage"),
                waitfor:   ('td.oe_kanban_column:nth-child(5) div.oe_fold_column.oe_kanban_record').length + 1,
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Complete Review"),
                content:   _t("Click on the patient index card in <b>Senior Review</b> stage  if you wish to complete review"),
                element:   'td.oe_kanban_column:nth-child(5) .oe_fold_column.oe_kanban_record:first()',
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Complete Review"),
                content:   _t("<li>Click on <b>Complete Review</b> button to complete the senior review, which admits the patient and patient will be in <b>Cosultant Review</b> stage</li><br><b>or</b>" +
                    "<li> Click on <b>To be Discharge</b> button to move patient to <b>To Be Discharged </b>stage</li>"),
                element:   'span:contains("Complete Review"):visible',
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Click on: <b>Referral Board</b>"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")}
            },
            {
                title:     _t("Consultant Review "),
                content:   _t("Click on the patient index card in <b>Senior Review</b> stage  if you wish to complete review.<br><b>Patient will disapear from <b>Referral Board</b> once you click on <b>Complete Review</b></b>"),
                element:   '.oe_button.oe_form_button span:contains("Complete Review"):visible',
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Referral Board"),
                content:   _t("Click on <b>Refferal Board</b> "),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Discharge Patient"),
                content:   _t("Click on <b>Discharge</b> button to discharge patient"),
                element:   '.oe_kanban_column:nth-child(7) .oe_highlight.btn-task.oe_kanban_action.oe_kanban_action_button:first()',
                popover:   { next: _t("Next"), End: _t("End")}
            },
            {
                title:     _t("Discharged"),
                waitFor:   ('td.oe_kanban_column:nth-child(1) div.oe_fold_column.oe_kanban_record').length + 1,
                content:   _t("Patient will be moved to <b>Discharged</b> stage"),
                popover:   { next: _t("Next"), end:_t("End")}
            }
        ]
    });

}());