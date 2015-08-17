/**
 * Created by neova on 12/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'junior_doctor_able_to_update_patient_arrival',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',
        steps: [
            {
                title:     _t("Login page"),
                element:   '.oe_topbar_name',
                popover:   { next: _t("Next")},
                content:   _t("You are Logged in as Junior Doctor")
            },
            {
                title:     _t("Referral Board"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   { next: _t("Next")},
                content:   _t("Referral Board is loaded")
            },
            {
                title:     _t("Click on Arrived Button"),
                element:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button',
                popover:   { next: _t("Next")},
                content: _t("Notify patient arrival by clicking on arrived  button)")

            },
            {
               title:     _t("patient arrival updated"),
               waitFor:   ('td.oe_kanban_column:nth-child(3) div.oe_fold_column.oe_kanban_record').length + 1,
               popover:   { next: _t("Next"), end: _t('End')},
               content: _t("patient arrival updated and patient is in To be clerked stage")

            }
        ]
    });

}());