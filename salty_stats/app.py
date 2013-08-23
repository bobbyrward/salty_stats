import sys
import logging  # noqa

from PySide import QtCore
from PySide import QtGui
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from salty_stats.character_model import CharacterListModel
from salty_stats.main_window import MainWindow


class Application(QtGui.QApplication):
    """Top Level Application Object

    Signals:
        player_1_changed(Character):
            Emitted when the player1 slot changes

        player_2_changed(Character):
            Emitted when the player2 slot changes

    Attributes:
        session:
            The app global session

        character_model:
            The global list model of characters

        settings:
            QSettings for the app

        player1:
            Currently selected player1 or None

        player2:
            Currently selected player2 or None
    """

    player_1_changed = QtCore.Signal(object)
    player_2_changed = QtCore.Signal(object)

    def __init__(self):
        super(Application, self).__init__(sys.argv)
        self.settings = QtCore.QSettings("saltybetstats", "saltybetstats")

        self.player1 = None
        self.player2 = None

        db_url = str(self.settings.value('db_url'))

        engine = create_engine(db_url)

        session_factory = sessionmaker(bind=engine)

        self.Session = scoped_session(session_factory)
        self.session = self.Session()

        self.character_model = CharacterListModel(self)

        self.main_window = MainWindow()

    def on_player_1_changed(self, character):
        self.player1 = character

    def on_player_2_changed(self, character):
        self.player2 = character
