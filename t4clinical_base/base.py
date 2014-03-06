# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)

class t4_clinical_pos(orm.Model):
    """ Clinical point of service """
    _name = 't4.clinical.pos' 
     
    _columns = {
        'name': fields.char('Point of Service', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'location_id': fields.many2one('t4.clinical.location', 'POS Location', required=True), 
        'company_id': fields.many2one('res.company', 'Company'),
        'lot_admission_id': fields.many2one('t4.clinical.location', 'Admission Location'),
        'lot_discharge_id': fields.many2one('t4.clinical.location', 'Discharge Location'),       
    }

class res_company(orm.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'pos_ids': fields.one2many('t4.clinical.pos', 'company_id', 'Points of Service'),
    }
    
class res_users(orm.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    _columns = {
        'pos_id': fields.many2one('t4.clinical.pos', 'POS'),
        'location_ids': fields.many2many('t4.clinical.location', 'user_location_rel', 'user_id', 'location_id', 'Locations of Responsibility'),        
    }
    
class t4_clinical_location(orm.Model):
    """ Clinical LOCATION """

    _name = 't4.clinical.location'
    #_parent_name = 'location_id'
    _rec_name = 'code'
    _types = [('poc', 'Point of Care'), ('structural', 'Structural'), ('virtual', 'Virtual'), ('pos', 'POS')]
    _usages = [('bed', 'Bed'), ('ward', 'Ward'), ('room', 'Room'),('department', 'Department'), ('hospital', 'Hospital')]
    
    def _location2pos_id(self, cr, uid, ids, field, args, context=None):
        res = {}
        pos_pool = self.pool['t4.clinical.pos']
        #pos_ids = pos_pool.search(cr, uid, [])
        #import pdb; pdb.set_trace()
        pos_locations_map = {pos.id: pos.location_id.id for pos in pos_pool.browse_domain(cr, uid, [])}
        for location in self.browse(cr, uid, ids, context):
            res[location.id] = False
            for pos_id, pos_location_id in pos_locations_map.iteritems():
                if location.id in self.search(cr, uid, ['|',('id', 'child_of', [pos_location_id]),('id','=',pos_location_id)]):
                    res[location.id] = pos_id
                    break
        return res
    
#     def _location2company_id(self, cr, uid, ids, field, args, context=None):
#         res = {}
#         company_pool = self.pool['res.company']
#         for location in self.browse(cr, uid, ids, context):
#             domain = [('pos_ids','in',location.pos_id)]
#             company_id = company_pool.search(cr, uid, domain, context=context)
#             res[location.id] = company_id and company_id[0] or False
#         return res    
    
    _columns = {
        'name': fields.char('Location', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'parent_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'active': fields.boolean('Active'),
        'pos_id': fields.function(_location2pos_id, type='many2one', relation='t4.clinical.pos', string='POS'),
        'company_id': fields.related('pos_id', 'company_id', type='many2one', relation='res.company', string='Company'),
        #'parent_left': fields.integer('Left Parent', select=1),
        #'parent_right': fields.integer('Right Parent', select=1),        
    }

        
    _defaults = {
        'active': True
    }

    def get_location_task_ids(self, cr, uid, location_id, context=None):
        """
        """
        location_models = self.pool['t4.clinical.task.data.type'].get_field_models(cr, uid, 'location_id')
        task_ids = []
        for m in location_models:
            data = m.browse_domain(cr, uid, [('location_id','=',location_id)], context=context)
            data = data and data[0]
            data and data.task_id and task_ids.append(data.task_id.id)
        return task_ids

class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    _columns = {
        'location_ids': fields.related('user_id','location_ids',type='many2many', relation='t4.clinical.location', string='Locations of Responsibility'),
        
    }

    
    
    

class t4_clinical_patient(osv.Model):
    """T4Clinical Patient object, to store all the parameters of the Patient
    """
    _name = 't4.clinical.patient'
    _description = "A Patient"

    _inherits = {'res.partner': 'partner_id'}

    def _get_fullname(self, vals):

        #TODO: Make this better and support comma dependency / format etc
        return ''.join([vals.get('family_name', '') or '', ', ',
                        vals.get('given_name', '') or '', ' ',
                        vals.get('middle_names', '') or ''])

    def _get_name(self, cr, uid, ids, fn, args, context=None):
        result = dict.fromkeys(ids, False)
        for r in self.read(cr, uid, ids, ['family_name', 'given_name', 'middle_name'], context=context):
            #TODO This needs to be manipulable depending on locale
            result[r['id']] = self._get_fullname(r)
        return result

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='restrict'),
        'dob': fields.datetime('Date Of Birth'),  # Partner birthdate is NOT a date.
        'sex': fields.char('Sex', size=1),
        'gender': fields.char('Gender', size=1),
        'ethnicity': fields.char('Ethnicity', size=20),
        'patient_identifier': fields.char('Patient Identifier', size=100, select=True, help="NHS Number"),
        'other_identifier': fields.char('Other Identifier', size=100, required=True, select=True,
                                        help="Hospital Number"),

        'given_name': fields.char('Given Name', size=200),
        'middle_names': fields.char('Middle Name(s)', size=200),
        'family_name': fields.char('Family Name', size=200, select=True),
        }

    _defaults = {
        'active': True,
        'name': 'unknown'
    }
    
    def create(self, cr, uid, vals, context=None):
        if not vals.get('name'):
            vals.update({'name': self._get_fullname(vals)})
        rec_id = super(t4_clinical_patient, self).create(cr, uid, vals, context)
        return rec_id    
    
    def set_task_frequency(self, cr, uid, patient_id, data_model, unit, unit_qty, context=None):
        trigger_pool = self.pool['t4.clinical.patient.task.trigger']
        trigger_id = trigger_pool.search(cr, uid, [('patient_id','=',patient_id),('data_model','=',data_model)])
        if trigger_id:
            trigger_id = trigger_id[0]
            trigger_pool.write(cr, uid, trigger_id, trigger_data, {'active': False})

        trigger_data = {'patient_id': patient_id, 'data_model': data_model, 'unit': unit, 'unit_qty': unit_qty}
        trigger_id = trigger_pool.create(cr, uid, trigger_data)        
        _logger.info("Task frequency for patient_id=%s data_model=%s set to %s %s(s)" % (patient_id, data_model, unit_qty, unit))
        return trigger_id