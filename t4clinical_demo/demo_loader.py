from openerp.osv import orm, fields, osv
from openerp.addons.t4clinical_base.task import except_if

import logging        
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()


class DemoLoader(orm.AbstractModel):
    _name = 'demo.loader'

    def get_register_data(self, qty=5):
        data = []
        n = 0
        lseed = str(fake.random_int(min=1001, max=9999))
        while n <= qty:

            gender = fake.random_element(array=('M','F'))
            data.append({
                    'family_name': fake.last_name(), 
                    'given_name': fake.first_name(),
                    'other_identifier': lseed + str(n).zfill(5),
                    'dob': fake.date_time_between(start_date="-80y", end_date="-10y").strftime("%Y-%m-%d %H:%M:%S"), 
                    'gender': gender, 
                    'sex': gender         
                   })
            n += 1
            
        return data
    
    def get_admit_data(self, register_data=[], qty=5):
        data = []
        n = 0
        lseed = str(fake.random_int(min=10001, max=99999)).zfill(4)
        for r in register_data:
            if n > qty:
                break
            t = {}
            t.update({'other_identifier':r['other_identifier']})
            t.update({'code': lseed + str(n).zfill(5),
                      'location': 'W'+fake.random_element(array=('8','9')), 
                      'start_date': fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S")
                      })
            data.append(t)
            n += 1
        return data
        
    def get_placement_data(self, cr, uid, qty=5):
        data = []
        # must be get_available location_ids(type, usage)
        locations = ['B'+str(n) for n in range(1,8)]
        location_ids = self.pool['t4.clinical.location'].search(cr, uid, [('code','in',locations)])
        n = 0
        for location_id in location_ids:
            if n > qty:
                break
            data.append({'location_id': location_id})
            n += 1
        return data
    
    
    def get_ews_data(self, cr, uid, patient_ids):
        data = []
        # must be get_available location_ids(type, usage)
        locations = ['B'+str(n) for n in range(1,8)]
        location_ids = self.pool['t4.clinical.location'].search(cr, uid, [('code','in',locations)])
        n = 0
        for patient_id in patient_ids:
                data.append({
                            'patient_id': patient_id,
                            'respiration_rate': fake.random_int(min=10, max=23),
                            'indirect_oxymetry_spo2': fake.random_int(min=95, max=100),
                            #'oxygen_administration_flag': False,
                            'body_temperature': float(fake.random_int(min=36, max=41)),
                            'blood_pressure_systolic': fake.random_int(min=115, max=150),
                            'blood_pressure_diastolic': fake.random_int(min=60, max=100),
                            'pulse_rate': fake.random_int(min=60, max=80),
                            'avpu_text': fake.random_element(array=('A','V','P','U'))                         
                         })
        return data   

    
    def scenario1(self, cr, uid, rollback=True):
        register_data = self.get_register_data(1000)
        admit_data = self.get_admit_data(register_data, 800)
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        task_pool = self.pool['t4.clinical.task']
        placement_pool = self.pool['t4.clinical.patient.placement']

        for rd in register_data:
            register_pool.create_task(cr, uid, {}, rd)
        for ad in admit_data:
            admit_pool.create_task(cr, uid, {}, ad)    
        placement_data = self.get_placement_data(cr, uid, qty=700)
        placement_task_ids = task_pool.search(cr, uid, [('data_model','=',placement_pool._name)])
        n = 0
        patient_ids = []
        #import pdb; pdb.set_trace()
        for placement_task_id in placement_task_ids:
            placement_task = task_pool.browse(cr, uid, placement_task_id)
            patient_ids.append(placement_task.patient_id.id)
            if n >=len(placement_data):
                break
            task_pool.submit(cr, uid, placement_task_id,  placement_data[n])
            task_pool.start(cr, uid, placement_task_id) 
            task_pool.complete(cr, uid, placement_task_id) 
            n += 1
        ews_pool = self.pool['t4.clinical.patient.observation.ews']
        for n in range(1,100):
            ews_data = self.get_ews_data(cr, uid, patient_ids)
            for ews in ews_data:
                        # task frequency
                task_pool.set_task_trigger(cr, uid, ews['patient_id'],'t4.clinical.patient.observation.ews','minute', 15, context=None)  
                ews_task_id = ews_pool.create_task(cr, uid, {}, {'patient_id': ews['patient_id']})
                task_pool.schedule(cr, uid, ews_task_id, 
                   date_scheduled=fake.date_time_between(start_date="-1w", end_date="-1h").strftime("%Y-%m-%d %H:%M:%S"))
                task_pool.submit(cr, uid, ews_task_id, ews)
                task_pool.start(cr, uid, ews_task_id)
                task_pool.complete(cr, uid, ews_task_id)
        except_if(rollback, msg="Rollback")
        return True

    def xml2db_id(self, cr, uid, xmlid):
        imd_pool = self.pool['ir.model.data']
        imd_id = imd_pool.search(cr, uid, [('name', '=', xmlid)])
        imd = imd_pool.browse(cr, uid, imd_id[0])
        return imd.res_id

    def set_patient_to_placement(self, cr, uid, rollback=True):

        register_data = self.get_register_data(0)
        admit_data = self.get_admit_data(register_data, 0)
        register_pool = self.pool['t4.clinical.adt.patient.register']
        admit_pool = self.pool['t4.clinical.adt.patient.admit']
        task_pool = self.pool['t4.clinical.task']
        placement_pool = self.pool['t4.clinical.patient.placement']

        for rd in register_data:
            register_pool.create_task(cr, uid, {}, rd)
        for ad in admit_data:
            admit_pool.create_task(cr, uid, {}, ad)

        #get a wardmanager
        ward_manager_id = self.xml2db_id(cr, uid, 'demo_user_winifred')

        #get placements tasks for ward managers
        placement_task_ids = task_pool.search(cr, ward_manager_id, [('data_model', '=', placement_pool._name),
                                                                    ('state', '=', 'draft')])

        #get available beds for location in placement task (ward)
        for placement_task in task_pool.browse(cr, ward_manager_id, placement_task_ids):
            location_ids = task_pool.get_available_bed_location_ids(cr, ward_manager_id,
                                                                    placement_task.parent_id.location_id.id)
            if location_ids:
                #submit location to placement task
                task_pool.submit(cr, ward_manager_id, placement_task.id, {'location_id': location_ids[0] })
                #complete placement task
                task_pool.complete(cr, ward_manager_id, placement_task.id)


            #assign obs frequency
            task_pool.set_task_trigger(cr, uid, placement_task.patient_id.id, 't4.clinical.patient.observation.ews',
                                   'minute', 30)

        except_if(rollback, msg="Rollback")
        return True