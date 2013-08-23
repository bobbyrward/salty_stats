from PySide import QtCore
from PySide import QtGui

from salty_stats import db


class CharacterListModel(QtCore.QAbstractListModel):
    """Model for a simple list of all characters sorted by name
    """

    def __init__(self, parent):
        super(CharacterListModel, self).__init__(parent)
        self.refresh()

    def refresh(self):
        """Refreshes the list of characters from the db
        """
        session = QtGui.QApplication.instance().session
        self.characters = session.query(db.Character).order_by(db.Character.name).all()

    def rowCount(self, parent):
        return len(self.characters)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.characters[index.row()].name
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return 'Characters'
        else:
            return None
