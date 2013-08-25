import logging

from PySide import QtCore
from PySide import QtGui


"""
Intro Page
    Description of what's about to happen

Params Page
    Enter params such as URL to parse
    or
    Retrieve list of tourneys and let them select one

Parse Page
    Download the tournet page and parse it

Finish Page
    Summary of changes

"""


class DownloadTourneyWizardPage(QtGui.QWizardPage):
    download_complete = QtCore.Signal(object, object)
    crawl_complete = QtCore.Signal()
    log = logging.getLogger(__name__)

    def __init__(self, parent=None):
        super(DownloadTourneyWizardPage, self).__init__(parent)
        self.download_complete.connect(self.on_download_complete)
        self.crawl_complete.connect(self.on_crawl_complete)
        self.setCommitPage(False)
        self.is_complete = False
        self.is_validated = False

    def initializePage(self):
        self.log.debug('DownloadTourneyWizardPage: initializePage')

        QtGui.QApplication.instance().request_processor.push_request(
            {'method': 'GET', 'url': self.field("url")},
            self.download_complete,
            None,
        )

    def on_crawl_complete(self):
        self.is_validated = True
        self.is_complete = True
        self.completeChanged.emit()
        self.parent.next()

    def on_download_complete(self, response, context):
        self.log.debug('DownloadTourneyWizardPage: on_download_complete')
        try:
            if response is None:
                raise ValueError("request error")
            response.raise_for_status()
        except Exception:
            self.is_validated = False
            # show the error
        else:
            QtGui.QApplication.instance().stats_crawler.push_request(response, self.crawl_complete)

    def validatePage(self):
        return self.is_validated

    def isComplete(self):
        return self.is_complete


class CrawlerWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        super(CrawlerWizard, self).__init__(parent)

        self.setWindowTitle('Stats Parsing Wizard')
        self.create_intro_page()
        self.create_params_page()
        self.create_parse_page()
        self.create_finish_page()

    def create_intro_page(self):
        pass

    def create_params_page(self):
        self.params_page = QtGui.QWizardPage(self)
        self.params_page.setTitle('Select tourney page to crawl')
        self.params_page.setSubTitle("Enter the URL of a tournet stats page to crawl")

        self.address_label = QtGui.QLabel("URL")
        self.address_edit = QtGui.QLineEdit()
        self.params_page.registerField("url*", self.address_edit)

        layout = QtGui.QGridLayout()
        layout.addWidget(self.address_label, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addWidget(self.address_edit, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.params_page.setLayout(layout)
        self.addPage(self.params_page)

    def create_parse_page(self):
        self.parse_page = DownloadTourneyWizardPage(self)
        self.parse_page.setTitle('Downloading stats')
        self.parse_page.setSubTitle('Please wait while the stats are downloaded and parsed')
        self.addPage(self.parse_page)

    def create_finish_page(self):
        self.finish_page = QtGui.QWizardPage(self)
        self.finish_page.setTitle('Download complete')
        self.finish_page.setSubTitle('The following changes were made')
        self.addPage(self.finish_page)
