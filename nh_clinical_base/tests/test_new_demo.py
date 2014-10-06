from openerp.tests.common import SingleTransactionCase
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from openerp import tools
from openerp.tools import config 
from openerp.osv import orm, fields, osv

import logging        
from pprint import pprint as pp
_logger = logging.getLogger(__name__)


class test_base_nhdemo(SingleTransactionCase):
    @classmethod
    def tearDownClass(cls):
        if config['test_commit']:
            cls.cr.commit()
            print "COMMIT"
        else:
            cls.cr.rollback()
            print "ROLLBACK"
        cls.cr.close()
        #import pdb; pdb.set_trace()

    def setUp(self):
        global cr, uid
        cr, uid = self.cr, self.uid


        super(test_base_nhdemo, self).setUp()
        
    def test_user(self):
        global cr, uid
        print "TEST res.users"
        api_demo = self.registry('nh.clinical.api.demo')
        api_demo.create(cr, uid, 'res.users')
        api_demo.create(cr, uid, 'res.users', 'user_hca')
        api_demo.create(cr, uid, 'res.users', 'user_nurse')
        api_demo.create(cr, uid, 'res.users', 'user_ward_manager')
        api_demo.create(cr, uid, 'res.users', 'user_doctor')
        api_demo.create(cr, uid, 'res.users', 'user_adt')
        
    def test_location(self):
        global cr, uid
        print "TEST nh.clinical.location"
        api_demo = self.registry('nh.clinical.api.demo')
        api_demo.create(cr, uid, 'nh.clinical.location')
        api_demo.create(cr, uid, 'nh.clinical.location', 'location_pos')
        api_demo.create(cr, uid, 'nh.clinical.location', 'location_admission')
        api_demo.create(cr, uid, 'nh.clinical.location', 'location_discharge')
        api_demo.create(cr, uid, 'nh.clinical.location', 'location_ward')
        api_demo.create(cr, uid, 'nh.clinical.location', 'location_bed')

    def test_patient(self):
        global cr, uid
        print "TEST nh.clinical.patient"        
        api_demo = self.registry('nh.clinical.api.demo')
        api_demo.create(cr, uid, 'nh.clinical.patient')

    def test_pos(self):
        global cr, uid
        print "TEST nh.clinical.pos"
        api_demo = self.registry('nh.clinical.api.demo')
        api_demo.create(cr, uid, 'nh.clinical.pos')        
        
    def test_device(self):
        global cr, uid
        print "TEST nh.clinical.device and type"
        api_demo = self.registry('nh.clinical.api.demo')
        api_demo.create(cr, uid, 'nh.clinical.device.type')
        api_demo.create(cr, uid, 'nh.clinical.device')   



        