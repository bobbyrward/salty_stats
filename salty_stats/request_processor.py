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

    def do_login_check(self):
        self.push_request({
            'method': 'GET',
            'url': 'http://www.saltybet.com/stats',
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
        parsed = html.fromstring(response.content)

        footer = parsed.xpath('//div[@id="footer"]')

        if not len(footer):
            self.log.debug('Sign in failed')
            return

        footer = footer[0]

        class_ = footer.get('class')

        if not class_ or 'goldfooter' not in class_:
            self.log.debug('Sign in failed')
            return

        # logged in already
        self.log.debug('Sign in succeeded')
        self.authentication_succeeded.emit(self)

    def on_auth_check(self, response, context):
        parsed = html.fromstring(response.content)

        footer = parsed.xpath('//div[@id="footer"]')

        if not len(footer):
            self.do_signin_request()
            return

        footer = footer[0]

        class_ = footer.get('class')

        if not class_ or 'goldfooter' not in class_:
            self.do_signin_request()
            return

        # logged in already
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
        self.log.debug('RequestProcessor: got work item {} [thread {}]'.format(request_kwargs['url'], self.thread()))

        try:
            self.log.debug('RequestProcessor: sending request w/ cookies {} [thread {}]'.format(self.cookies, self.thread()))
            response = self.request_session.request(cookies=self.cookies, **request_kwargs)
        except Exception:
            response = None
        else:
            self.cookies = response.cookies

        self.log.debug('RequestProcessor: response {}'.format(response))

        if signal:
            signal.emit(response, context)
