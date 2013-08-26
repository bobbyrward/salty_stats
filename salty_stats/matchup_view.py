import logging

from PySide import QtGui

from salty_stats.character_view import CharacterStatsView
from salty_stats.match_history import MatchHistoryTableView
from salty_stats.character_selector import CharacterSelector
from salty_stats.prediction_view import PredictionBetView
from salty_stats.prediction_view import PredictionMessageView


class MatchupView(QtGui.QWidget):
    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(MatchupView, self).__init__(parent)
        p1_changed = QtGui.QApplication.instance().player_1_changed
        p2_changed = QtGui.QApplication.instance().player_2_changed

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

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 1)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)

        align = 0

        layout.addWidget(p1_selector, 0, 0, 1, 2, align)
        layout.addWidget(p1_stats, 1, 0, 1, 2, align)
        #layout.addWidget(p1_history, 2, 0, 1, 2, align)

        layout.addWidget(p2_selector, 0, 2, 1, 2, align)
        layout.addWidget(p2_stats, 1, 2, 1, 2, align)
        #layout.addWidget(p2_history, 2, 2, 1, 2, align)

        layout.addWidget(bet_prediction, 2, 0, 1, 2, align)
        layout.addWidget(warnings, 2, 2, 1, 2, align)

        layout.addWidget(favor_p1, 3, 0, 1, 2, align)
        layout.addWidget(favor_p2, 3, 2, 1, 2, align)

        self.setLayout(layout)
