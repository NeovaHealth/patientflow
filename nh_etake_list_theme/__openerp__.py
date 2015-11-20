# -*- encoding: utf-8 -*-
# Part of Patient Flow.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'NH eTake List Theme',
    'version': '0.1',
    'category': 'Clinical',
    'license': 'AGPL-3',
    'summary': '',
    'description': """ A theme for the eTake List """,
    'author': 'Neova Health',
    'website': 'http://www.neovahealth.co.uk/',
    'depends': ['nh_etake_list_eobs'],
    'data': [
        'views/overview_view.xml'
    ],
    'demo': [],
    'css': [],
    'js': [],
    'qweb': ['static/src/xml/base.xml'],
    'images': [],
    'application': True,
    'installable': True,
    'active': False,
}
