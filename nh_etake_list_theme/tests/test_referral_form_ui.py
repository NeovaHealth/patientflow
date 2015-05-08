__author__ = 'neova'

import openerp.tests

class TestReferralFormUI(openerp.tests.HttpCase):

    def test_referral_form_creation(self):
        self.phantom_js("/web",
            "openerp.Tour.run('referral_nurse_able_to_update_patient_arrival', 'test')",
            "openerp.Tour.tours.referral_nurse_able_to_update_patient_arrival", login="taylor"
        )