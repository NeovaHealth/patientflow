import openerp.tests

class TestReferralFormUI( openerp.tests.HttpCase):


    def test_referral_nurse_able_to_create_referral(self):
        self.phantom_js("/web",
            "openerp.Tour.run('referral_nurse_able_to_create_referral', 'test')",
            "openerp.Tour.tours.referral_nurse_able_to_create_referral", login="taylor"
        )
    def test_junior_doctor(self):
        self.phantom_js("/web",
            "openerp.Tour.run('junior_doctor', 'test')",
            "openerp.Tour.tours.junior_doctor", login="james"
        )
    def test_registrar(self):
        self.phantom_js("/web",
            "openerp.Tour.run('registrar', 'test')",
            "openerp.Tour.tours.registrar_able_to_create_referrals", login="roger"
        )
    def test_consultant(self):
        self.phantom_js("/web",
            "openerp.Tour.run('consultant', 'test')",
            "openerp.Tour.tours.consultant", login="caroline"
        )
    def test_senior_doctor(self):
        self.phantom_js("/web",
            "openerp.Tour.run('senior_doctor', 'test')",
            "openerp.Tour.tours.senior_doctor", login="don"
        )



