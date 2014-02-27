from openerp.tests import common
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.osv import orm, fields, osv




admission_type_data = {'summary': 'Patient Admission', 'data_model': 't4.clinical.patient.admission'}


class TestAdmission(common.SingleTransactionCase):
    def setUp(self):
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        
                
        self.task_pool = self.registry('t4.clinical.task')
        self.hw_pool = self.registry('t4.clinical.patient.observation.height_weight')
        self.patient_id = self.xml2db_id("demo_patient_donald")
        self.location_id = self.xml2db_id("demo_location_uhg")
        self.admission_data = {'location_id': self.location_id, 'patient_id':self.patient_id}
        self.adm_task_id = self.adm_pool.create_task(self.cr, self.uid, {}, self.admission_data)
        
        super(TestAdmission, self).setUp()

    def xml2db_id(self, xmlid):
        imd_pool = self.registry('ir.model.data')
        imd_id = imd_pool.search(self.cr, self.uid, [('name','=', xmlid)])
        db_id = imd_id and imd_pool.browse(self.cr, self.uid, imd_id[0]).res_id or False
        return db_id
    
    def test_complete(self):
        """
        when:
            adm_task.complete
        then:
            adm_task.parent_id.data_model == 't4.clinical.spell'
            move_pool.get_location() == self.location
            
        """
        self.task_pool.assign(self.cr, self.uid, self.adm_task_id, 1)
        self.task_pool.start(self.cr, self.uid, self.adm_task_id)
        #import pdb; pdb.set_trace()
        self.task_pool.complete(self.cr, self.uid, self.adm_task_id)
        adm_task = self.task_pool.browse(self.cr, self.uid, self.adm_task_id)
        
        self.assertTrue(adm_task.parent_id.data_model == 't4.clinical.spell', 'Data model')
        location = self.move_pool.get_location(self.cr, self.uid, self.patient_id)
        self.assertTrue( location and location.id == self.location_id, 'Data model')
        
     
        
        