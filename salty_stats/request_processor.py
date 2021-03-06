import logging

import requests
from lxml import html
from PySide import QtCore
from PySide import QtGui


class RequestProcessor(QtCore.QThread):
    log = logging.getLogger(__name__)
    auth_check = QtCore.Signal(object, object)
    request_pushed = QtCore.Signal(object, object, object)
    check_signin = QtCore.Signal(object, object)

    request_processor_started = QtCore.Signal(object)
    authentication_succeeded = QtCore.Signal(object)

    def __init__(self, parent, cookies):
        super(RequestProcessor, self).__init__(parent)
        self.quit_flag = False
        self.cookies = cookies
        self.request_session = None
        self.userid = None
        self.balance = None

    def do_login_check(self):
        self.push_request({
            'method': 'GET',
            'url': 'http://www.saltybet.com',
        }, self.auth_check)

    def push_request(self, request_kwargs, signal=None, context=None):
        self.log.debug('RequestProcessor: push_request {} [thread {}]'.format(request_kwargs['url'], self.thread()))

        self.request_pushed.emit(request_kwargs, signal, context)

    def do_signin_request(self):
        app = QtGui.QApplication.instance()

        self.log.debug('Signing in w/ ("{}":"{}")'.format(
            str(app.settings.value('auth_user')),
            str(app.settings.value('auth_password')),
        ))

        self.push_request({
            'method': 'POST',
            'url': 'http://www.saltybet.com/authenticate?signin=1',
            'data': {
                'email': str(app.settings.value('auth_user')),
                'pword': str(app.settings.value('auth_password')),
                'authenticate': 'signin',
            },
        }, self.check_signin)

    def on_check_signin(self, response, context):
        self.log.debug('on_check_signin')
        parsed = html.fromstring(response.content)

        userid = parsed.xpath('//input[@id="u"]')

        if not len(userid):
            self.log.debug('Sign in failed')
            return

        userid = userid[0].get('value')

        if not userid:
            self.log.debug('on_auth_check: userid blank, logging in')
            return

        self.userid = userid

        balance = parsed.xpath('//input[@id="b"]')
        self.balance = balance[0].get('value')

        # logged in already
        self.log.debug('Sign in succeeded, userid = {}'.format(self.userid))
        self.authentication_succeeded.emit(self)

    def on_auth_check(self, response, context):
        self.log.debug('on_auth_check')
        parsed = html.fromstring(response.content)

        userid = parsed.xpath('//input[@id="u"]')

        if not len(userid):
            self.log.debug('on_auth_check: not logged in, logging in')
            self.do_signin_request()
            return

        userid = userid[0].get('value')

        if not userid:
            self.log.debug('on_auth_check: userid blank, logging in')
            self.do_signin_request()
            return

        self.userid = userid

        balance = parsed.xpath('//input[@id="b"]')
        self.balance = balance[0].get('value')

        # logged in already
        self.log.debug('on_auth_check: already logged in, userid = {}'.format(self.userid))
        self.authentication_succeeded.emit(self)

    def run(self):
        self.request_session = requests.session()
        self.request_session.headers.update({
            'Origin': 'http://www.saltybet.com',
            'Referer': 'http://www.saltybet.com/authenticate?signin=1',
            'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
        })

        self.auth_check.connect(self.on_auth_check)
        self.request_pushed.connect(self.on_request_pushed)
        self.check_signin.connect(self.on_check_signin)

        self.log.debug('RequestProcessor: evet loop started [thread {}]'.format(self.thread()))
        self.request_processor_started.emit(self)
        self.exec_()

    def on_request_pushed(self, request_kwargs, signal, context):
        try:
            response = self.request_session.request(cookies=self.cookies, **request_kwargs)
        except Exception:
            response = None
        else:
            self.cookies = response.cookies

        self.log.debug('RequestProcessor: response {}'.format(response))

        if signal:
            signal.emit(response, context)
