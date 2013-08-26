import logging

from PySide import QtCore
from PySide import QtGui


class MatchHistoryTabelModel(QtCore.QAbstractTableModel):
    log = logging.getLogger(__name__)

    def __init__(self, parent, character):
        self.log.debug('MatchHistoryTabelModel.__init__')
        super(MatchHistoryTabelModel, self).__init__(parent)
        self.character = character
        self.matches = []

        if character is not None:
            self.matches.extend(x for x in character.matches if x.winner == character)
            self.matches.extend(x for x in character.matches if x.winner != character)

    def rowCount(self, parent):
        if self.character is None:
            return 0
        else:
            return len(self.matches)

    def columnCount(self, parent):
        return 3

    def matchFromIndex(self, index):
        return self.matches[index.row()]

    def data(self, index, role):
        match = self.matches[index.row()]

        if role == QtCore.Qt.DisplayRole:
            column = index.column()
            opponent = [x.character for x in match.characters if x.character != self.character][0]

            # opponent
            if column == 0:
                found = opponent.name
            # opponents win ratio
            elif column == 1:
                try:
                    found = str(round(opponent.win_loss_ratio, 2))
                except TypeError:
                    found = opponent.win_loss_ratio
            # opponents rating
            elif column == 2:
                found = str(opponent.rating)

            return found
        elif role == QtCore.Qt.BackgroundRole:
            if match.winner == self.character:
                return QtGui.QApplication.instance().palette().alternateBase()
            else:
                return QtGui.QApplication.instance().palette().base()
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return None

            return ['Opponent', 'Ratio', 'Rating'][section]
        else:
            return None
