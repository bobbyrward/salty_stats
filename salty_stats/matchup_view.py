import logging

from PySide import QtCore  # noqa
from PySide import QtGui  # noqa

from salty_stats.character_view import CharacterView
from salty_stats.character_selector import CharacterSelector
from salty_stats.prediction_view import PredictionView


class MatchupView(QtGui.QWidget):
    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(MatchupView, self).__init__(parent)

        self.player_1_selector = CharacterSelector(self, QtGui.QApplication.instance().player_1_changed)
        self.player_1_view = CharacterView(self, QtGui.QApplication.instance().player_1_changed)

        self.player_2_selector = CharacterSelector(self, QtGui.QApplication.instance().player_2_changed)
        self.player_2_view = CharacterView(self, QtGui.QApplication.instance().player_2_changed)

        self.prediction_view = PredictionView(self)

        p1_layout = QtGui.QVBoxLayout()
        p1_layout.addWidget(self.player_1_selector)
        p1_layout.addWidget(self.player_1_view)
        p1_layout.setContentsMargins(0, 0, 0, 0)

        p2_layout = QtGui.QVBoxLayout()
        p2_layout.addWidget(self.player_2_selector)
        p2_layout.addWidget(self.player_2_view)
        p2_layout.setContentsMargins(0, 0, 0, 0)

        both_players = QtGui.QHBoxLayout()
        both_players.addLayout(p1_layout)
        both_players.addLayout(p2_layout)
        both_players.setContentsMargins(0, 0, 0, 0)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(both_players)
        layout.addWidget(self.prediction_view)

        self.setLayout(layout)
