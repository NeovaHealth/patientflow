from openerp.tests import common
from datetime import datetime as dt
from openerp.osv import orm
from dateutil.relativedelta import relativedelta as rd


class TestActivities(common.SingleTransactionCase):

    def setUp(self):

        cr, uid = self.cr, self.uid
        
        self.now = dt.today().strftime('%Y-%m-%d %H:%M:%S')
        self.tomorrow = (dt.today() + rd(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                
        self.activity_pool = self.registry('t4.clinical.activity')
        self.user_pool = self.registry('res.users')

        super(TestActivities, self).setUp()

    def test_nurse_can_see_Activities(self):
        cr, uid = self.cr, self.uid

        self.activity_pool.create_activity()

        nurse_id = self.user_pool.search(cr, uid, [('login', '=', 'winifred')])[0]
        print nurse_id

        Activities = self.activity_pool.search(cr, nurse_id, [])
        self.assertTrue(Activities)



