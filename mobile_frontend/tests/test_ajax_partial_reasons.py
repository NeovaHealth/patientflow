__author__ = 'colin'

import openerp.tests
import helpers

class TestAjaxPartialReasons(openerp.tests.HttpCase):

    # test score calculation ajax
    def test_ajax_partial_obs_reasons(self):
        self.phantom_js('/ajax_test/', helpers.PARTIAL_REASONS_AJAX, 'document', login='norah')