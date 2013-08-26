from PySide import QtGui

from salty_stats.match_history import MatchHistoryTableView
from salty_stats.match_history_model import MatchHistoryTabelModel


#TODO: Break some of these controls out into separate classes


class CharacterView(QtGui.QWidget):
    """Encapsulates all the views of a single character
    """

    def __init__(self, parent, signal):
        super(CharacterView, self).__init__(parent)
        self.init_ui()
        signal.connect(self.on_character_changed)

    def init_ui(self):
        self.name = QtGui.QLabel("Name", self)
        self.wins = QtGui.QLabel("Wins", self)
        self.losses = QtGui.QLabel("Losses", self)
        self.rating = QtGui.QLabel("Rating", self)
        self.ratio = QtGui.QLabel("Ratio", self)
        self.history = MatchHistoryTableView(self, MatchHistoryTabelModel(self, None))

        wins_layout = QtGui.QVBoxLayout()
        wins_layout.addWidget(self.wins)
        wins_layout.setContentsMargins(0, 0, 0, 0)

        wins_group = QtGui.QGroupBox("Wins", self)
        wins_group.setLayout(wins_layout)

        losses_layout = QtGui.QVBoxLayout()
        losses_layout.addWidget(self.losses)
        losses_layout.setContentsMargins(0, 0, 0, 0)

        losses_group = QtGui.QGroupBox("Losses", self)
        losses_group.setLayout(losses_layout)

        rating_layout = QtGui.QVBoxLayout()
        rating_layout.addWidget(self.rating)
        rating_layout.setContentsMargins(0, 0, 0, 0)

        rating_group = QtGui.QGroupBox("Rating", self)
        rating_group.setLayout(rating_layout)

        ratio_layout = QtGui.QVBoxLayout()
        ratio_layout.addWidget(self.ratio)
        ratio_layout.setContentsMargins(0, 0, 0, 0)

        ratio_group = QtGui.QGroupBox("Ratio", self)
        ratio_group.setLayout(ratio_layout)

        upper_layout = QtGui.QHBoxLayout()
        upper_layout.addWidget(rating_group)
        upper_layout.addWidget(wins_group)
        upper_layout.addWidget(losses_group)
        upper_layout.addWidget(ratio_group)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(5)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.name)
        main_layout.addLayout(upper_layout)
        main_layout.addWidget(self.history)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        self.setLayout(main_layout)

    def on_character_changed(self, character):
        history_model = MatchHistoryTabelModel(self, character)
        self.name.setText(character.name)
        self.history.setModel(history_model)
        self.wins.setText(str(character.win_count))
        self.losses.setText(str(character.loss_count))
        self.rating.setText(str(character.rating))

        try:
            self.ratio.setText(str(round(character.win_loss_ratio, 2)))
        except TypeError:
            self.ratio.setText(character.win_loss_ratio)
