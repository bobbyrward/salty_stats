from PySide import QtCore
from PySide import QtGui


class CharacterCompleter(QtGui.QCompleter):
    """QCompleter to complete character names
    """

    def __init__(self, parent):
        super(CharacterCompleter, self).__init__(parent)
        self.setModel(QtGui.QApplication.instance().character_model)
        self.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QtGui.QCompleter.UnfilteredPopupCompletion)


class CharacterSelector(QtGui.QComboBox):
    """QComboBox to select a character name

    AutoCompletes the character name

    You must pass a signal to __init__.
    This is emitted when the character is selected.
    """

    def __init__(self, parent, signal):
        super(CharacterSelector, self).__init__(parent)

        self.completer = CharacterCompleter(self)

        self.setModel(QtGui.QApplication.instance().character_model)
        self.currentIndexChanged.connect(self.on_list_selection_changed)
        self.setCompleter(self.completer)
        self.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self.setMaxCount(5)
        self.setEditable(True)

        self.setCurrentIndex(0)

        self.change_signal = signal

    @property
    def selected_character(self):
        index = self.currentIndex()
        item = self.model().characters[index]
        return item

    def on_list_selection_changed(self, index):
        self.change_signal.emit(self.selected_character)
