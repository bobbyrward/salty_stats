import logging

from PySide import QtCore
from PySide import QtGui


class BettingDialog(QtGui.QDialog):
    # (playername, amount)
    bet_placed = QtCore.Signal(object, object)

    # response, context
    bet_finished = QtCore.Signal(object, object)

    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(BettingDialog, self).__init__(parent)
        app = QtGui.QApplication.instance()
        app.balance_updated.connect(self.on_balance_updated)

        self.bet_finished.connect(self.on_bet_finished)

        self.bet_amount = QtGui.QLineEdit()
        balance = int(100 if app.balance is None else app.balance)
        self.bet_amount.setValidator(QtGui.QIntValidator(1, balance, self))

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_accepted)
        buttons.rejected.connect(self.reject)

        self.player_1_button = QtGui.QRadioButton('Player 1')
        self.player_2_button = QtGui.QRadioButton('Player 2')

        self.player_button_group = QtGui.QButtonGroup(self)
        self.player_button_group.addButton(self.player_1_button)
        self.player_button_group.addButton(self.player_2_button)

        prediction = app.prediction.bet

        if prediction == app.player1.name:
            self.player_1_button.setChecked(True)
        else:
            self.player_2_button.setChecked(True)

        top_layout = QtGui.QGridLayout()
        top_layout.addWidget(QtGui.QLabel('Bet Amount'), 0, 0, 1, 1, 0)
        top_layout.addWidget(self.bet_amount, 0, 1, 1, 1, 0)

        top_layout.addWidget(QtGui.QLabel('Player'), 1, 0, 1, 1, 0)
        top_layout.addWidget(self.player_1_button, 1, 1, 1, 1, 0)
        top_layout.addWidget(self.player_2_button, 2, 1, 1, 1, 0)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_accepted(self):
        app = QtGui.QApplication.instance()

        amount = int(self.bet_amount.text())
        button = self.player_button_group.checkedButton()
        player = 'player1' if button == self.player_1_button else 'player2'

        request = {
            'method': 'POST',
            'url': 'http://www.saltybet.com/ajax_place_bet.php',
            'headers': {
                'X-Requested-With': 'XMLHttpRequest',
            },
            'data': {
                'radio': 'on',
                'selectedplayer': player,
                'wager': str(amount),
            },
        }

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        app.request_processor.push_request(request, self.bet_finished, None)

    def on_bet_finished(self, response, context):
        self.accept()
        QtGui.QApplication.restoreOverrideCursor()

    def on_balance_updated(self, new_balance):
        self.bet_amount.validator().setRange(0, int(new_balance))
