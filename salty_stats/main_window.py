import logging

from PySide import QtCore
from PySide import QtGui

from salty_stats.matchup_view import MatchupView


class MainWindow(QtGui.QMainWindow):
    """Top-Level window for the app
    """

    log = logging.getLogger(__name__)

    def __init__(self):
        super(MainWindow, self).__init__()
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
