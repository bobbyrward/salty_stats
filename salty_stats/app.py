import sys
import json
import logging  # noqa
import logging.config
import logging.handlers

from PySide import QtCore
from PySide import QtGui

from salty_stats import db
from salty_stats.character_model import CharacterListModel
from salty_stats.main_window import MainWindow
from salty_stats.request_processor import RequestProcessor
from salty_stats.stats_crawler import StatsCrawler
from salty_stats.predictor import predict_winner


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
    prediction_changed = QtCore.Signal(object, object, object)
    log = logging.getLogger(__name__)

    def __init__(self):
        super(Application, self).__init__(sys.argv)
        self.aboutToQuit.connect(self.on_exit)

        self.settings = QtCore.QSettings("saltybetstats", "saltybetstats")

        self.player1 = None
        self.player2 = None
        self.player_1_changed.connect(self.on_player_1_changed)
        self.player_2_changed.connect(self.on_player_2_changed)

        self.Session = db.create_session_class()
        self.session = self.Session()

        cookies = self.settings.value('cookies')

        if not cookies:
            cookies = {}
        else:
            cookies = json.loads(cookies)

        self.request_processor = RequestProcessor(self, cookies)
        self.request_processor.start()
        self.request_processor.request_processor_started.connect(self.on_rp_started)
        self.request_processor.authentication_succeeded.connect(self.on_rp_auth_success)

        self.stats_crawler = StatsCrawler(self)
        self.stats_crawler.start()

        self.character_model = CharacterListModel(self)

        self.main_window = MainWindow()

    def on_player_1_changed(self, character):
        self.player1 = character
        self.make_prediction()

    def on_player_2_changed(self, character):
        self.player2 = character
        self.make_prediction()

    def make_prediction(self):
        if self.player1 is None or self.player2 is None:
            self.prediction = None
        else:
            self.log.debug('making prediction: {} vs {}'.format(self.player1.name, self.player2.name))
            self.prediction = predict_winner(self.session, self.player1, self.player2)
            self.prediction_changed.emit(self.prediction, self.player1, self.player2)

    def on_exit(self):
        cookies = dict(self.request_processor.cookies)
        self.settings.setValue('cookies', json.dumps(cookies))
        self.log.debug('Persisting cookies: {}'.format(cookies))

        self.request_processor.quit()
        self.stats_crawler.quit()

    def on_rp_started(self, request_processor):
        if self.settings.value('startup_auth_check'):
            request_processor.do_login_check()

    def on_rp_auth_success(self, rp):
        #self.log.debug('Auth Success, now crawling')
        #self.stats_crawler.push_request('http://www.saltybet.com/stats?tournament_id=82')
        pass

    def setup_logging(self):
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'basic': {
                    'format': '%(name)s: %(levelname)s: %(message)s',
                },
            },
            'handlers': {
                'syslog': {
                    'level': 'NOTSET',
                    'class': 'logging.handlers.SysLogHandler',
                    'address': '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log',
                    'facility': logging.handlers.SysLogHandler.LOG_LOCAL0,
                    'formatter': 'basic',
                },
                'console': {
                    'level': 'NOTSET',
                    'class': 'logging.StreamHandler',
                    'stream': sys.stdout,
                    'formatter': 'basic',
                },
            },
            'loggers': {
                'requests': {
                    'level': 'DEBUG',
                },
            },
            'root': {
                'handlers': ['syslog', 'console'],
                'level': 'DEBUG',
            },
        }

        logging.config.dictConfig(LOGGING)
