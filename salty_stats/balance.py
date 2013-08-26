from PySide import QtGui


class BalanceView(QtGui.QGroupBox):
    def __init__(self, parent):
        super(BalanceView, self).__init__('Balance', parent)
        self.balance = QtGui.QLabel('')

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.balance)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        app = QtGui.QApplication.instance()
        app.balance_updated.connect(self.on_balance_updated)

    def on_balance_updated(self, new_balance):
        self.balance.setText(str(new_balance))
