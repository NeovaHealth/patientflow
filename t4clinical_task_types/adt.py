# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if
import logging        
_logger = logging.getLogger(__name__)



class t4_clinical_adt(orm.Model):
    _name = 't4.clinical.adt'
    _inherit = ['t4.clinical.task.data']       
    _columns = {
    }
    
class t4_clinical_adt_patient_register(orm.Model):
    _name = 't4.clinical.adt.patient.register'
    _inherit = ['t4.clinical.task.data']      
    _columns = { 
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),
        'family_name': fields.text('familyName'),
        'given_name': fields.text('givenName'),
        'middle_names': fields.text('middleName'),  
        'dob': fields.datetime('DOB'),
        'gender': fields.char('Gender', size=1),      
        'sex': fields.char('Sex', size=1),                
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(not 'patient_identifier' in vals.keys() and not 'other_identifier' in vals.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        patient_domain = [(k,'=',v) for k,v in vals.iteritems()]
        patient_id = patient_pool.search(cr, uid, patient_domain)
        if patient_id:
            patient_id = patient_id[0]
            except_if(patient_id, msg="Patient with the data submitted already exists! Data: %s" % vals)
            # handle duplicate patient here        
        patient_pool = self.pool['t4.clinical.patient']
        patient_pool.create(cr, uid, vals, context)
        super(t4_clinical_adt_patient_register, self).submit(cr, uid, task_id, vals, context)
        return True
    


class t4_clinical_adt_patient_admit(orm.Model):
    _name = 't4.clinical.adt.patient.admit'
    _inherit = ['t4.clinical.task.data']      

    def _admit2location_id(self, cr, uid, ids, field, arg, context=None):
        res = {}
        location_pool = self.pool['t4.clinical.location']
        for admit in self.browse(cr, uid, ids, context):
            location_id = location_pool.search(cr, uid, [('code','=',admit.location)])
            res[admit.id] = location_id and location_id[0] or False
        return res
        
    _columns = {
        'location_id': fields.function(_admit2location_id, type='many2one', relation='t4.clinical.location', string='Location', 
                               store={
                                      't4.clinical.adt.patient.admit':(lambda self, cr, uid, ids, c: ids, ['location'], 10)
                                      }),
        'patient_id': fields.many2one('t4.clinical.patient', 'Patient'),
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"), 
        'other_identifier': fields.text("Other Identifier")              
    }
    def submit(self, cr, uid, task_id, vals, context=None):
#         except_if(not 'patient_identifier' in vals.keys() and not 'other_identifier' in vals.keys(),
#               msg="patient_identifier or other_identifier not found in submitted data!")
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.search(cr, uid, [('code','=',vals['location'])])
        except_if(not location_id, msg="Location not found!")
        location_id = location_id[0]
        
        patient_pool = self.pool['t4.clinical.patient']
        patient_id = patient_pool.search(cr, uid, [('other_identifier','=',vals['other_identifier'])])
        #import pdb; pdb.set_trace()
        if not patient_id:
            except_if(True, msg="Patient not found!")
        elif len(patient_id) > 1:
            except_if(True, msg="More than one patient found!")
        patient_id = patient_id[0]
        super(t4_clinical_adt_patient_admit, self).submit(cr, uid, task_id, vals, context)
        admission_pool = self.pool['t4.clinical.patient.admission']
        vals_copy = vals.copy()       
        vals_copy.update({'location_id': location_id})  
        vals_copy.update({'patient_id': patient_id})  
        admission_task_id = admission_pool.create_task(cr, uid, {}, vals_copy)
        task_pool = self.pool['t4.clinical.task']
        task_pool.start(cr, uid, admission_task_id, context)
#         ctx = context and context.copy() or {}
#         ctx.update({'parent_task_id': task_id})        
        admission_result = task_pool.complete(cr, uid, admission_task_id, context)
        task_pool.write(cr, uid, task_id, {'parent_id': admission_result['spell_task_id']})
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        task_pool.set_task_trigger(cr, uid, patient_id,'t4.clinical.patient.observation.ews',
                                   'minute', user.pos_id.ews_init_frequency, context=None)
        return True    

class t4_clinical_adt_patient_discharge(orm.Model):
    _name = 't4.clinical.adt.patient.discharge'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
    }

class t4_clinical_adt_patient_transfer(orm.Model):
    _name = 't4.clinical.adt.patient.transfer'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),                
        'location': fields.text('Location'),                
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(not ('other_identifier' in vals or 'patient_identifier' in vals), msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        other_identifier = vals.get('other_identifier')
        patient_identifier = vals.get('patient_identifier')
        domain = []
        other_identifier and domain.append(('other_identifier','=',other_identifier))
        patient_identifier and domain.append(('patient_identifier','=',patient_identifier))
        domain = domain and ['|']*(len(domain)-1) + domain
        print "transfer domain: ", domain
        patient_id = patient_pool.search(cr, uid, domain)
        except_if(not patient_id, msg="Patient not found!")
        patient_id = patient_id[0]           
        location_pool = self.pool['t4.clinical.location']
        location_id = location_pool.search(cr, uid, [('code','=',vals['location'])])
        except_if(not location_id, msg="Location not found!")
        location_id = location_id[0]
        placement_pool = self.pool['t4.clinical.patient.placement']
        placement_pool.create_task(cr, uid, {}, {'patient_id': patient_id}, context)
        super(t4_clinical_adt_patient_transfer, self).submit(cr, uid, task_id, vals, context)    
        
class t4_clinical_adt_patient_merge(orm.Model):
    _name = 't4.clinical.adt.patient.merge'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
        'from_identifier': fields.text('From patient Identifier'),
        'into_identifier': fields.text('Into Patient Identifier'),        
    }
    
    def submit(self, cr, uid, task_id, vals, context=None):
        except_if(not ('from_identifier' in vals and 'into_identifier' in vals), msg="from_identifier or into_identifier not found in submitted data!")
        patient_pool = self.pool['t4.clinical.patient']
        from_id = self.search(cr, uid, [('other_identifier', '=', vals['from_identifier'])])
        into_id = self.search(cr, uid, [('other_identifier', '=', vals['into_identifier'])])
        except_if(not(from_id and into_id), msg="Source or destination patient not found!")    
        # compare and combine data. may need new cursor to have the update in one transaction
        for model_pool in self.pool._models.values():
            if model_pool._name.startswith("t4.clinical") and 'patient_id' in model_pool.columns.keys() and model_pool._name != self._name:
                ids = model_pool.search(cr, uid, [('patient_id','=',from_id)])
                ids and model_pool.write(cr, uid, ids, {'patient_id': into_id})
        from_data = patient_pool.read(cr, uid, from_id, context)        
        indo_data = patient_pool.read(cr, uid, into_id, context)
        vals_into = {}
        for fk, fv in from_data.iteritems():
            for ik, iv in into_data.iteritems():
                if not fv:
                    continue
                if fv and iv and fv != iv:
                    pass # which to choose ?
                if fv and not iv:
                    vals_into.update({ik: fv})
        patient_pool.write(cr, uid, into_id, vals_into, context)
        patient_pool.write(cr, uid, from_id, {'active':False}, context)
        super(t4_clinical_adt_patient_merge, self).submit(cr, uid, task_id, vals, context)
        
             
    
class t4_clinical_adt_patient_update(orm.Model):
    _name = 't4.clinical.adt.patient.update'
    _inherit = ['t4.clinical.task.data']      
    _columns = {
    }