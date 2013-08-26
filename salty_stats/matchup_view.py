import logging

from PySide import QtCore
from PySide import QtGui

from salty_stats.character_view import CharacterStatsView
from salty_stats.character_selector import CharacterSelector
from salty_stats.prediction_view import PredictionBetView
from salty_stats.prediction_view import PredictionMessageView
from salty_stats.balance import BalanceView
from salty_stats.betting import BettingDialog


class MatchupView(QtGui.QWidget):
    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(MatchupView, self).__init__(parent)
        app = QtGui.QApplication.instance()
        p1_changed = app.player_1_changed
        p2_changed = app.player_2_changed

        app.status_changed.connect(self.on_status_changed)

        p1_selector = CharacterSelector(self, p1_changed)
        p1_selector.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

        p1_stats = CharacterStatsView(self, p1_changed)
        #p1_history = MatchHistoryTableView(self, p1_changed)

        p2_selector = CharacterSelector(self, p2_changed)
        p2_selector.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        p2_stats = CharacterStatsView(self, p2_changed)
        #p2_history = MatchHistoryTableView(self, p2_changed)

        bet_prediction = PredictionBetView(self)
        warnings = PredictionMessageView(self, 'warnings', 'Warnings')
        favor_p1 = PredictionMessageView(self, 'favorp1', 'Favor P1')
        favor_p2 = PredictionMessageView(self, 'favorp2', 'Favor P2')

        balance = BalanceView(self)
        self.bet_button = QtGui.QPushButton('Place a bet')
        self.bet_button.clicked.connect(self.on_bet)
        self.bet_button.setEnabled(False)

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 1)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)
        layout.setRowStretch(4, 0)

        align = 0

        row = 0
        layout.addWidget(balance, row, 0, 1, 2, QtCore.Qt.AlignCenter)
        layout.addWidget(self.bet_button, row, 2, 1, 2, QtCore.Qt.AlignCenter)
        row += 1

        layout.addWidget(p1_selector, row, 0, 1, 2, align)
        layout.addWidget(p2_selector, row, 2, 1, 2, align)
        row += 1

        layout.addWidget(p1_stats, row, 0, 1, 2, align)
        layout.addWidget(p2_stats, row, 2, 1, 2, align)
        row += 1

        layout.addWidget(bet_prediction, row, 0, 1, 2, align)
        layout.addWidget(warnings, row, 2, 1, 2, align)
        row += 1

        layout.addWidget(favor_p1, row, 0, 1, 2, align)
        layout.addWidget(favor_p2, row, 2, 1, 2, align)
        row += 1

        self.setLayout(layout)

    def on_bet(self):
        dlg = BettingDialog(self)
        result = dlg.exec_()

        if result == QtGui.QDialog.Accepted:
            self.bet_button.setEnabled(False)

    def on_status_changed(self, new_status):
        #TODO: This isn't quite right.  Not getting an 'open' status though. Maybe only from state.json?
        if str(new_status) != 'locked':
            self.bet_button.setEnabled(True)
        else:
            self.bet_button.setEnabled(False)
