import logging

from PySide import QtCore  # noqa
from PySide import QtGui  # noqa


class SettingsDialog(QtGui.QDialog):
    log = logging.getLogger(__name__)

    settings_map = [
        {
            'name': 'Database',
            'items': [
                {
                    'label': 'Database URL',
                    'name': 'db_url',
                    'type': str,
                },
            ],
        },
        {
            'name': 'Site Integration',
            'items': [
                {
                    'label': 'Authenticate on startup',
                    'name': 'startup_auth_check',
                    'type': bool,
                },
                {
                    'label': 'username',
                    'name': 'auth_user',
                    'type': str,
                },
                {
                    'label': 'password',
                    'name': 'auth_password',
                    'type': str,
                },
                {
                    'label': 'State check interval in seconds (blank to disable)',
                    'name': 'state_check_interval',
                    'type': int,
                },
            ],
        },
        {
            'name': 'Logging',
            'items': [
                {
                    'label': 'Log Level',
                    'name': 'root_log_level',
                    'type': list,
                    'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                },
                {
                    'label': 'Log To Syslog',
                    'name': 'log_syslog',
                    'type': bool,
                },
                {
                    'label': 'Log To stdout',
                    'name': 'log_stdout',
                    'type': bool,
                },
            ],
        },
        {
            'name': 'Debugging',
            'items': [
                {
                    'label': 'Dump bad stats pages',
                    'name': 'dump_bad_stats',
                    'type': bool,
                },
            ],
        },
    ]

    def create_pages(self):
        for page_values in self.settings_map:
            page = self.create_page(page_values)
            self.pages.addWidget(page)

            list_item = QtGui.QListWidgetItem(self.contents)
            list_item.setText(page_values['name'])
            list_item.setTextAlignment(QtCore.Qt.AlignCenter)
            list_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

            self.contents.currentItemChanged.connect(self.on_contents_item_changed)

    def on_contents_item_changed(self, current, previous):
        if not current:
            current = previous

        self.pages.setCurrentIndex(self.contents.row(current))

    def create_page(self, page_values):
        page = QtGui.QWidget()
        layout = QtGui.QGridLayout()

        row = 0

        for values in page_values['items']:
            label, widget = self.create_widget(values)

            if label:
                layout.addWidget(label, row, 0, 1, 1, 0)
                layout.addWidget(widget, row, 1, 1, 1, 0)
            else:
                layout.addWidget(widget, row, 0, 1, 2, 0)

            row += 1

        page.setLayout(layout)

        return page

    def create_widget(self, values):
        app = QtGui.QApplication.instance()
        widget = None
        title = values['label']
        name = values['name']
        value_type = values['type']

        def update_setting(new_value):
            old_value = app.settings.value(name)
            app.settings.setValue(name, new_value)
            app.setting_changed.emit(name, new_value, old_value)

        # str, bool, int, list

        if value_type == str:
            widget = QtGui.QLineEdit()
            widget.setText(app.settings.value(name))

            def valueChanged():
                update_setting(str(widget.text()))

            widget.editingFinished.connect(valueChanged)
            return QtGui.QLabel(title), widget

        elif value_type == bool:
            widget = QtGui.QCheckBox(title)

            if app.settings.value(name):
                widget.setCheckState(QtCore.Qt.Checked)
            else:
                widget.setCheckState(QtCore.Qt.Unchecked)

            def stateChanged(new_state):
                new_value = (new_state == QtCore.Qt.Checked)
                new_value = 1 if new_value else 0
                update_setting(str(new_value))

            widget.stateChanged.connect(stateChanged)
            return None, widget

        elif value_type == int:
            widget = QtGui.QLineEdit()
            widget.setText(app.settings.value(name))
            widget.setValidator(QtGui.QIntValidator(0, 1500, self))

            def valueChanged(new_value):
                update_setting(str(new_value))

            widget.textEdited.connect(valueChanged)
            return QtGui.QLabel(title), widget

        elif value_type == list:
            widget = QtGui.QComboBox()
            widget.addItems(values['choices'])
            widget.setCurrentIndex(widget.findText(app.settings.value(name), QtCore.Qt.MatchExactly))

            @QtCore.Slot(unicode)
            def currentIndexChanged(new_value):
                update_setting(str(new_value))

            widget.currentIndexChanged.connect(currentIndexChanged)
            return QtGui.QLabel(title), widget

    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle('Settings')

        self.contents = QtGui.QListWidget()
        self.contents.setViewMode(QtGui.QListView.IconMode)
        #TODO: Add icons
        #contentsWidget->setIconSize(QSize(96, 84));
        self.contents.setMovement(QtGui.QListView.Static)
        self.contents.setMaximumWidth(128)
        self.contents.setSpacing(12)

        self.pages = QtGui.QStackedWidget()
        self.create_pages()

        close_button = QtGui.QPushButton("Close")
        close_button.clicked.connect(self.close)

        self.contents.setCurrentRow(0)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(self.contents)
        hlayout.addWidget(self.pages, 1)

        buttons_layout = QtGui.QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(close_button)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(hlayout)
        main_layout.addStretch(1)
        main_layout.addSpacing(12)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
