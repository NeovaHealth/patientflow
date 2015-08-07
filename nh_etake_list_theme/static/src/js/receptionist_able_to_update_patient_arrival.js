/**
 * Created by neova on 11/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'receptionist_able_to_update_patient_arrival',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        mode: 'test',


        steps: [

            {
                title:     _t("Login page"),
                element:   '.oe_topbar_name',
                popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
                content:   _t("Enter a name for your new product then click 'Continue'."),
            },

            {
                title:     _t("Referral"),
                element:   '.oe_menu_text:contains("Referral Board")',
                popover:   {fixed:true}
            },

            {
                title:     _t("Notify patient arrival (click on'Arrived'  button)"),
                waitFor:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button',
                popover:   {fixed:true}
            },
            //{
            //    title:     _t("patient arrival updated and patient is in To be clerked stage"),
            //    waitFor:   ('td.oe_kanban_column:nth-child(3) div.oe_fold_column.oe_kanban_record').length + 1
            //}
        ]
    });

}());