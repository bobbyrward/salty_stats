import logging

from PySide import QtCore
from PySide import QtGui

from salty_stats.match_history_model import MatchHistoryTabelModel


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

    def __init__(self, parent, signal):
        super(MatchHistoryTableView, self).__init__(parent)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.setTabKeyNavigation(False)
        self.setModel(MatchHistoryTabelModel(self, None))
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setItemDelegate(MatchHistoryItemDelegate(self))
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        signal.connect(self.on_character_changed)

    def on_character_changed(self, character):
        self.setModel(MatchHistoryTabelModel(self, character))
