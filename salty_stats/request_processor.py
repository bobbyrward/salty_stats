import logging
import urllib

from lxml import html
from PySide import QtCore
from PySide import QtGui
from PySide import QtNetwork


class RequestProcessor(QtCore.QObject):
    log = logging.getLogger(__name__)
    auth_check = QtCore.Signal(object, object)
    request_pushed = QtCore.Signal(object, object, object)
    check_signin = QtCore.Signal(object, object)

    request_processor_started = QtCore.Signal(object)
    authentication_succeeded = QtCore.Signal(object)

    headers = {
        'Origin': 'http://www.saltybet.com',
        'Referer': 'http://www.saltybet.com/authenticate?signin=1',
        'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
    }

    def __init__(self, parent, cookies):
        super(RequestProcessor, self).__init__(parent)
        self.quit_flag = False
        self.cookies = cookies
        self.request_session = None
        self.userid = None
        self.balance = None
        self.manager = None
        self.manager = QtNetwork.QNetworkAccessManager()

    def start(self):
        pass

    def quit(self):
        pass

    def do_login_check(self):
        self.push_request({
            'method': 'GET',
            'url': 'http://www.saltybet.com',
        }, self._auth_check)

    def push_request(self, request_kwargs, callback=None, context=None):
        self.log.debug('RequestProcessor: push_request {} [thread {}]'.format(request_kwargs['url'], self.thread()))

        self.on_request_pushed(request_kwargs, callback, context)

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
        }, self._check_signin)

    def _check_signin(self, response, context):
        self.log.debug('_check_signin')
        parsed = html.fromstring(str(response.readAll()))

        userid = parsed.xpath('//input[@id="u"]')

        if not len(userid):
            self.log.debug('Sign in failed')
            with open('dump.html', 'wb') as fd:
                fd.write(html.tostring(parsed, pretty_print=True))

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

    def _auth_check(self, response, context):
        self.log.debug('_auth_check')
        parsed = html.fromstring(str(response.readAll()))

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
        self.auth_check.connect(self.on_auth_check)
        self.request_pushed.connect(self.on_request_pushed)
        self.check_signin.connect(self.on_check_signin)

        self.log.debug('RequestProcessor: evet loop started [thread {}]'.format(self.thread()))
        self.request_processor_started.emit(self)

        self.exec_()

    def on_request_pushed(self, request_kwargs, callback, context):
        data = None

        request = QtNetwork.QNetworkRequest()

        for header, value in self.headers.iteritems():
            request.setRawHeader(header, value)

        url = QtCore.QUrl(request_kwargs['url'])

        if 'params' in request_kwargs:
            for key, value in request_kwargs['params'].iteritems():
                url.addQueryItem(key, value)

        request.setUrl(url)

        self.log.debug('RequestProcessor: sending request for {}'.format(url.toString()))

        method = {
            'GET': QtNetwork.QNetworkAccessManager.GetOperation,
            'POST': QtNetwork.QNetworkAccessManager.PostOperation,
        }[request_kwargs['method']]

        if 'data' in request_kwargs:
            data = QtCore.QBuffer(self)
            data.open(QtCore.QBuffer.ReadWrite)

            encoded = urllib.urlencode(request_kwargs['data'])
            data.write(encoded)

            request.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader, 'application/x-www-form-urlencoded')
            request.setHeader(QtNetwork.QNetworkRequest.ContentLengthHeader, len(encoded))
            request.setRawHeader('Referer', 'http://www.saltybet.com/authenticate?signin=1')

        response = self.manager.createRequest(method, request, data)

        def on_error(error_num):
            self.log.debug('RequestProcessor: response error {}'.format(error_num))

            if callable(callback):
                callback(response, context)

        def on_finished():
            self.log.debug('RequestProcessor: response {} - {}'.format(response.url().toString(), response.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute)))

            if callable(callback):
                callback(response, context)

            self.log.debug('RequestProcessor: emitted success signal')

        response.finished.connect(on_finished)
        response.error.connect(on_error)
