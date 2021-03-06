__author__ = 'colin'
from openerp import api, models
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

class TakeListReport(models.AbstractModel):
    _name = 'report.nh_etake_list.takelist_report_view'
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh_etake_list.takelist_report_view')
        overview_pool = self.pool['nh.etake_list.overview']
        sort_options = [
            ['P', 'clerking_started asc'],
            ['J', 'clerking_started asc'],
            ['H', 'clerking_started asc'],
            ['W', 'location_name asc, clerking_started asc']
        ]
        titles = [
            ['P', 'PTWR Take List'],
            ['J', 'Junior Activity Take List'],
            ['H', '14 Hour Target Take List'],
            ['W', 'Location Take List']
        ]
        default_domain = [['state', 'not in', ['Done','Other','dna','to_dna','admitted']], ['hours_from_discharge', '<', 12], ['clerking_started', '!=', False]]
        domains = [
            ['P', [
                ['state', 'in', ['Senior Review', 'Consultant Review']],
                ['hours_from_discharge', '<', 12],
                ['clerking_started', '!=', False]]
            ],
            ['J', [
                ['state', 'in', ['To Be Clerked', 'Clerking in Process']],
                ['hours_from_discharge', '<', 12],
                ['clerking_started', '!=', False]]
            ],
            ['H', default_domain],
            ['W', default_domain],
        ]

        clerking_order = [opt[1] for opt in sort_options if opt[0] == data] if data else []
        domain = [dom[1] for dom in domains if dom[0] == data] if data else []
        title = [ts[1] for ts in titles if ts[0] == data] if data else []
        # clerking_order = 'location_name asc, clerking_started asc' if data and data == 'W' else 'clerking_started asc'
        # non_clerking_order = 'location_name asc, id asc' if data and data == 'W' else 'id asc'
        clerking_take_list_ids = overview_pool.search(self._cr, self._uid, domain[0] if domain else default_domain, order=clerking_order[0] if clerking_order else 'clerking_started asc')
        # non_clerking_take_list_ids = overview_pool.search(self._cr, self._uid, [['state', 'not in', ['Done','Other','dna','to_dna','admitted']], ['hours_from_discharge', '<', 12], ['clerking_started', '=', False]], order=non_clerking_order)
        take_list = overview_pool.read(self._cr, self._uid, clerking_take_list_ids)
        grouped_take_list = reduce(lambda x,y: x+[{'location': y, 'patients': []}] if not {'location': y, 'patients': []} in x else x, [p['location_name'] for p in take_list],[])
        for patient in take_list:
            if patient['dob']:
                dob_delta = datetime.strptime(patient['dob'], dtf)
                patient['dob'] = datetime.strftime(dob_delta, '%d/%m/%Y')
            if patient['clerking_started']:
                clerking_start = datetime.strptime(patient['clerking_started'], dtf)
                clerking_deadline = clerking_start + timedelta(hours=14)
                if clerking_deadline > datetime.now():
                    patient['clerking_deadline'] = '14 hour target @ {0}'.format(datetime.strftime(clerking_deadline, '%d/%m/%Y %H:%M'))
                else:
                    patient['clerking_deadline'] = '14 hour target BREACHED @ {0}'.format(datetime.strftime(clerking_deadline, '%d/%m/%Y %H:%M'))
            if data and data == 'W':
                group_to_use = [group for group in grouped_take_list if group['location'] == patient['location_name']][0]
                group_to_use['patients'].append(patient)

        sorting_by = data if data else 'none'
        take_list_to_use = grouped_take_list if data and data == 'W' else take_list
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'take_list': take_list_to_use,
            'sort_by': sorting_by,
            'title': title[0] if title else 'Take List'
        }
        return report_obj.render('nh_etake_list.takelist_report_view', docargs)
