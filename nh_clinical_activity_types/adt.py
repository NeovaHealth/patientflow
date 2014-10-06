# -*- coding: utf-8 -*-

from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp import SUPERUSER_ID
import logging        
_logger = logging.getLogger(__name__)

class nh_clinical_adt(orm.Model):
    _name = 'nh.clinical.adt'
    _inherit = ['nh.activity.data']     
    _columns = {
    }


class nh_clinical_adt_patient_register(orm.Model):
    _name = 'nh.clinical.adt.patient.register'
    _inherit = ['nh.activity.data']   
    _description = 'ADT Patient Register'   
    _columns = { 
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),
        'family_name': fields.text('familyName'),
        'given_name': fields.text('givenName'),
        'middle_names': fields.text('middleName'),  
        'dob': fields.datetime('DOB'),
        'gender': fields.char('Gender', size=1),      
        'sex': fields.char('Sex', size=1),                
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        vals_copy = vals.copy()
        res = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)        
        except_if(not 'patient_identifier' in vals_copy.keys() and not 'other_identifier' in vals_copy.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['nh.clinical.patient']
        patient_domain = [(k,'=',v) for k,v in vals_copy.iteritems()]
        patient_id = patient_pool.search(cr, uid, patient_domain)
        except_if(patient_id, msg="Patient already exists! Data: %s" % vals_copy)
        patient_id = patient_pool.create(cr, uid, vals_copy, context)
        vals_copy.update({'patient_id': patient_id, 'pos_id': user.pos_id.id})
        super(nh_clinical_adt_patient_register, self).submit(cr, uid, activity_id, vals_copy, context)
        res.update({'patient_id': patient_id})
        return res
    
    def complete(self, cr, uid, activity_id, context=None): 
        res = {}
        super(nh_clinical_adt_patient_register, self).complete(cr, uid, activity_id, context)
        return res       

    def demo_values(self, cr, uid, values={}):
        fake = self.next_seed_fake()
        gender = fake.random_element(('M','F'))
        v = {
                'family_name': fake.last_name(),
                'given_name': fake.first_name(),
                'other_identifier': str(fake.random_int(min=1000001, max=9999999)),
                'dob': fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S"),
                'gender': gender,
                'sex': gender,
                }
        v.update(values)
        return v


class nh_clinical_adt_patient_admit(orm.Model):
    """
        adt.patient.admit: 
            - validate patient(patient_id), suggested_location(location_id or false)
            - on validation fail raise exception
            - start admission with patient_id and suggested_location
            
       consulting and referring doctors are expected in the submitted values on key='doctors' in format:
       [...
       {
       'type': 'c' or 'r',
       'code': code string,
       'title':, 'given_name':, 'family_name':, }
       ...]
       
       if doctor doesn't exist, we create partner, but don't create user
        
             
    """
    
    _name = 'nh.clinical.adt.patient.admit'
    _inherit = ['nh.activity.data']      
    _description = 'ADT Patient Admit'    
    _columns = {
        'suggested_location_id': fields.many2one('nh.clinical.location', 'Suggested Location', help="Location suggested by ADT for placement. Usually ward."),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"), 
        'other_identifier': fields.text("Other Identifier"),
        'doctors': fields.text("Doctors"),
        'ref_doctor_ids': fields.many2many('res.partner', 'ref_doctor_admit_rel', 'admit_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('res.partner', 'con_doctor_admit_rel', 'admit_id', 'doctor_id', "Consulting Doctors"),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        res = {}
        api_pool = self.pool['nh.clinical.api']
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        # location validation
        suggested_location = api_pool.get_locations(cr, SUPERUSER_ID, codes=[vals['location']], pos_ids=[user.pos_id.id])
        if not suggested_location:
            _logger.warn("ADT suggested_location '%s' not found! Will automatically create one" % vals['location'])
            location_pool = self.pool['nh.clinical.location']
            suggested_location_id = location_pool.create(cr, uid, {
                'name': vals['location'],
                'code': vals['location'],
                'pos_id': user.pos_id.id,
                'type': 'poc',
                'usage': 'ward'
            }, context=context)
        else:
            suggested_location_id = suggested_location[0].id
        # patient validation
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier','=',vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s" 
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()       
        vals_copy.update({'suggested_location_id': suggested_location_id, 'patient_id': patient_id, 'pos_id': user.pos_id.id})  
        # doctors
        if vals.get('doctors'):
            try:
                doctors = eval(str(vals['doctors']))
                ref_doctor_ids = []
                con_doctor_ids = []
                partner_pool = self.pool['res.partner'] 
                for d in doctors:
                    doctor_id = partner_pool.search(cr, uid, [['code','=',d['code']]])
                    if not doctor_id:
                        if d['title']:
                            d['title'] = d['title'].strip()
                            title_pool = self.pool['res.partner.title']
                            title_id = title_pool.search(cr, uid, [['name','=',d['title']]])
                            title_id = title_id and title_id[0] or title_pool.create(cr, uid, {'name': d['title']})
                        data = {
                                'name': "%s, %s" % (d['family_name'], d['given_name']),
                                'title': title_id,
                                'code': d['code'],
                                'doctor': True
                                }
                        doctor_id = partner_pool.create(cr, uid, data)
                    else:
                        doctor_id > 1 and _logger.warn("More than one doctor found with code '%s' passed id=%s" 
                                                       % (d['code'], doctor_id[0]))
                        doctor_id = doctor_id[0]
                    d['type'] == 'r' and ref_doctor_ids.append(doctor_id)
                    d['type'] == 'c' and con_doctor_ids.append(doctor_id)
                ref_doctor_ids and vals_copy.update({'ref_doctor_ids': [[4, id] for id in ref_doctor_ids]})
                con_doctor_ids and vals_copy.update({'con_doctor_ids': [[4, id] for id in con_doctor_ids]})
            except:
                _logger.warn("Can't evaluate 'doctors': %s" % (vals['doctors']))   
        super(nh_clinical_adt_patient_admit, self).submit(cr, uid, activity_id, vals_copy, context)
        return res 

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_patient_admit, self).complete(cr, uid, activity_id, context)
        api_pool = self.pool['nh.clinical.api']
        admit_activity = api_pool.get_activity(cr, uid, activity_id)        
        admission_activity = api_pool.create_complete(cr, SUPERUSER_ID, 'nh.clinical.patient.admission',
                                       {'creator_id': activity_id}, 
                                       # FIXME! pos_id should be taken from adt_user.pos_id
                                       {'pos_id': admit_activity.data_ref.suggested_location_id.pos_id.id,
                                        'patient_id': admit_activity.patient_id.id,
                                        'suggested_location_id': admit_activity.data_ref.suggested_location_id.id,
                                        'start_date': admit_activity.data_ref.start_date})
        spell_activity = [a for a in admission_activity.created_ids if a.data_model == 'nh.clinical.spell'][0]
        api_pool.write_activity(cr, SUPERUSER_ID, activity_id, {'parent_id': spell_activity.id})
        return res  
    
    def demo_values(self, cr, uid, values={}):
        fake = self.next_seed_fake()
        api =self.pool['nh.clinical.api']
        v = {}
        # if 'other_identifier' not passed register new patient and use it's data
        if 'other_identifier' not in values:
            reg_pool = self.pool['nh.clinical.adt.patient.register']
            reg_activity_id = reg_pool.create_activity(cr, uid, {}, {}, {'demo': True})
            reg_data = api.get_activity_data(cr, uid, reg_activity_id)
            v.update({'other_identifier': reg_data['other_identifier']})
        if 'location' not in values:
            location_pool = self.pool['nh.clinical.location']
            wards = api.location_map(cr, uid, pos_ids=[reg_data['pos_id']], usages=['wards'])
            if not wards:
                ward_location_id = location_pool.create(cr, uid, {}, {'demo': True, 'demo_method': 'demo_values_ward'})
                wards = api.location_map(cr, uid, location_ids=[ward_location_id])
            ward_id = fake.random_element(wards.keys())
            v.update({'location': wards[ward_id]['code']})
        v.update(values)
        return v    
    
class nh_clinical_adt_patient_cancel_admit(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_admit'
    _inherit = ['nh.activity.data']  
    _description = 'ADT Cancel Patient Admit'    
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier','=',vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s" 
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]        
        vals_copy = vals.copy()
        vals_copy.update({'pos_id': user.pos_id.id, 'patient_id':patient_id})
        res = super(nh_clinical_adt_patient_cancel_admit, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        admit_cancel_activity = activity_pool.browse(cr, uid, activity_id)
        # get admit activity
        api_pool = self.pool['nh.clinical.api']
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, SUPERUSER_ID, admit_cancel_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity, msg="Patient id=%s has no started spell!" % admit_cancel_activity.data_ref.patient_id.id)
        # admit-admission-spell
        admit_activity_id = spell_activity.creator_id \
                            and spell_activity.creator_id.creator_id\
                            and spell_activity.creator_id.creator_id.id \
                            or False
        except_if(not admit_activity_id, msg="adt.admit activity is not found!")
        admit_activity = activity_pool.browse(cr, uid, admit_activity_id)
        # get all children and created activity_ids
        activity_ids = []
        next_level_activity_ids = []

        next_level_activity_ids.extend([child.id for child in admit_activity.child_ids])
        next_level_activity_ids.extend([created.id for created in admit_activity.created_ids])
        activity_ids.extend(next_level_activity_ids)
        #import pdb; pdb.set_trace()
        while next_level_activity_ids:
            for activity in activity_pool.browse(cr, uid, next_level_activity_ids):
                next_level_activity_ids = [child.id for child in activity.child_ids]
                next_level_activity_ids.extend([created.id for created in activity.created_ids])            
                activity_ids.extend(next_level_activity_ids)
        activity_ids = list(set(activity_ids)) 
        activity_id in activity_ids and activity_ids.remove(activity_id)
        _logger.info("Starting activities cancellation due to adt.pateint.cancel_admit activity completion...")       
        for activity in activity_pool.browse(cr, uid, activity_ids):
            if activity.state not in ['completed', 'cancelled']:
                activity_pool.cancel(cr, uid, activity.id)
        res = super(nh_clinical_adt_patient_cancel_admit, self).complete(cr, uid, activity_id, context)
        return res


class nh_clinical_adt_patient_discharge(orm.Model):
    _name = 'nh.clinical.adt.patient.discharge'
    _inherit = ['nh.activity.data']  
    _description = 'ADT Patient Discharge'
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'discharge_date': fields.datetime('Discharge Date')
    }

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        patient_pool = self.pool['nh.clinical.patient']
        discharge_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', discharge_activity.data_ref.other_identifier)], context=context)
        except_if(not patient_id, msg="Patient not found!")
        patient_id = patient_id[0]
        spell_activity = api_pool.get_patient_spell_activity_browse(cr, SUPERUSER_ID, patient_id, context=context)
        except_if(not spell_activity.id, msg="Patient was not admitted!")
        res = super(nh_clinical_adt_patient_discharge, self).complete(cr, uid, activity_id, context)
        discharge_pool = self.pool['nh.clinical.patient.discharge']
        discharge_activity_id = discharge_pool.create_activity(
            cr, SUPERUSER_ID,
            {'creator_id': activity_id,
             'parent_id': spell_activity.id},
            {'patient_id': patient_id,
             'discharge_date': discharge_activity.data_ref.discharge_date}, context=context)
        activity_pool.complete(cr, SUPERUSER_ID, discharge_activity_id, context=context)
        return res 

class nh_clinical_adt_patient_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.transfer'
    _inherit = ['nh.activity.data']
    _description = 'ADT Patient Transfer'      
    _columns = {
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),                
        'location': fields.text('Location'),
        'from_location_id': fields.many2one('nh.clinical.location', 'Origin Location'),
        'location_id': fields.many2one('nh.clinical.location', 'Transfer Location'),
    }
    
    def submit(self, cr, uid, activity_id, vals, context=None):
        except_if(not ('other_identifier' in vals or 'patient_identifier' in vals), msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['nh.clinical.patient']
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        other_identifier = vals.get('other_identifier')
        patient_identifier = vals.get('patient_identifier')
        domain = []
        other_identifier and domain.append(('other_identifier','=',other_identifier))
        patient_identifier and domain.append(('patient_identifier','=',patient_identifier))
        domain = domain and ['|']*(len(domain)-1) + domain
        print "transfer domain: ", domain
        patient_id = patient_pool.search(cr, uid, domain)
        except_if(not patient_id, msg="Patient not found!")
        #activity = activity_pool.browse(cr, uid, activity_id, context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, uid, patient_id[0], context=context)
        except_if(not spell_activity_id, msg="Active spell not found for patient.id=%s !" % patient_id[0])
        spell_activity = activity_pool.browse(cr, uid, spell_activity_id, context=context)
        patient_id = patient_id[0]           
        location_pool = self.pool['nh.clinical.location']
        location_id = location_pool.search(cr, uid, [('code', '=', vals['location'])], context=context)
        if not location_id:
            _logger.warn("ADT transfer location '%s' not found! Will automatically create one" % vals['location'])
            location_pool = self.pool['nh.clinical.location']
            location_id = location_pool.create(cr, uid, {
                'name': vals['location'],
                'code': vals['location'],
                'pos_id': spell_activity.location_id.pos_id.id,
                'type': 'poc',
                'usage': 'ward'
            }, context=context)
        else:
            location_id = location_id[0]
        from_location_id = spell_activity.location_id.parent_id.id if spell_activity.location_id.usage == 'bed' else spell_activity.location_id.id
        if spell_activity.location_id.usage not in ['ward', 'bed']:
            placement_activity_id = activity_pool.search(cr, uid, [
                ('state', 'not in', ['completed', 'cancelled']),
                ('data_model', '=', 'nh.clinical.patient.placement'),
                ('patient_id', '=', patient_id)], context=context)
            if placement_activity_id:
                placement_activity = activity_pool.browse(cr, uid, placement_activity_id[0], context=context)
                from_location_id = placement_activity.data_ref.suggested_location_id.id
        vals.update({'location_id': location_id, 'from_location_id': from_location_id})
        super(nh_clinical_adt_patient_transfer, self).submit(cr, uid, activity_id, vals, context)

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_patient_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        move_pool = self.pool['nh.clinical.patient.move']
        transfer_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        # patient move
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, transfer_activity.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,{
            'parent_id': spell_activity_id,
            'creator_id': activity_id
        }, {
            'patient_id': transfer_activity.patient_id.id,
            'location_id': transfer_activity.data_ref.location_id.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 'nh.clinical.patient.placement', context=context)
        placement_pool = self.pool['nh.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': transfer_activity.patient_id.id,
            'suggested_location_id': transfer_activity.data_ref.location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res
        

class nh_clinical_adt_patient_merge(orm.Model):
    _name = 'nh.clinical.adt.patient.merge'
    _inherit = ['nh.activity.data'] 
    _description = 'ADT Patient Merge'
    _columns = {
        'from_identifier': fields.text('From patient Identifier'),
        'into_identifier': fields.text('Into Patient Identifier'),        
    }

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_patient_merge, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        merge_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        except_if(not (merge_activity.data_ref.from_identifier and merge_activity.data_ref.into_identifier), msg="from_identifier or into_identifier not found in submitted data!")
        patient_pool = self.pool['nh.clinical.patient']
        from_id = patient_pool.search(cr, uid, [('other_identifier', '=', merge_activity.data_ref.from_identifier)])
        into_id = patient_pool.search(cr, uid, [('other_identifier', '=', merge_activity.data_ref.into_identifier)])
        except_if(not(from_id and into_id), msg="Source or destination patient not found!")
        from_id = from_id[0]
        into_id = into_id[0]
        # compare and combine data. may need new cursor to have the update in one transaction
        for model_name in self.pool.models.keys():
            model_pool = self.pool[model_name]
            if model_name.startswith("nh.clinical") and 'patient_id' in model_pool._columns.keys() and model_name != self._name and model_name != 'nh.clinical.notification' and model_name != 'nh.clinical.patient.observation':
                ids = model_pool.search(cr, uid, [('patient_id', '=', from_id)], context=context)
                if ids:
                    model_pool.write(cr, uid, ids, {'patient_id': into_id}, context=context)
        activity_ids = activity_pool.search(cr, uid, [('patient_id', '=', from_id)], context=context)
        activity_pool.write(cr, uid, activity_ids, {'patient_id': into_id}, context=context)
        from_data = patient_pool.read(cr, uid, from_id, context)
        into_data = patient_pool.read(cr, uid, into_id, context)
        vals_into = {}
        for fk, fv in from_data.iteritems():
            if not fv:
                continue
            if fv and into_data[fk] and fv != into_data[fk]:
                pass
            if fv and not into_data[fk]:
                if '_id' == fk[-3:]:
                    vals_into.update({fk: fv[0]})
                else:
                    vals_into.update({fk: fv})
        res['merge_into_update'] = patient_pool.write(cr, uid, into_id, vals_into, context)
        res['merge_from_deactivate'] = patient_pool.write(cr, uid, from_id, {'active': False}, context)
        return res
        

class nh_clinical_adt_patient_update(orm.Model):
    _name = 'nh.clinical.adt.patient.update'
    _inherit = ['nh.activity.data'] 
    _description = 'ADT Patient Update'     
    _columns = {
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'patient_identifier': fields.text('patientId'),
        'other_identifier': fields.text('otherId'),
        'family_name': fields.text('familyName'),
        'given_name': fields.text('givenName'),
        'middle_names': fields.text('middleName'),
        'dob': fields.datetime('DOB'),
        'gender': fields.char('Gender', size=1),
        'sex': fields.char('Sex', size=1),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        vals_copy = vals.copy()
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        except_if(not 'patient_identifier' in vals_copy.keys() and not 'other_identifier' in vals_copy.keys(),
              msg="patient_identifier or other_identifier not found in submitted data!")
        patient_pool = self.pool['nh.clinical.patient']
        hospital_number = vals_copy.get('other_identifier')
        nhs_number = vals_copy.get('patient_identifier')
        if hospital_number:
            patient_domain = [('other_identifier', '=', hospital_number)]
            del vals_copy['other_identifier']
        else:
            patient_domain = [('patient_identifier', '=', nhs_number)]
            del vals_copy['patient_identifier']
        patient_id = patient_pool.search(cr, uid, patient_domain, context=context)
        except_if(not patient_id, msg="Patient doesn't exist! Data: %s" % patient_domain)
        res = patient_pool.write(cr, uid, patient_id, vals_copy, context=context)
        vals_copy.update({'patient_id': patient_id[0], 'other_identifier': hospital_number, 'patient_identifier': nhs_number})
        super(nh_clinical_adt_patient_update, self).submit(cr, uid, activity_id, vals_copy, context)
        return res


class nh_clinical_adt_spell_update(orm.Model):

    _name = 'nh.clinical.adt.spell.update'
    _inherit = ['nh.activity.data']
    _description = 'ADT Spell Update'
    _columns = {
        'suggested_location_id': fields.many2one('nh.clinical.location', 'Suggested Location', help="Location suggested by ADT for placement. Usually ward."),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'location': fields.text('Location'),
        'code': fields.text("Code"),
        'start_date': fields.datetime("ADT Start Date"),
        'other_identifier': fields.text("Other Identifier"),
        'doctors': fields.text("Doctors"),
        'ref_doctor_ids': fields.many2many('res.partner', 'ref_doctor_admit_rel', 'admit_id', 'doctor_id', "Referring Doctors"),
        'con_doctor_ids': fields.many2many('res.partner', 'con_doctor_admit_rel', 'admit_id', 'doctor_id', "Consulting Doctors"),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        res = {}
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        # location validation
        location_pool = self.pool['nh.clinical.location']
        suggested_location_id = location_pool.search(cr, SUPERUSER_ID,
                                                    [('code','=',vals['location']),
                                                     ('id','child_of',user.pos_id.location_id.id)])
        if not suggested_location_id:
            _logger.warn("ADT suggested_location '%s' not found! Will automatically create one" % vals['location'])
            location_pool = self.pool['nh.clinical.location']
            suggested_location_id = location_pool.create(cr, uid, {
                'name': vals['location'],
                'code': vals['location'],
                'pos_id': user.pos_id.id,
                'type': 'poc',
                'usage': 'ward'
            }, context=context)
        else:
            suggested_location_id = suggested_location_id[0]
        # patient validation
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s"
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()
        vals_copy.update({'suggested_location_id': suggested_location_id})
        vals_copy.update({'patient_id': patient_id, 'pos_id': user.pos_id.id})
        # doctors
        if vals.get('doctors'):
            try:
                doctors = eval(str(vals['doctors']))
                ref_doctor_ids = []
                con_doctor_ids = []
                partner_pool = self.pool['res.partner']
                for d in doctors:
                    doctor_id = partner_pool.search(cr, uid, [['code', '=', d['code']]])
                    if not doctor_id:
                        if d['title']:
                            d['title'] = d['title'].strip()
                            title_pool = self.pool['res.partner.title']
                            title_id = title_pool.search(cr, uid, [['name', '=', d['title']]])
                            title_id = title_id and title_id[0] or title_pool.create(cr, uid, {'name': d['title']})
                        data = {
                                'name': "%s, %s" % (d['family_name'], d['given_name']),
                                'title': title_id,
                                'code': d['code'],
                                'doctor': True
                                }
                        doctor_id = partner_pool.create(cr, uid, data)
                    else:
                        doctor_id > 1 and _logger.warn("More than one doctor found with code '%s' passed id=%s"
                                                       % (d['code'], doctor_id[0]))
                        doctor_id = doctor_id[0]
                    d['type'] == 'r' and ref_doctor_ids.append(doctor_id)
                    d['type'] == 'c' and con_doctor_ids.append(doctor_id)
                ref_doctor_ids and vals_copy.update({'ref_doctor_ids': [[4, id] for id in ref_doctor_ids]})
                con_doctor_ids and vals_copy.update({'con_doctor_ids': [[4, id] for id in con_doctor_ids]})
            except:
                _logger.warn("Can't evaluate 'doctors': %s" % (vals['doctors']))
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id)

        super(nh_clinical_adt_spell_update, self).submit(cr, uid, activity_id, vals_copy, context)
        self.write(cr, uid, activity.data_ref.id, vals_copy)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_spell_update, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        update_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, update_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        spell_activity = activity_pool.browse(cr, SUPERUSER_ID, spell_activity_id, context=context)
        data = {
            'con_doctor_ids': [[6, 0,  [d.id for d in update_activity.data_ref.con_doctor_ids]]],
            'ref_doctor_ids': [[6, 0, [d.id for d in update_activity.data_ref.ref_doctor_ids]]],
            'location_id': update_activity.data_ref.pos_id.lot_admission_id.id,
            'code': update_activity.data_ref.code,
            'start_date': update_activity.data_ref.start_date if update_activity.data_ref.start_date < spell_activity.data_ref.start_date else spell_activity.data_ref.start_date
        }
        res = activity_pool.submit(cr, uid, spell_activity_id, data, context=context)
        activity_pool.write(cr, SUPERUSER_ID, activity_id, {'parent_id': spell_activity_id})
        # patient move
        move_pool = self.pool['nh.clinical.patient.move']
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
            {'parent_id': spell_activity_id, 'creator_id': activity_id},
            {'patient_id': update_activity.data_ref.patient_id.id,
             'location_id': update_activity.data_ref.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 'nh.clinical.patient.placement', context=context)
        placement_pool = self.pool['nh.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': update_activity.data_ref.patient_id.id,
            'suggested_location_id': update_activity.data_ref.suggested_location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res


class nh_clinical_adt_patient_cancel_discharge(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_discharge'
    _inherit = ['nh.activity.data']
    _description = 'ADT Cancel Patient Discharge'
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s"
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()
        vals_copy.update({'pos_id': user.pos_id.id, 'patient_id': patient_id})
        res = super(nh_clinical_adt_patient_cancel_discharge, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        move_pool = self.pool['nh.clinical.patient.move']
        res = {}
        cancel_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        patient_id = cancel_activity.data_ref.patient_id.id
        spell_activity_id = api_pool.activity_map(cr, uid, patient_ids=[patient_id], 
                                                  data_models=['nh.clinical.spell'], states=['started'])
        except_if(spell_activity_id, msg="Patient was not discharged or was admitted again!")
        
        super(nh_clinical_adt_patient_cancel_discharge, self).complete(cr, uid, activity_id, context=context)

        cancel_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        spell_activity_id = api_pool.activity_map(cr, uid, patient_ids=[patient_id], 
                                                  data_models=['nh.clinical.spell'], states=['started'])
#         #get_patient_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
#         
#         spell_activity_id = dict(api_pool.patient_map(cr, uid, patient_ids=[cancel_activity.data_ref.patient_id.id])[0][1])['previous']
#         #api_pool.get_patient_last_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
        except_if(spell_activity_id, msg="Patient was not discharged!")
        domain = [('data_model', '=', 'nh.clinical.adt.patient.discharge'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        last_discharge_activity_id = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        except_if(not last_discharge_activity_id, msg='Patient was not discharged!')
        spell_activity_id = api_pool.activity_map(cr, uid, patient_ids=[patient_id],
                                                  data_models=['nh.clinical.spell'], states=['completed']).keys()[0]
        domain = [('data_model', '=', 'nh.clinical.patient.move'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        move_activity_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        move_activity = activity_pool.browse(cr, uid, move_activity_ids[1], context=context)
        res[self._name] = activity_pool.write(cr, uid, spell_activity_id, {'state': 'started'}, context=context)
        if move_activity.location_id.usage == 'bed':
            if move_activity.location_id.is_available:
                move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                    {'parent_id': spell_activity_id, 'creator_id': activity_id},
                    {'patient_id': cancel_activity.data_ref.patient_id.id,
                     'location_id': move_activity.location_id.id},
                    context=context)
                res[move_pool._name] = move_activity_id
                activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
            else:
                move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                    {'parent_id': spell_activity_id, 'creator_id': activity_id},
                    {'patient_id': cancel_activity.data_ref.patient_id.id,
                     'location_id': move_activity.location_id.pos_id.lot_admission_id.id},
                    context=context)
                res[move_pool._name] = move_activity_id
                activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
                # patient placement
                api_pool.cancel_open_activities(cr, uid, spell_activity_id, 'nh.clinical.patient.placement', context=context)
                placement_pool = self.pool['nh.clinical.patient.placement']

                placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
                    'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
                    'creator_id': activity_id
                }, {
                    'patient_id': cancel_activity.data_ref.patient_id.id,
                    'suggested_location_id': move_activity.location_id.parent_id.id
                }, context=context)
                res[placement_pool._name] = placement_activity_id
        res['spell_state_change'] = activity_pool.write(cr, uid, spell_activity_id, {'state': 'started'}, context=context)
        return res


class nh_clinical_adt_patient_cancel_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_transfer'
    _inherit = ['nh.activity.data']
    _description = 'ADT Cancel Patient Transfer'
    _columns = {
        'other_identifier': fields.text('otherId', required=True),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def submit(self, cr, uid, activity_id, vals, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        except_if(not user.pos_id or not user.pos_id.location_id, msg="POS location is not set for user.login = %s!" % user.login)
        patient_pool = self.pool['nh.clinical.patient']
        patient_id = patient_pool.search(cr, SUPERUSER_ID, [('other_identifier', '=', vals['other_identifier'])])
        except_if(not patient_id, msg="Patient not found!")
        if len(patient_id) > 1:
            _logger.warn("More than one patient found with 'other_identifier' = %s! Passed patient_id = %s"
                                    % (vals['other_identifier'], patient_id[0]))
        patient_id = patient_id[0]
        vals_copy = vals.copy()
        vals_copy.update({'patient_id': patient_id})
        res = super(nh_clinical_adt_patient_cancel_transfer, self).submit(cr, uid, activity_id, vals_copy, context)
        return res

    def complete(self, cr, uid, activity_id, context=None):
        res = {}
        super(nh_clinical_adt_patient_cancel_transfer, self).complete(cr, uid, activity_id, context=context)
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        move_pool = self.pool['nh.clinical.patient.move']
        cancel_activity = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        domain = [('data_model', '=', 'nh.clinical.adt.patient.transfer'),
                  ('state', '=', 'completed'),
                  ('patient_id', '=', cancel_activity.data_ref.patient_id.id)]
        transfer_activity_ids = activity_pool.search(cr, uid, domain, order='date_terminated desc', context=context)
        except_if(not transfer_activity_ids, msg='Patient was not transfered!')
        transfer_activity = activity_pool.browse(cr, uid, transfer_activity_ids[0], context=context)

        # patient move
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, cancel_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id, msg="Spell not found!")
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,{
            'parent_id': spell_activity_id,
            'creator_id': activity_id
        }, {
            'patient_id': cancel_activity.data_ref.patient_id.id,
            'location_id': transfer_activity.data_ref.from_location_id.pos_id.lot_admission_id.id},
            context=context)
        res[move_pool._name] = move_activity_id
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id, context)
        # patient placement
        api_pool.cancel_open_activities(cr, uid, spell_activity_id, 'nh.clinical.patient.placement', context=context)
        placement_pool = self.pool['nh.clinical.patient.placement']

        placement_activity_id = placement_pool.create_activity(cr, SUPERUSER_ID, {
            'parent_id': spell_activity_id, 'date_deadline': (dt.now()+td(minutes=5)).strftime(DTF),
            'creator_id': activity_id
        }, {
            'patient_id': cancel_activity.data_ref.patient_id.id,
            'suggested_location_id': transfer_activity.data_ref.from_location_id.id
        }, context=context)
        res[placement_pool._name] = placement_activity_id
        return res