import logging

from PySide import QtCore
from PySide import QtGui

from salty_stats.predictor import predict_winner


class PredictionView(QtGui.QTextEdit):
    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(PredictionView, self).__init__(parent)
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.player1 = None
        self.player2 = None

        QtGui.QApplication.instance().player_1_changed.connect(self.on_player1_changed)
        QtGui.QApplication.instance().player_2_changed.connect(self.on_player2_changed)

        self.refresh_data()

    def refresh_data(self):
        if self.player1 is None or self.player2 is None:
            self.setPlainText('')
            return

        messages, p1rating, p2rating = predict_winner(
            QtGui.QApplication.instance().session,
            self.player1,
            self.player2,
        )

        lines = []

        estimate = None

        if abs(p1rating - p2rating) > 1:
            if p1rating > p2rating:
                estimate = self.player1
            elif p2rating > p1rating:
                estimate = self.player2

        if estimate is not None:
            lines.append("Estimate: Bet {}".format('????' if estimate is None else estimate.name))
        else:
            lines.append("Estimate: Try betting upset")

        if messages['warnings']:
            lines.append('')
            lines.append('WARNINGS')
            lines.extend(''.join(('\t', x)) for x in messages['warnings'])

        lines.append('')
        lines.append('Favoring Player 1:')
        lines.extend(''.join(('\t', x)) for x in messages['favorp1'])
        lines.append('')
        lines.append('Favoring Player 2:')
        lines.extend(''.join(('\t', x)) for x in messages['favorp2'])
        lines.append('')
        lines.append('Similarities:')
        lines.extend(''.join(('\t', x)) for x in messages['similar'])

        self.setPlainText('\n'.join(lines))

    def on_player1_changed(self, player1):
        self.player1 = player1
        self.refresh_data()

    def on_player2_changed(self, player2):
        self.player2 = player2
        self.refresh_data()
