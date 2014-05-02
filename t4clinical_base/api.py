# -*- coding: utf-8 -*-
from openerp.osv import orm, fields, osv
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import SUPERUSER_ID

import logging        
_logger = logging.getLogger(__name__)

    
class t4_clinical_api(orm.AbstractModel):
    _name = 't4.clinical.api'

    def activity_info(self, cr, uid, activity_id, context={}):
        """
            activity diagnostic info
        """
        res = {}
        activity_pool = self.pool['t4.clinical.activity']
        activity = activity_pool.browse(cr, uid, activity_id, {})
        res['activity'] = activity_pool.read(cr,uid,activity_id, [])
        res['data'] = self.pool[activity.data_model].read(cr,uid,activity.data_ref.id, [])
        res['parents'] = {}
        while True:
            parent = activity.parent_id
            if not parent: break
            activity = activity = activity_pool.browse(cr, uid, parent.id, context)
            res['parents'].update({parent.data_model: parent})
        res['creators'] = {}
        activity = activity_pool.browse(cr, uid, activity_id, context)
        while True:
            creator = activity.creator_id
            if not creator: break
            activity = activity_pool.browse(cr, uid, creator.id, context)
            res['creators'].update({creator.data_model: creator}) 
        from pprint import pprint as pp
        pp(res)
        return res           
            
    def get_not_palced_patient_ids(self, cr, uid, location_id=None, context=None):
        # all current patients
        spell_domain = [('state','=','started')]
        spell_pool = self.pool['t4.clinical.spell']
        spell_ids = spell_pool.search(cr, uid, spell_domain)
        spell_patient_ids = [s.patient_id.id for s in spell_pool.browse(cr, uid, spell_ids, context)]
        # placed current patients
        placement_domain = [('activity_id.parent_id.state','=','started'),('state','=','completed')]
        location_id and  placement_domain.append(('activity_id.location_id','child_of',location_id))
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_ids = placement_pool.search(cr, uid, placement_domain)
        placed_patient_ids = [p.patient_id.id for p in placement_pool.browse(cr, uid, placement_ids, context)]       
        patient_ids = set(spell_patient_ids) - set(placed_patient_ids)
        #import pdb; pdb.set_trace()
        return list(patient_ids)
    


    def get_patient_spell_activity_id(self, cr, uid, patient_id, pos_id=None, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('patient_id', '=', patient_id),
                  ('state', '=', 'started'),
                  ('data_model', '=', 't4.clinical.spell')]
        if pos_id:
            domain.append(('pos_id', '=', pos_id))
        spell_activity_id = activity_pool.search(cr, SUPERUSER_ID, domain)
        if not spell_activity_id:
            return False
        if len(spell_activity_id) > 1:
            _logger.warn("For patient_id=%s found more than 1 started spell_activity_ids: %s " % (patient_id, spell_activity_id))
        return spell_activity_id[0]


    def get_patient_spell_activity_browse(self, cr, uid, patient_id, pos_id=None, context=None):
        spell_activity_id = self.get_patient_spell_activity_id(cr, uid, patient_id, pos_id, context)
        if not spell_activity_id:
            return False
        return self.pool['t4.clinical.activity'].browse(cr, uid, spell_activity_id, context)

    
    def get_device_session_activity_id(self, cr, uid, device_id, context=None):
        activity_pool = self.pool['t4.clinical.activity']
        domain = [('device_id', '=', device_id),
                  ('state', '=', 'started'),
                  ('data_model', '=', 't4.clinical.device.session')]
        session_activity_id = activity_pool.search(cr, SUPERUSER_ID, domain)
        if not session_activity_id:
            return False
        if len(session_activity_id) > 1:
            _logger.warn("For device_id=%s found more than 1 started device session activity_ids: %s " 
                         % (device_id, session_activity_id))
        return session_activity_id[0]

          

    def get_patient_current_location_browse(self, cr, uid, patient_id, context=None):
        move_pool = self.pool['t4.clinical.patient.move']
        move_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        # sort parameter includes 'id' to resolve situation with equal values in 'date_terminated'
        move = move_pool.browse_domain(cr, uid, move_domain, limit=1, order="date_terminated, id desc", context=context)
        location_id = move and move[0].location_id or False
        return location_id

    def get_patient_current_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_current_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res

    def get_patient_placement_location_browse(self, cr, uid, patient_id, context=None):
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_domain = [('patient_id','=',patient_id), ('state','=','completed')]
        placement = placement_pool.browse_domain(cr, uid, placement_domain, limit=1, order="date_terminated desc", context=context)
        placement = placement and placement[0]
        res = placement and placement.location_id or False
        return res    
    
    def get_patient_placement_location_id(self, cr, uid, patient_id, context=None):
        res = self.get_patient_placement_location_browse(cr, uid, patient_id, context)
        res = res and res.id
        return res    

class t4_clinical_api_adt(orm.AbstractModel):
    _name = 't4.clinical.api.adt'
    


    
class t4_clinical_api_frontend(orm.AbstractModel):
    _name = 't4.clinical.api.frontend'