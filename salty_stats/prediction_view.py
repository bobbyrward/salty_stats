from PySide import QtGui


class PredictionBetView(QtGui.QWidget):
    def __init__(self, parent):
        super(PredictionBetView, self).__init__(parent)
        self.bet_on = QtGui.QLabel('')
        self.bet_rating = QtGui.QLabel('')
        self.confidence = QtGui.QLabel('')

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.create_group_box('Bet On', self.bet_on))
        layout.addWidget(self.create_group_box('Bet Rating', self.bet_rating))
        layout.addWidget(self.create_group_box('Confidence', self.confidence))
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        app = QtGui.QApplication.instance()
        app.prediction_changed.connect(self.on_prediction_changed)

    def create_group_box(self, name, widget):
        layout = QtGui.QVBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QtGui.QGroupBox(name, self)
        group.setLayout(layout)

        return group

    def on_prediction_changed(self, prediction, player1, player2):
        self.bet_on.setText(prediction.bet)
        self.bet_rating.setText('{} vs {}'.format(prediction.bet_rating[player1], prediction.bet_rating[player2]))
        self.confidence.setText(str(prediction.confidence))


class PredictionMessageView(QtGui.QGroupBox):
    def __init__(self, parent, name, label):
        super(PredictionMessageView, self).__init__(label, parent)
        self.name = name
        self.messages = QtGui.QLabel()
        self.messages.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.messages)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        app = QtGui.QApplication.instance()
        app.prediction_changed.connect(self.on_prediction_changed)

    def on_prediction_changed(self, prediction, player1, player2):
        name_translate = {
            'favorp1': player1,
            'favorp2': player2,
            'warnings': 'warnings',
        }

        messages_text = '\n'.join(prediction.messages[name_translate[self.name]])
        self.messages.setText(messages_text)
