from PyQt4 import QtGui, QtCore, uic
from pyqtgraph.dockarea import DockArea, Dock
import random
from datetime import datetime
import os

from StreamViewer import StreamViewer

main_package_dir = os.path.join(os.path.dirname(__file__), os.pardir)


class MainWindow(QtGui.QMainWindow):
    """The only window of the application."""

    def __init__(self, settings):
        super(MainWindow, self).__init__()
        self.settings = settings

        # self.setupUi(self)

        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        self.setupUi()

        self.loadSettings()

    def setupUi(self):
        self.createDocks()

    def createDocks(self):
        self.zmq_viewer = StreamViewer(self.settings, settings_group='StreamViewer',
                                    parent=self)
        self.zmq_viewer_dock = Dock('StreamViewer',
                                        widget=self.zmq_viewer)
        self.dock_area.addDock(self.zmq_viewer_dock)

    def loadSettings(self):
        """Load window state from self.settings"""

        self.settings.beginGroup('mainwindow')
        geometry = self.settings.value('geometry').toByteArray()
        state = self.settings.value('windowstate').toByteArray()
        dock_string = str(self.settings.value('dockstate').toString())
        if dock_string is not "":
            dock_state = eval(dock_string)
            self.dock_area.restoreState(dock_state)
        self.settings.endGroup()

        self.restoreGeometry(geometry)
        self.restoreState(state)

    def saveSettings(self):
        """Save window state to self.settings."""
        self.settings.beginGroup('mainwindow')
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowstate', self.saveState())
        dock_state = self.dock_area.saveState()
        # dock_state returned here is a python dictionary. Coundn't find a good
        # way to save dicts in QSettings, hence just using representation
        # of it.
        self.settings.setValue('dockstate', repr(dock_state))
        self.settings.endGroup()

    def closeEvent(self, event):
        self.zmq_viewer.saveSettings()
        self.saveSettings()
