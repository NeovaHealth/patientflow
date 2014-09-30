# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4activity.activity import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_patient_placement_wizard(orm.TransientModel):
    _name = 't4.clinical.patient.placement.wizard'
    _columns = {
        'placement_ids': fields.many2many('t4.clinical.patient.placement', 'placement_wiz_rel', 'placement_id', 'wiz_id', 'Placements'),
        'recent_placement_ids': fields.many2many('t4.clinical.patient.placement', 'recent_placement_wiz_rel', 'placement_id', 'wiz_id', 'Recent Placements'),
    }
    
    
    def _get_placement_ids(self, cr, uid, context=None):
        domain=[('state','in',['draft','scheduled','started'])]
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_ids = placement_pool.search(cr, uid, domain)
        return placement_ids
    
    def _get_recent_placement_ids(self, cr, uid, context=None):
        domain=[('state','in',['completed'])]
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_ids = placement_pool.search(cr, uid, domain, limit=3, order="date_terminated desc")
        return placement_ids    
    
    _defaults = {
         'placement_ids': _get_placement_ids,
         'recent_placement_ids': _get_recent_placement_ids,
     }
    
    def apply(self, cr, uid, ids, context=None):
        activity_pool = self.pool['t4.activity']
        for placement in self.browse(cr, uid, ids[0], context).placement_ids:
            if placement.location_id:
                activity_pool.start(cr, uid, placement.activity_id.id, context)
                activity_pool.submit(cr, uid, placement.activity_id.id, {'location': placement.location_id.id}, context)
                activity_pool.complete(cr, uid, placement.activity_id.id, context)
                
        self.write(cr, uid, ids, {'placement_ids': [(6,0,self._get_placement_ids(cr, uid))],
                                  'recent_placement_ids': [(6,0,self._get_recent_placement_ids(cr, uid))]})
        
        aw = {'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': ids[0],
            'view_type': "form",
            'view_mode': "form",
            'target': "inline",
            
            }
        return aw