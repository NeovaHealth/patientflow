__author__ = 'colin'
from openerp.tests import common
import openerp.modules.registry
from BeautifulSoup import BeautifulSoup
import helpers


class PatientListTest(common.SingleTransactionCase):

    def setUp(self):
        super(PatientListTest, self).setUp()

        # set up database connection objects
        self.registry = openerp.modules.registry.RegistryManager.get('t4clinical_test')
        self.uid = 1
        self.host = 'http://localhost:8169'

        # set up pools
        self.patient = self.registry.get('t4.clinical.patient')
        self.patient_visits = self.registry.get('t4.clinical.patient.visit')
        self.tasks = self.registry.get('t4.clinical.task.base')
        self.location = self.registry.get('t4.clinical.pos.delivery')
        self.location_type = self.registry.get('t4.clinical.pos.delivery.type')
        self.users = self.registry.get('res.users')

    def test_patient_list(self):
        cr, uid = self.cr, self.uid

        # Create test patient
        # create environment
        api_demo = self.registry('t4.clinical.api.demo')
        api_demo.build_uat_env(cr, uid, patients=8, placements=4, context=None)

        # get a nurse user
        norah_user = self.users.search(cr, uid, [['login', '=', 'norah']])[0]

        self.context = {
            'lang': 'en_GB',
            'tz': 'Europe/London',
            'uid': 1
        }

        # Call controller
        patient_api = self.registry['t4.clinical.api.external']
        patients = patient_api.get_patients(cr, norah_user, [], context=self.context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(helpers.URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False

        view_obj = self.registry("ir.ui.view")
        get_patients_html = view_obj.render(
            cr, uid, 'mobile_frontend.patient_task_list', {'items': patients,
                                                           'section': 'patient',
                                                           'username': 'norah',
                                                           'urls': helpers.URLS},
            context=self.context)

        # Create BS instances
        patient_list_string = ""
        for patient in patients:
           patient_list_string += helpers.PATIENT_LIST_ITEM.format(patient['url'],
                                                                   patient['deadline_time'],
                                                                   patient['full_name'],
                                                                   patient['ews_score'],
                                                                   patient['trend_icon'],
                                                                   patient['location'],
                                                                   patient['parent_location'])
        example_html = helpers.PATIENT_LIST_HTML.format(patient_list_string)

        get_patients_bs = str(BeautifulSoup(get_patients_html)).replace('\n', '')
        example_patients_bs = str(BeautifulSoup(example_html)).replace('\n', '')

        # Assert that shit
        self.assertEqual(get_patients_bs,
                         example_patients_bs,
                         'DOM from Controller ain\'t the same as DOM from example')
