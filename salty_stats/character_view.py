from PySide import QtGui


class CharacterStatsView(QtGui.QWidget):
    def __init__(self, parent, signal):
        super(CharacterStatsView, self).__init__(parent)
        self.init_ui()
        signal.connect(self.on_character_changed)

    def init_ui(self):
        self.wins = QtGui.QLabel()
        self.losses = QtGui.QLabel()
        self.rating = QtGui.QLabel()
        self.ratio = QtGui.QLabel()
        self.total_matches = QtGui.QLabel()

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.create_group_box('Rating', self.rating))
        layout.addWidget(self.create_group_box('Ratio', self.ratio))
        layout.addWidget(self.create_group_box('Wins', self.wins))
        layout.addWidget(self.create_group_box('Losses', self.losses))
        layout.addWidget(self.create_group_box('Matches', self.total_matches))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

    def create_group_box(self, name, label):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QtGui.QGroupBox(name, self)
        group.setLayout(layout)

        return group

    def on_character_changed(self, character):
        self.wins.setText(str(character.win_count))
        self.losses.setText(str(character.loss_count))
        self.rating.setText(str(character.rating))
        self.total_matches.setText(str(character.total_matches))

        try:
            self.ratio.setText(str(round(character.win_loss_ratio, 2)))
        except TypeError:
            self.ratio.setText(character.win_loss_ratio)
