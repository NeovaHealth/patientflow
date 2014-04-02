# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
import logging        
_logger = logging.getLogger(__name__)

class t4clinical_res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'doctor': fields.boolean('Doctor', help="Check this box if this contact is a Doctor")
    }


class t4_clinical_device_type(orm.Model):
    _name = 't4.clinical.device.type'

    _columns = {
        'name': fields.text("Device Type"),
        'flow_direction': fields.selection([('none', 'None'), ('in', 'In'), ('out', 'Out'), ('both', 'Both')], 'Flow Direction'),
        
    }

class device_type(orm.Model):
    _name = 't4.clinical.device'
    _rec_name = 'type_id'
    _columns = {
        'type_id': fields.many2one('t4.clinical.device.type', "Device Type"),
        'flow_direction': fields.selection([('none', 'None'), ('in', 'In'), ('out', 'Out'), ('both', 'Both')], 'Flow Direction'),
        
    }
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
        'ews_init_frequency': fields.integer('EWS Initial Frequency in Minutes')
    }

    _defaults = {
        'ews_init_frequency': 15
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
        'activity_type_ids': fields.many2many('t4.clinical.activity.type', 'user_activity_type_rel', 'user_id', 'type_id', 'Activity Types of Responsibility'),
    }

class res_groups(orm.Model):
    _name = 'res.groups'
    _inherit = 'res.groups'
    _columns = {
        'activity_type_ids': fields.many2many('t4.clinical.activity.type', 'group_activity_type_rel', 'group_id', 'type_id', 'Activity Types of Responsibility'),
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
        #import pdb; pdb.set_trace()
        for location in self.browse(cr, uid, ids, context):
            pos_location_id = self.search(cr, uid, [['parent_id','=',False],['child_ids','child_of',location.id]])
            pos_location_id = pos_location_id and pos_location_id[0] or False
            pos_id = pos_pool.search(cr, uid, [['location_id','=',pos_location_id]])
            res[location.id] = pos_id and pos_id[0]
            if not pos_id:
                _logger.warning("pos_id not found for location '%s', id=%s" % (location.code, location.id))
        return res
    
    def _pos2location_id(self, cr, uid, ids, context=None):
        res = []
        for pos in self.browse(cr, uid, ids, context):
            res.extend(self.pool['t4.clinical.location'].search(cr, uid, [['id','child_of',pos.location_id.id]]))
        return res          
 
    def _is_available(self, cr, uid, ids, field, args, context=None):
        #import pdb; pdb.set_trace()
        activity_pool = self.pool['t4.clinical.activity']
        res = {}
        pos_ids = list(set([l.pos_id.id for l in self.browse(cr, uid, ids, context)]))
        available_location_ids = []
        for pos_id in pos_ids:
            available_location_ids.extend(activity_pool.get_available_bed_location_ids(cr, uid, pos_id, context))
        for location in self.browse(cr, uid, ids, context):
            res[location.id] = location.id in available_location_ids
        return res
    
    def _placement2location_id(self, cr, uid, ids, context=None):
        res = [p.location_id.id for p in self.pool['t4.clinical.patient.placement'].browse(cr, uid, ids, context)]
        return res
        
         
         
    _columns = {
        'name': fields.char('Location', size=100, required=True, select=True),
        'code': fields.char('Code', size=256),
        'parent_id': fields.many2one('t4.clinical.location', 'Parent Location'),
        'child_ids': fields.one2many('t4.clinical.location', 'parent_id', 'Child Locations'),
        'type': fields.selection(_types, 'Location Type'),
        'usage': fields.selection(_usages, 'Location Usage'),
        'active': fields.boolean('Active'),
        'pos_id': fields.function(_location2pos_id, type='many2one', relation='t4.clinical.pos', string='POS', store={
                                  't4.clinical.location': (lambda s, cr, uid, ids, c: s.search(cr, uid, [['id','child_of',ids]]), ['parent_id'], 10),
                                  't4.clinical.pos': (_pos2location_id, ['location_id'], 5),
                                    }),
        'company_id': fields.related('pos_id', 'company_id', type='many2one', relation='res.company', string='Company'),
        'is_available': fields.function(_is_available, type='boolean', string='Is Available?', 
                                        store={
                                               't4.clinical.location': (lambda self, cr, uid, ids, c: ids, [], 10),
                                               't4.clinical.patient.placement': (_placement2location_id, ['location_id'], 20)
                                               })
      
    }

        
    _defaults = {
        'active': True,
    }

    def get_location_activity_ids(self, cr, uid, location_id, context=None):
        """
        """
        location_models = self.pool['t4.clinical.activity.type'].get_field_models(cr, uid, 'location_id')
        activity_ids = []
        for m in location_models:
            data = m.browse_domain(cr, uid, [('location_id','=',location_id)], context=context)
            data = data and data[0]
            data and data.activity_id and activity_ids.append(data.activity_id.id)
        return activity_ids

    def get_available_location_ids(self, cr, uid, usages, location_id=None, context=None):
        """
        beds not placed into and not in non-terminated placement Activities
        """
        #import pdb; pdb.set_trace()
        domain = [('usage','in',usages)]
        location_id and  domain.append(('id','child_of',location_id)) 
        location_pool = self.pool['t4.clinical.location']
        location_ids = location_pool.search(cr, uid, domain)
        spell_pool = self.pool['t4.clinical.spell']
        domain = [('state','=','started'),('location_id','in',location_ids)]
        spell_ids = spell_pool.search(cr, uid, domain)
        location_ids = list(set(location_ids) - set([s.location_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]))
        placement_pool = self.pool['t4.clinical.patient.placement']
        domain = [('date_terminated','=',False),('location_id','in',location_ids)]    
        placement_ids = placement_pool.search(cr, uid, domain)
        location_ids = list(set(location_ids) - set([p.location_id.id for p in placement_pool.browse(cr, uid, placement_ids, context)]))
        return location_ids
    

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
