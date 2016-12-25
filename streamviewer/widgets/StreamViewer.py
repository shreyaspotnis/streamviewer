from PyQt4 import QtGui, QtCore, uic
from datetime import datetime
import os
from widgets.DictEditor import DictEditor
import ast


class StreamViewer(QtGui.QWidget):

    def __init__(self, settings, settings_group='StreamViewer', parent=None):
        super(StreamViewer, self).__init__(parent)
        self.settings = settings
        self.settings_group = settings_group

        self.setupUi()
        self.loadSettings()

    def setupUi(self):
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.edit_stream_button = QtGui.QPushButton('Edit Stream', self)
        self.edit_stream_button.clicked.connect(self.handleEditStreamButtonClicked)

        self.grid.addWidget(self.edit_stream_button, 0, 0, 1, 1)

    def handleEditStreamButtonClicked(self):
        ss_temp = dict(self.stream_settings)
        ss_temp['log_folder'] = QtCore.QFileInfo(ss_temp['log_folder'])

        print ss_temp

        d = DictEditor(ss_temp)
        if d.exec_():
            new_folder = str(ss_temp['log_folder'].canonicalFilePath())
            ss_temp['log_folder'] = new_folder
            self.stream_settings = ss_temp

        print self.stream_settings


    def loadSettings(self):
        self.settings.beginGroup(self.settings_group)
        ss_string = str(self.settings.value('stream_settings').toString())
        if ss_string == '':
            self.stream_settings = {'ip_addr': 'localhost',
                                    'port': 5557,
                                    'update_period_ms': 100,
                                    'log_folder': str(QtCore.QDir.homePath()),
                                    'logdata': False}
        else:
            self.stream_settings = ast.literal_eval(ss_string)
        self.settings.endGroup()

    def saveSettings(self):
        self.settings.beginGroup(self.settings_group)
        ss_string = repr(self.stream_settings)
        self.settings.setValue('stream_settings', ss_string)
        self.settings.endGroup()

