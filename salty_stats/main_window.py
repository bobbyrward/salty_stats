import logging

from PySide import QtCore
from PySide import QtGui

from salty_stats.matchup_view import MatchupView
from salty_stats.crawler_dialog import CrawlerWizard


class MainWindow(QtGui.QMainWindow):
    """Top-Level window for the app
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.actions = {}

        self.create_actions()
        self.create_menus()
        self.init_ui()

        app = QtGui.QApplication.instance()

        self.restoreGeometry(app.settings.value('geometry'))
        self.restoreState(app.settings.value('windowState'))

        self.log.debug('MainWindow.__init__ finished')

    def init_ui(self):
        self.log.debug('init_ui')

        self.matchup = MatchupView(self)
        self.setCentralWidget(self.matchup)

        self.setWindowTitle('Salty Bet Stats')
        self.resize(QtCore.QSize(800, 600))
        self.show()
        self.raise_()

    def closeEvent(self, event):
        self.log.debug('close_event')

        app = QtGui.QApplication.instance()

        app.settings.setValue("geometry", self.saveGeometry())
        app.settings.setValue("windowState", self.saveState())

        super(MainWindow, self).closeEvent(event)

    def create_actions(self):
        self.actions = {}
        self.actions['quit'] = QtGui.QAction(
            'E&xit',
            self,
            shortcut=QtGui.QKeySequence.Quit,
            statusTip='Exit the application',
            triggered=self.close,
        )

        self.actions['crawl'] = QtGui.QAction(
            '&Crawl stats',
            self,
            statusTip='Crawl a tourney stats page',
            triggered=self.on_crawl,
        )

    def create_menus(self):
        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(self.actions['crawl'])
        file_menu.addSeparator()
        file_menu.addAction(self.actions['quit'])

    def on_crawl(self):
        crawler = CrawlerWizard()
        crawler.exec_()
