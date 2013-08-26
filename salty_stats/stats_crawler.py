import logging

from PySide import QtCore
from PySide import QtGui
from lxml import html

from salty_stats.parsing.parser import load_tourney_stats


DEFAULT_REQUEST_WAIT_INTERVAL = 1.5


class StatsCrawler(QtCore.QThread):
    log = logging.getLogger(__name__)
    process_url = QtCore.Signal(object, object)
    download_done = QtCore.Signal(object, object)

    def __init__(self, parent, request_wait_interval=DEFAULT_REQUEST_WAIT_INTERVAL):
        super(StatsCrawler, self).__init__(parent)
        self.request_wait_interval = request_wait_interval

    def push_request(self, response, signal=None):
        self.log.debug('push_request (url {}) [thread {}]'.format(response, self.thread()))
        self.download_done.emit(response, signal)

    def quit(self):
        self.log.debug('StatsCrawler.quit: [thread {}]'.format(self.thread()))
        super(StatsCrawler, self).quit()

    def run(self):
        self.process_url.connect(self.on_process_url)
        self.download_done.connect(self.on_download_complete)
        self.exec_()

    def on_process_url(self, url, signal):
        self.log.debug('on_process_url [thread {}]'.format(self.thread()))
        self._process_url(url, signal)

    def _process_url(self, url, signal):
        self.log.debug('_process_url (url {}) [thread {}]'.format(url, self.thread()))

        rp = QtGui.QApplication.instance().request_processor
        rp.push_request({'method': 'GET', 'url': url}, self.download_done, signal)

    def _emit_crawl_done(self, signal):
        self.log.debug('crawl done (signal {}) [thread {}]'.format(signal, self.thread()))

        if signal:
            signal.emit()

    def on_download_complete(self, response, signal):
        self.log.debug('on_download_complete [thread {}]'.format(self.thread()))

        session = QtGui.QApplication.instance().Session()
        parsed_html = html.fromstring(response.content)
        try:
            found_existing = load_tourney_stats(session, parsed_html)
        except ValueError as e:
            #with open('dump.html', 'w') as fd:
            #    fd.write(response.content)
            self.log.debug('ValueError while loading tourney stats: {}'.format(e))
            return

        if found_existing:
            self._emit_crawl_done(signal)

        found_next_url = parsed_html.xpath('//div[@id="pagination"]/div[@class="right"]/a/@href')

        if len(found_next_url):
            self._process_url(''.join(('http://www.saltybet.com', found_next_url[0])), signal)
        else:
            self._emit_crawl_done(signal)
