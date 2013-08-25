import logging

from PySide import QtCore
from PySide import QtGui


class MatchHistoryItemDelegate(QtGui.QStyledItemDelegate):
    log = logging.getLogger(__name__)

    def __init__(self, parent):
        super(MatchHistoryItemDelegate, self).__init__(parent)

    def initStyleOption(self, option, index):
        super(MatchHistoryItemDelegate, self).initStyleOption(option, index)

        model = self.parent().model()

        if model.character is None:
            return

        match = model.matchFromIndex(index)

        if model.character == match.winner:
            option.backgroundBrush = QtGui.QBrush(QtGui.QColor(255, 0, 0))

        option.version = 4


class MatchHistoryTableView(QtGui.QTableView):
    log = logging.getLogger(__name__)

    def __init__(self, parent, model):
        super(MatchHistoryTableView, self).__init__(parent)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(False)
        self.setModel(model)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setItemDelegate(MatchHistoryItemDelegate(self))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
