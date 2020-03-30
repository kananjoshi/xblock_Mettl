# uncompyle6 version 3.5.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.5 (default, Aug  7 2019, 00:51:29) 
# [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]
# Embedded file name: /edx/app/edxapp/venvs/edxapp/lib/python2.7/site-packages/mettl/mettl.py
# Compiled at: 2018-01-16 14:35:23
"""Mettl XBlock"""
from django.conf import settings
if not settings.configured:
    settings.configure(DEBUG=True)
import hmac, urllib, requests, time, json, pkg_resources
from collections import OrderedDict
from hashlib import sha1
from xblock.core import XBlock
from xblock.fragment import Fragment
from django.contrib.auth.models import User
from django.template import Template, Context
from django.views.decorators.csrf import csrf_exempt
from xblock.fields import Scope, Integer, String, Float, Dict

def create_signature(string, secret):
    hashed = hmac.new(str(secret), string, sha1)
    return urllib.quote(hashed.digest().encode('base64').rstrip('\n'))


class MettlXBlock(XBlock):
    """
    Mettl XBlock
    """
    has_score = True
    icon_class = 'problem'
    private_key = '4660ef83-4f6d-4ba6-b8b1-bf6af7f4ecd4'
    public_key = 'c6c519d8-630f-4b9c-99b3-dd48a06e7602'
    display_name = String(display_name='Display Name', help='This name appears in the horizontal navigation at the top of the page.', scope=Scope.settings, default='Mettl XBlock')
    attempts = Integer(display_name='Attempts', help='Defines the number of times a student can attempt the test.', scope=Scope.settings, default=0)
    weight = Float(display_name='Weight', help='Defines the number of points this test is worth', scope=Scope.settings, default=100, values={'min': 0, 'step': 0.1})
    current_assessment_id = Integer(display_name='Current Assessment ID', help='Select one of the above assessment id.', scope=Scope.settings, default='')
    test_button_label = String(display_name='Test Button Label', help='Defines the label for the test button', scope=Scope.settings, default='Click here to start the test')
    test_button_back_color = String(display_name='Test Button Background Color', help='Defines the background color of the test button', scope=Scope.settings, default='#00ACCD')
    test_button_color = String(display_name='Test Button Text Color', help='Defines the text color of the test button', scope=Scope.settings, default='#FFFFFF')
    student_score = Float(display_name='Student Score', scope=Scope.user_state, default=0)
    test_link = Dict(display_name='Start Test Link', scope=Scope.user_state, default={})
    error_code = ''
    error_msg = ''

    def set_auth_keys(self):
        try:
            with open(__file__.rsplit('/', 1)[0] + '/mettl_auth_keys.json', 'r') as (json_data):
                keys = json.load(json_data)
                self.private_key, self.public_key = keys['PRIVATE_KEY'], keys['PUBLIC_KEY']
        except IOError:
            with open(__file__.rsplit('/', 1)[0] + '/mettl_auth_keys.json', 'w+') as (json_data):
                json.dump({'PUBLIC_KEY': '', 'PRIVATE_KEY': ''}, json_data)
                self.private_key, self.public_key = ('', '')

    def raise_error(self, err_code, err_msg):
        self.error_code = err_code
        self.error_msg = err_msg

    def has_any_error(self):
        if self.error_code:
            return (self.error_code, self.error_msg)
        else:
            return False

    def get_all_assessments(self, limit='20'):
        """
        Returns all assessments list from Mettl
        """
        self.set_auth_keys()
        ts = str(time.time())
        string = ('GEThttp://api.mettl.com/v1/assessments\n{ak}\n{limit}\n{ts}').format(ak=self.public_key, limit=limit, ts=ts)
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/assessments?ak={ak}&limit={limit}&ts={ts}&asgn={asgn}').format(ak=self.public_key, limit=limit, ts=ts, asgn=asgn)
        try:
            resp = requests.get(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    assessments = {assess['id']:assess['name'] for assess in resp_json['assessments']}
                    return assessments
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''
        else:
            return ''

    def get_assessment_detail(self, assessment_id):
        """
        Returns details of a specific assessment.
        """
        self.set_auth_keys()
        ts = str(time.time())
        string = ('GEThttp://api.mettl.com/v1/assessments/{assessment_id}\n{ak}\n{ts}').format(ak=self.public_key, assessment_id=str(assessment_id), ts=ts)
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/assessments/{assessment_id}?ak={ak}&ts={ts}&asgn={asgn}').format(ak=self.public_key, assessment_id=str(assessment_id), ts=ts, asgn=asgn)
        try:
            resp = requests.get(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    return resp_json['assessment']
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''
        else:
            return ''

    def get_all_schedules(self, assessment_id):
        """
        Returns all schedules list from Mettl
        """
        self.set_auth_keys()
        ts = str(time.time())
        string = ('GEThttp://api.mettl.com/v1/assessments/{assessment_id}/schedules\n{ak}\n{ts}').format(ak=self.public_key, assessment_id=str(assessment_id), ts=ts)
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/assessments/{assessment_id}/schedules?ak={ak}&ts={ts}&asgn={asgn}').format(ak=self.public_key, assessment_id=str(assessment_id), ts=ts, asgn=asgn)
        try:
            resp = requests.get(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    schedules = {schedule['accessKey']:schedule['name'] for schedule in resp_json['schedules']}
                    if self.attempts:
                        if self.attempts < len(schedules):
                            sorted_schedules = sorted(schedules.items(), key=lambda x: x[1])
                            return dict(sorted_schedules[:self.attempts])
                    return schedules
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''

    def get_student_result_in_schedule(self, schedule_key, user_email):
        """
        Returns all details of schedule
        """
        self.set_auth_keys()
        ts = str(time.time())
        string = ('GEThttp://api.mettl.com/v1/schedules/{schedule_key}/candidates/{user_email}\n{ak}\n{ts}').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, user_email=user_email)
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/schedules/{schedule_key}/candidates/{user_email}?ak={ak}&ts={ts}&asgn={asgn}').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, user_email=user_email, asgn=asgn)
        try:
            resp = requests.get(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    test_status = resp_json['candidate']['testStatus']
                    return test_status
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''

    def register_student_for_schedule(self, schedule_key, user):
        """
            registers the user for a specifid schedule
        """
        self.set_auth_keys()
        ts = str(time.time())
        if user.profile.year_of_birth:
            dob = str(user.profile.year_of_birth)
        else:
            dob = ''
        rd = {'registrationDetails': [
                                 {'First Name': user.profile.name, 
                                    'Email Address': user.email, 
                                    'Date of birth': dob}]}
        string = ('POSThttp://api.mettl.com/v1/schedules/{schedule_key}/candidates\n{ak}\ntrue\n{rd}\n{ts}').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, rd=json.dumps(rd))
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/schedules/{schedule_key}/candidates?ak={ak}&ts={ts}&asgn={asgn}&rd={rd}&allowMissingMandatoryRegistrationFields=true').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, rd=json.dumps(rd), asgn=asgn)
        try:
            resp = requests.post(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    return resp_json['registrationStatus']
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''

    def get_all_student_details_in_schedule(self, schedule_key, limit='100'):
        """
        Returns all details of schedule for assessment
        """
        self.set_auth_keys()
        ts = str(time.time())
        string = ('GEThttp://api.mettl.com/v1/schedules/{schedule_key}/candidates\n{ak}\n{limit}\n{ts}').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, limit=limit)
        asgn = create_signature(string, self.private_key)
        api_url = ('http://api.mettl.com/v1/schedules/{schedule_key}/candidates?ak={ak}&limit={limit}&ts={ts}&asgn={asgn}').format(ak=self.public_key, schedule_key=str(schedule_key), ts=ts, limit=limit, asgn=asgn)
        try:
            resp = requests.get(api_url)
        except:
            self.raise_error('404', 'Oops! Something went wrong, please try after sometime')

        if not self.has_any_error():
            if resp.status_code == 200:
                resp_json = resp.json()
                if resp_json['status'] == 'SUCCESS':
                    candidates = resp_json['candidates']
                    return candidates
                self.raise_error(resp_json['error']['code'], resp_json['error']['message'])
                return ''

    def create_schedules_for_assessment(self):
        """
        Creates schedules as per no. of attemtps entered
        """
        for attempt_no in range(int(self.attempts)):
            self.set_auth_keys()
            ts = str(time.time())
            sc = {'assessmentId': self.current_assessment_id, 
               'name': 'Attempt ' + str(attempt_no + 1), 
               'scheduleType': 'AlwaysOn', 
               'webProctoring': {'enabled': False}, 'access': {'type': 'OpenForAll', 'sendEmail': False}, 'ipAccessRestriction': {'enabled': False}, 'sourceApp': 'Mettl'}
            string = ('POSThttp://api.mettl.com/v1/assessments/{assessment_id}/schedules/\n{ak}\n{sc}\n{ts}').format(assessment_id=self.current_assessment_id, ak=self.public_key, sc=json.dumps(sc), ts=ts)
            asgn = create_signature(string, self.private_key)
            api_url = ('http://api.mettl.com/v1/assessments/{assessment_id}/schedules/?ak={ak}&asgn={asgn}&sc={sc}&ts={ts}').format(assessment_id=self.current_assessment_id, ak=self.public_key, asgn=asgn, sc=json.dumps(sc), ts=ts)
            try:
                resp = requests.post(api_url)
            except:
                self.raise_error('404', 'Oops! Something went wrong, please try after sometime')
            else:
                if not self.has_any_error():
                    if resp.status_code == 200:
                        resp_json = resp.json()
                        if resp_json['status'] != 'SUCCESS':
                            self.raise_error(resp_json['error']['code'], resp_json['error']['message'])

        return True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode('utf8')

    def student_view(self, context=None):
        """
        The primary view of the MettlXBlock, shown to students
        when viewing courses,
        And the author view of the MettlXBlock, shown to instructor 
        for previewing XBlock.
        """
        if getattr(self.xmodule_runtime, 'is_author_mode', False):
            temp = self.resource_string('static/html/mettl_author_view.html')
            html = Template(temp)
            all_students_data = OrderedDict()
            if self.current_assessment_id:
                assessment_detail = self.get_assessment_detail(self.current_assessment_id)
                schedules = self.get_all_schedules(self.current_assessment_id)
                if not self.has_any_error():
                    context['assessment_id'], context['assessment_name'] = assessment_detail['id'], assessment_detail['name']
                    for schedule, schedule_name in sorted(schedules.iteritems(), key=lambda (k, v): (v, k)):
                        all_students_data[schedule] = [
                         schedule_name]
                        students = self.get_all_student_details_in_schedule(schedule)
                        if not self.has_any_error():
                            for student in students:
                                if student['testStatus']['status'] == 'Completed':
                                    all_students_data[schedule].append({'first_name': student['registration']['First Name'], 
                                       'email': student['registration']['Email Address'], 
                                       'status': student['testStatus']['status'], 
                                       'marks_obtained': student['testStatus']['result']['totalMarks'], 
                                       'max_marks': student['testStatus']['result']['maxMarks'], 
                                       'end_time': student['testStatus']['endTime'], 
                                       'pdf_report': student['testStatus']['pdfReport']})
                                else:
                                    all_students_data[schedule].append({'first_name': student['registration']['First Name'], 
                                       'email': student['registration']['Email Address'], 
                                       'status': student['testStatus']['status'], 
                                       'marks_obtained': '-', 
                                       'max_marks': '-', 
                                       'end_time': '-', 
                                       'pdf_report': '-'})

                if not self.has_any_error():
                    context['student_data'] = all_students_data
                    context['schedules'] = schedules
                else:
                    context.update({'error_msg': self.error_msg, 
                       'error_code': self.error_code})
            context.update({'display_name': self.display_name, 
               'attempts': self.attempts, 
               'weight': self.weight})
            frag = Fragment(html.render(Context(context)))
            frag.add_css(self.resource_string('static/css/mettl.css'))
            frag.add_css(self.resource_string('static/css/paginate.css'))
            frag.add_javascript(self.resource_string('static/js/src/paginate.js'))
            frag.add_javascript(self.resource_string('static/js/src/mettl_author.js'))
            frag.initialize_js('MettlXBlock')
            return frag
        else:
            schedule_data = OrderedDict()
            self.test_link = {}
            self.student_score = 0
            instructions = ''
            if self.current_assessment_id:
                schedules = self.get_all_schedules(self.current_assessment_id)
                assessment_detail = self.get_assessment_detail(self.current_assessment_id)
                if not self.has_any_error():
                    attempt = 1
                    has_other_enabled = False
                    if assessment_detail['instructions']:
                        instructions = assessment_detail['instructions']
                    else:
                        instructions = assessment_detail['defaultInstructions']
                    user_id = self.runtime.user_id
                    user = User.objects.get(id=user_id)
                    for schedule, schedule_name in sorted(schedules.iteritems(), key=lambda (k, v): (v, k)):
                        register_resp = self.register_student_for_schedule(schedule, user)
                        test_status = self.get_student_result_in_schedule(schedule, user.email)
                        if not self.has_any_error():
                            status = test_status['status']
                            if status == 'Completed':
                                schedule_data[schedule] = {'attempt_no': attempt, 'status': 'Attempted', 
                                   'start_test': '', 
                                   'resume_test': '', 
                                   'marks': int(test_status['result']['totalMarks']), 
                                   'max_marks': int(test_status['result']['maxMarks']), 
                                   'time_taken': time.strftime('%H:%M:%S', time.gmtime(int(test_status['result']['attemptTime']))), 
                                   'finish_time': test_status['endTime'], 
                                   'pdf_report': test_status['pdfReport'], 
                                   'last_response_time': '', 
                                   'finish_mode': test_status['completionMode'], 
                                   'can_start_test': False, 
                                   'schedule_name': schedules[schedule]}
                                percent = test_status['result']['totalMarks'] * 100 / test_status['result']['maxMarks']
                                if percent > self.student_score:
                                    self.student_score = percent
                            elif status == 'Archive':
                                schedule_data[schedule] = {'attempt_no': attempt, 'status': status, 
                                   'start_test': '', 
                                   'resume_test': '', 
                                   'marks': 0, 
                                   'max_marks': '', 
                                   'time_taken': '--', 
                                   'finish_time': '--', 
                                   'pdf_report': '', 
                                   'last_response_time': '', 
                                   'finish_mode': '', 
                                   'can_start_test': False, 
                                   'schedule_name': schedules[schedule]}
                            else:
                                self.test_link[schedule] = register_resp[0]['url']
                                if status == 'InProgress':
                                    schedule_data[schedule] = {'attempt_no': attempt, 'status': status, 
                                       'start_test': '', 
                                       'resume_test': self.test_link[schedule], 
                                       'marks': 0, 
                                       'max_marks': '', 
                                       'time_taken': '--', 
                                       'finish_time': '--', 
                                       'pdf_report': '', 
                                       'last_response_time': test_status['lastResponseTime'], 
                                       'finish_mode': '', 
                                       'schedule_name': schedules[schedule]}
                                else:
                                    schedule_data[schedule] = {'attempt_no': attempt, 'status': status, 
                                       'start_test': self.test_link[schedule], 
                                       'resume_test': '', 
                                       'marks': 0, 
                                       'max_marks': '', 
                                       'time_taken': '--', 
                                       'finish_time': '--', 
                                       'pdf_report': '', 
                                       'last_response_time': '', 
                                       'finish_mode': '', 
                                       'schedule_name': schedules[schedule]}
                                if has_other_enabled:
                                    schedule_data[schedule]['can_start_test'] = False
                                else:
                                    schedule_data[schedule]['can_start_test'] = True
                                    has_other_enabled = True
                            attempt += 1

            context.update({'attempts': self.attempts, 
               'test_button_label': self.test_button_label, 
               'test_button_color': self.test_button_color, 
               'test_button_back_color': self.test_button_back_color, 
               'schedule_data': schedule_data, 
               'instructions': instructions})
            if self.has_any_error():
                context['error_msg'] = 'Oops! Something went wrong, please try after sometime.'
            grade_event = {'value': self.student_score * self.weight / 100, 'max_value': self.weight}
            self.runtime.publish(self, 'grade', grade_event)
            temp = self.resource_string('static/html/mettl.html')
            html = Template(temp)
            frag = Fragment(html.render(Context(context)))
            frag.add_css(self.resource_string('static/css/mettl.css'))
            frag.add_javascript(self.resource_string('static/js/src/mettl.js'))
            frag.initialize_js('MettlXBlock')
            return frag

    def studio_view(self, context=None):
        """
        The studio view of the MettlXBlock. shown to instructor
        by clicking on edit XBLock.
        """
        cls = type(self)

        def none_to_empty(data):
            """
                Return empty string if data is None else return data.
                """
            if data is not None:
                return data
            else:
                return ''

        edit_fields = ((field, none_to_empty(getattr(self, field.name)), input_type) for field, input_type in (
         (
          cls.display_name, 'text'),
         (
          cls.attempts, 'number'),
         (
          cls.weight, 'number'),
         (
          cls.test_button_label, 'text'),
         (
          cls.test_button_back_color, 'color'),
         (
          cls.test_button_color, 'color')))
        if self.current_assessment_id:
            assessment_detail = self.get_assessment_detail(self.current_assessment_id)
            if not self.has_any_error():
                context['current_assessment_id'], context['current_assessment_name'] = assessment_detail['id'], assessment_detail['name']
        assessments = self.get_all_assessments('100')
        context['fields'] = edit_fields
        if not self.has_any_error():
            context['assessments'] = assessments
        else:
            context['error_msg'] = self.error_msg
        temp = self.resource_string('static/html/mettl_studio_edit.html')
        html = Template(temp)
        frag = Fragment(html.render(Context(context)))
        frag.add_css(self.resource_string('static/css/mettl.css'))
        frag.add_javascript(self.resource_string('static/js/src/mettl_studio.js'))
        frag.initialize_js('MettlXBlock')
        return frag

    @XBlock.json_handler
    def save_studio_edits(self, data, suffix=''):
        """
        Handles submit action of studio edit.
        """
        self.current_assessment_id = data.get('assessment_id')
        self.display_name = data.get('display_name')
        self.weight = data.get('weight')
        self.test_button_label = data.get('test_button_label')
        self.test_button_color = data.get('test_button_color')
        self.test_button_back_color = data.get('test_button_back_color')
        if self.current_assessment_id:
            self.attempts = data.get('attempts')
            self.create_schedules_for_assessment()
        return {'Status': 'Success'}

    @XBlock.json_handler
    def fetch_result(self, data, suffix=''):
        schedules = self.get_all_schedules(self.current_assessment_id)
        schedule_data = OrderedDict()
        if not self.has_any_error():
            has_other_enabled = False
            user_id = self.runtime.user_id
            user = User.objects.get(id=user_id)
            for schedule, schedule_name in sorted(schedules.iteritems(), key=lambda (k, v): (v, k)):
                test_status = self.get_student_result_in_schedule(schedule, user.email)
                if not self.has_any_error():
                    status = test_status['status']
                    if status == 'Completed':
                        schedule_data[schedule] = {'status': 'Attempted', 'start_test': '', 
                           'resume_test': '', 
                           'marks': int(test_status['result']['totalMarks']), 
                           'max_marks': int(test_status['result']['maxMarks']), 
                           'time_taken': time.strftime('%H:%M:%S', time.gmtime(int(test_status['result']['attemptTime']))), 
                           'finish_time': test_status['endTime'], 
                           'pdf_report': test_status['pdfReport'], 
                           'last_response_time': '', 
                           'finish_mode': test_status['completionMode'], 
                           'can_start_test': False}
                        percent = test_status['result']['totalMarks'] * 100 / test_status['result']['maxMarks']
                        if percent > self.student_score:
                            self.student_score = percent
                    elif status == 'Archive':
                        schedule_data[schedule] = {'status': status, 'start_test': '', 
                           'resume_test': '', 
                           'marks': 0, 
                           'max_marks': '', 
                           'time_taken': '--', 
                           'finish_time': '--', 
                           'pdf_report': '', 
                           'last_response_time': '', 
                           'finish_mode': '', 
                           'can_start_test': False}
                    else:
                        if status == 'InProgress':
                            schedule_data[schedule] = {'status': status, 'start_test': '', 
                               'resume_test': self.test_link[schedule], 
                               'marks': 0, 
                               'max_marks': '', 
                               'time_taken': '--', 
                               'finish_time': '--', 
                               'pdf_report': '', 
                               'last_response_time': test_status['lastResponseTime'], 
                               'finish_mode': ''}
                        else:
                            schedule_data[schedule] = {'status': status, 'start_test': self.test_link[schedule], 
                               'resume_test': '', 
                               'marks': 0, 
                               'max_marks': '', 
                               'time_taken': '--', 
                               'finish_time': '--', 
                               'pdf_report': '', 
                               'last_response_time': '', 
                               'finish_mode': ''}
                        if has_other_enabled:
                            schedule_data[schedule]['can_start_test'] = False
                        else:
                            schedule_data[schedule]['can_start_test'] = True
                            has_other_enabled = True

        grade_event = {'value': self.student_score * self.weight / 100, 'max_value': self.weight}
        self.runtime.publish(self, 'grade', grade_event)
        return schedule_data

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
         ('MettlXBlock', '<mettl/>\n             '),
         ('Multiple MettlXBlock', '<vertical_demo>\n                <mettl/>\n                <mettl/>\n                <mettl/>\n                </vertical_demo>\n             ')]