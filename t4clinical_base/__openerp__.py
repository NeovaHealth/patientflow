# -*- encoding: utf-8 -*-
{
    'name': 'T4 Clinical Improved',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Tactix4',
    'website': 'http://www.tactix4.com/',
    'depends': ['project','hr'], #, 't4_base'],
    'data': ['data.xml', 
             
             'activity_view.xml',
             'pos_view.xml',
             'location_view.xml',
             'patient_view.xml',
             'activity_type_view.xml',
             'employee_view.xml',
             'user_view.xml',
             'trigger_view.xml',
             
             'menuitem.xml',             
             
             'ir.model.access.csv'],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}