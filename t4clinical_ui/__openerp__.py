# -*- encoding: utf-8 -*-
{
    'name': 'T4 Clinical UI',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """    """,
    'author': 'Tactix4',
    'website': 'http://www.tactix4.com/',
    'depends': ['t4clinical_base','t4clinical_activity_types', 't4clinical_api', ],
    'data': [
             'wardboard_view.xml',
             'workload_view.xml',
             'menuitem.xml',
             'ir.model.access.csv'],
    'application': True,
    'installable': True,
    'active': False,
}