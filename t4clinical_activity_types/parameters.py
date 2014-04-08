# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.activity import except_if
import logging        
_logger = logging.getLogger(__name__)


class t4_clinical_o2level(orm.Model):
    _name = 't4.clinical.o2level'      
    _columns = {
        'name': fields.integer("O2 Target Name"),
        'min': fields.integer("Min"),
        'max': fields.integer("Max"),               
    }
    
class t4_clinical_patient_o2target(orm.Model):
    _name = 't4.clinical.patient.o2target'
    _inherit = ['t4.clinical.activity.data']       
    _rec_name = 'level_id'
    _columns = {
        'level_id': fields.many2one('t4.clinical.o2level', 'O2 Level', required=True),                
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient', required=True),
               
    }