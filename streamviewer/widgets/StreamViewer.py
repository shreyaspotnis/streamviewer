from PyQt4 import QtGui, QtCore, uic

import os
import ast
import zmq
import time
import datetime

from widgets.DictEditor import DictEditor


zmq_context = zmq.Context()


class StreamViewer(QtGui.QWidget):

    def __init__(self, settings, settings_group='StreamViewer', parent=None):
        super(StreamViewer, self).__init__(parent)
        self.settings = settings
        self.settings_group = settings_group

        self.made_socket = False
        self.got_first_data = False

        self.setupUi()
        self.loadSettings()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.stream_settings['update_period_ms'])
        self.timer.timeout.connect(self.grabData)
        self.timer.start()


        self.updateSettingsLabel()
        self.makeConnection()

    def setupUi(self):
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.edit_stream_button = QtGui.QPushButton('Edit Stream', self)
        self.edit_stream_button.clicked.connect(self.handleEditStreamButtonClicked)

        self.settings_label = QtGui.QLabel(self)
        self.timestamp_label = QtGui.QLabel(self)

        self.grid.addWidget(self.edit_stream_button, 0, 0, 1, 1)
        self.grid.addWidget(self.settings_label, 0, 1, 1, 1)
        self.grid.addWidget(self.timestamp_label, 0, 2, 1, 1)

    def updateSettingsLabel(self):
        s = 'tcp://{0}:{1}, topic: {5}, update period: {2} ms,\nlog? {3}, log folder: {4}'
        ss = self.stream_settings
        label_str = s.format(ss['ip_addr'], ss['port'], ss['update_period_ms'],
                             ss['logdata'], ss['log_folder'], ss['topic'])
        self.settings_label.setText(label_str)

    def handleEditStreamButtonClicked(self):
        ss_temp = dict(self.stream_settings)
        ss_temp['log_folder'] = QtCore.QFileInfo(ss_temp['log_folder'])

        d = DictEditor(ss_temp)
        if d.exec_():
            new_folder = str(ss_temp['log_folder'].canonicalFilePath())
            ss_temp['log_folder'] = new_folder
            self.stream_settings = ss_temp
            self.timer.setInterval(self.stream_settings['update_period_ms'])
            self.makeConnection()

    def loadSettings(self):

        self.settings.beginGroup(self.settings_group)
        ss_string = str(self.settings.value('stream_settings').toString())
        if ss_string == '':
            self.stream_settings = {'ip_addr': 'localhost',
                                    'port': 5557,
                                    'update_period_ms': 100,
                                    'log_folder': str(QtCore.QDir.homePath()),
                                    'logdata': False,
                                    'topic': 'wa1500'}
        else:
            self.stream_settings = ast.literal_eval(ss_string)
        self.settings.endGroup()

    def makeConnection(self):
        if self.made_socket:
            self.socket.close()
        else:
            self.made_socket = True

        # Socket to talk to server
        self.socket = zmq_context.socket(zmq.SUB)

        connect_string = "tcp://%s:%s" % (self.stream_settings['ip_addr'],
                                          self.stream_settings['port'])
        self.socket.connect(connect_string)
        self.socket.setsockopt(zmq.SUBSCRIBE, self.stream_settings['topic'])

    def grabData(self):
        if self.made_socket:
            try:
                string = self.socket.recv(flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                # no data recvd, change label to red
                text = str(self.timestamp_label.text())
                self.timestamp_label.setText(text.replace('green', 'red'))
                return

            out = string.split(' ')
            topic, time = out[:2]
            messagedata = ast.literal_eval(' '.join(out[2:]))

            self.timestamp = float(time)
            self.messagedata = messagedata

            self.displayData()

    def displayData(self):
        fmt = '%Y-%m-%d %H:%M:%S'
        dt_disp = datetime.datetime.fromtimestamp(self.timestamp).strftime(fmt)
        lstrfmt = '<b><font color="green">last recvd: {0}</font></b>'
        lstr = lstrfmt.format(dt_disp)
        self.timestamp_label.setText(lstr)

        if self.got_first_data is False:
            # make boxes to display the data
            self.data_labels = []
            self.data_lineedits = []
            for i, key in enumerate(sorted(self.messagedata.keys())):
                label = QtGui.QLabel(key, self)
                lineedit = QtGui.QLineEdit(str(self.messagedata[key]), self)

                self.grid.addWidget(label, i+1, 0, 1, 1)
                self.grid.addWidget(lineedit, i+1, 1, 1, 1)

                self.data_labels.append(label)
                self.data_lineedits.append(lineedit)
            self.got_first_data = True
        else:
            # boxes already made, just update the data
            for key, le in zip(sorted(self.messagedata.keys()),
                               self.data_lineedits):
                le.setText(str(self.messagedata[key]))


    def saveSettings(self):
        self.settings.beginGroup(self.settings_group)
        ss_string = repr(self.stream_settings)
        self.settings.setValue('stream_settings', ss_string)
        self.settings.endGroup()

