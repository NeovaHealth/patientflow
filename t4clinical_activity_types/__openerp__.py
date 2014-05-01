# -*- encoding: utf-8 -*-
{
    'name': 'T4 Clinical activity types',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Tactix4',
    'website': 'http://www.tactix4.com/',
    'depends': ['t4clinical_base','project','hr'],
    'data': [
             'views/views.xml',
             'views/patient_placement_view.xml',
             'wizards/placement_wizard_view.xml',
             'data/types.xml', 
             'views/menuitem.xml',
             'security/ir.model.access.csv'],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': [],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}