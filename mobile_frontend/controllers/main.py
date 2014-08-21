# -*- coding: utf-8 -*-s
import openerp, re
from openerp import http
from openerp.modules.module import get_module_path
from datetime import datetime
from openerp.http import request
from werkzeug import utils, exceptions
import openerp.addons.web.controllers.main as main

URL_PREFIX = '/mobile/'

URLS = {'patient_list': URL_PREFIX+'patients/',
        'single_patient': URL_PREFIX+'patient/',
        'task_list': URL_PREFIX+'tasks/',
        'single_task': URL_PREFIX+'task/',
        'stylesheet': URL_PREFIX+'src/css/main.css',
        'new_stylesheet': URL_PREFIX+'src/css/new.css',
        'logo': URL_PREFIX+'src/img/logo.png',
        'login': URL_PREFIX+'login',
        'logout': URL_PREFIX+'logout/',
        'task_form_action': URL_PREFIX+'task/submit/',
        'patient_form_action': URL_PREFIX+'patient/submit/',
        }

class MobileFrontend(http.Controller):

    @http.route(URLS['stylesheet'], type='http', auth='public')
    def get_stylesheet(self, *args, **kw):
        with open(get_module_path('mobile_frontend') + '/static/src/css/t4skr.css', 'r') as stylesheet:
            return request.make_response(stylesheet.read(), headers={'Content-Type': 'text/css; charset=utf-8'})

    @http.route(URLS['new_stylesheet'], type='http', auth='public')
    def get_new_stylesheet(self, *args, **kw):
        with open(get_module_path('mobile_frontend') + '/static/src/css/new.css', 'r') as stylesheet:
            return request.make_response(stylesheet.read(), headers={'Content-Type': 'text/css; charset=utf-8'})

    @http.route('/mobile/src/fonts/<xmlid>', auth='public', type='http')
    def get_font(self, xmlid, *args, **kw):
        with open(get_module_path('mobile_frontend') + '/static/src/fonts/' + xmlid, 'r') as font:
            return request.make_response(font.read(), headers={'Content-Type':'application/font-woff'})


    @http.route(URLS['logo'], type='http', auth='public')
    def get_logo(self, *args, **kw):
        with open(get_module_path('mobile_frontend') + '/static/src/img/t4skrlogo.png', 'r') as logo:
            return request.make_response(logo.read(), headers={'Content-Type': 'image/png'})

    # Session Management
    @http.route(URL_PREFIX, type='http', auth='none')
    def index(self, *args, **kw):
        #ensure_db(redirect='http://google.com')
        if request.session.uid:
            return utils.redirect(URLS['task_list'], 303)
        else:
            return utils.redirect(URLS['login'], 303)

    @http.route(URLS['login'], type="http", auth="none")
    def mobile_login(self, *args, **kw):

        if not request.uid:
            request.uid = openerp.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except openerp.exceptions.AccessDenied:
            values['databases'] = None


        if request.httprequest.method == 'GET':
            login_template = open(get_module_path('mobile_frontend') + '/views/login.html', 'rb').read()
            return request.make_response(login_template.format(stylesheet=URLS['stylesheet'], logo=URLS['logo'], form_action=URLS['login'], errors=''))
        if request.httprequest.method == 'POST':
            uid = request.session.authenticate('t4clinical_default_config', request.params['username'], request.params['password'])
            if uid is not False:
                request.uid = uid
                return utils.redirect(URLS['task_list'], 303)
            return request.render('mobile_frontend.login', qcontext={'urls': URLS, 'errors': True})


    @http.route(URLS['patient_list'], type='http', auth="user")
    def get_patients(self, *args, **kw):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        users_api = request.registry['res.users']
        user_ids = users_api.search(cr, uid, [['login', '=', 'norah']], context=context)
        new_uid = user_ids[0]
        patient_api = request.registry['t4.clinical.api.external']
        patients = patient_api.get_patients(cr, new_uid, [], context=context)
        for patient in patients:
            patient['url'] = '{0}{1}'.format(URLS['single_patient'], patient['id'])
            patient['color'] = 'level-one'
            patient['trend_icon'] = 'icon-{0}-arrow'.format(patient['ews_trend'])
            patient['deadline_time'] = patient['next_ews_time']
            patient['summary'] = patient['summary'] if patient.get('summary') else False
        return request.render('mobile_frontend.patient_task_list', qcontext={'items': patients,
                                                                             'section': 'patient',
                                                                             'username': 'norah',
                                                                             'urls': URLS})

    @http.route(URLS['task_list'], type='http', auth='user')
    def get_tasks(self, *args, **kw):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        users_api = request.registry['res.users']
        user_ids = users_api.search(cr, uid, [['login', '=', 'norah']], context=context)
        new_uid = user_ids[0]
        task_api = request.registry['t4.clinical.api.external']
        tasks = task_api.get_activities(cr, new_uid, [], context=context)
        for task in tasks:
            task['url'] = '{0}{1}'.format(URLS['single_task'], task['id'])
            task['color'] = 'level-one'
            task['trend_icon'] = 'icon-{0}-arrow'.format(task['ews_trend'])
        return request.render('mobile_frontend.patient_task_list', qcontext={'items': tasks,
                                                                             'section': 'task',
                                                                             'username': 'norah',
                                                                             'urls': URLS})

    @http.route(URLS['single_task']+'<task_id>', type='http', auth='user')
    def get_task(self, task_id, *args, **kw):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        users_api = request.registry['res.users']
        user_ids = users_api.search(cr, uid, [['login', '=', 'norah']], context=context)
        new_uid = user_ids[0]
        activity_reg = request.registry['t4.activity']
        api_reg = request.registry['t4.clinical.api.external']
        task_id = int(task_id)
        task = activity_reg.read(cr, uid, task_id, ['user_id', 'data_model', 'summary'], context=context)
        patient = dict()
        patient['url'] = URLS['single_patient'] + '{0}'.format(2)
        patient['name'] = 'Colin is Awesome'
        form = dict()
        form['action'] = URLS['task_form_action']+'{0}'.format(task_id)
        form['type'] = task['data_model']
        form['source-id'] = int(task_id)
        form['source'] = "task"
        form['start'] = datetime.now().strftime('%s')
        if task.get('user_id') and task['user_id'][0] != new_uid:
            return request.render('mobile_frontend.error', qcontext={'error_string': 'Task is taken by another user',
                                                                     'section': 'task',
                                                                     'username': 'norah',
                                                                     'urls': URLS})
        try:
            api_reg.assign(cr, uid, task_id, {'user_id': new_uid}, context=context)
        except Exception:
            #return 'unable to take task'
            a = 0

        if 'notification' in task['data_model']:
            # load notification foo
            form['type'] = re.match(r't4\.clinical\.patient\.notification\.(.*)', task['data_model']).group(1)
            return request.render('mobile_frontend.notification_confirm_cancel', qcontext={'name': task['summary'],
                                                                                 'section': 'task',
                                                                                 'username': 'norah',
                                                                                 'urls': URLS})
        elif 'observation' in task['data_model']:
            # load obs foo
            obs_reg = request.registry[task['data_model']]
            form_desc = obs_reg._form_description
            form['type'] = re.match(r't4\.clinical\.patient\.observation\.(.*)', task['data_model']).group(1)
            for form_input in form_desc:
                if form_input['type'] in ['float', 'integer']:
                    form_input['step'] = 0.1 if form_input['type'] is 'float' else 1
                    form_input['type'] = 'number'
                    form_input['number'] = True
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    #if form_input['target']:
                    #    form_input['target'] = False
                elif form_input['type'] == 'selection':
                    form_input['selection_options'] = []
                    form_input['info'] = ''
                    form_input['errors'] = ''
                    for option in form_input['selection']:
                        opt = dict()
                        opt['value'] = '{0}'.format(option[0])
                        opt['label'] = option[1]
                        form_input['selection_options'].append(opt)

            return request.render('mobile_frontend.observation_entry', qcontext={'inputs': form_desc,
                                                                                      'name': task['summary'],
                                                                                      'patient': patient,
                                                                                      'form': form,
                                                                                      'section': 'task',
                                                                                      'username': 'norah',
                                                                                      'urls': URLS})
        else:
            return request.render('mobile_frontend.error', qcontext={'error_string': 'Task is neither a notification nor an observation',
                                                                     'section': 'task',
                                                                     'username': 'norah',
                                                                     'urls': URLS})

    @http.route(URLS['task_form_action']+'<task_id>', type="http", auth="user")
    def process_form(self, task_id, *args, **kw):
        print 'doing some foo'
        #import pdb; pdb.set_trace()
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        api = request.registry('t4.clinical.api')
        kw_copy = kw.copy()
        del kw_copy['taskId']
        api.submit_complete(cr, uid, int(task_id), kw_copy, context)
        return utils.redirect(URLS['task_list'])

