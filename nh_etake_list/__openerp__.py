# -*- encoding: utf-8 -*-
{
    'name': 'NH eTake List',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_patient_flow', 'nh_doctor_activities'],
    'data': ['security/ir.model.access.csv',
             'etake_list_data.xml',
             'views/clerking_view.xml',
             'views/review_view.xml',
             'views/overview_view.xml',
             'views/transfer_view.xml',
             'views/referral_form_view.xml',
             'wizard/doctor_task_wizard_view.xml',
             'wizard/accept_referral_wizard_view.xml',
             'wizard/print_report_wizard_view.xml',
             'views/menuitem.xml',
             'takelist_report.xml',
             'views/takelist_report_view.xml'],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}