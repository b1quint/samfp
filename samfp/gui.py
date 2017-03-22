# -*- coding: utf-8 -*-

from __future__ import print_function, division
from PyQt4 import QtCore, QtGui, Qt

import configparser
import logging
import sys

logging.basicConfig()
log = logging.getLogger("samfp.scan")
log.setLevel(logging.DEBUG)


class Main(QtGui.QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        self.initUI()

    def initUI(self):

        # Set the font of the ToolTip windows
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # Create the status bar
        self.statusBar()

        # Create an action to leave the program
        # TODO Get icons for these
        load_action = QtGui.QAction(QtGui.QIcon('load_file.png'), 'Open', self)
        load_action.setShortcut('Ctrl+o')
        load_action.setStatusTip('Open new file.')
        load_action.triggered.connect(self.load_config_file)

        exit_action = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        # Create the menu bar
        menubar = self.menuBar()
        menu = menubar.addMenu('&File')
        menu.addAction(load_action)
        menu.addAction(exit_action)

        # Create the central widget
        central = CentralWidget()
        self.setCentralWidget(central)
        self.active_panel = central

        # Set the geometry
        #self.resize(800, 600)
        self.center()

        self.setWindowTitle('SAM-FP - Data-Acquisition')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.show()

    def center(self):

        # Figure out the screen resolution of our monitor.
        # And from this resolution, we get the center point.
        cp = QtGui.QDesktopWidget().availableGeometry().center()

        # get a rectangle specifying the geometry of the main window.
        # This includes any window frame
        qr = self.frameGeometry()

        # Our rectangle has already its width and height.
        # Now we set the center of the rectangle to the center of the screen.
        # The rectangle's size is unchanged.
        qr.moveCenter(cp)

        # We move the top-left point of the application window to the top-left
        # point of the qr rectangle, thus centering the window on our screen.
        self.move(qr.topLeft())

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def load_config_file(self):

        # TODO Isolate only configuration files
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')

        cfg = configparser.RawConfigParser()
        cfg.read("scan.ini")

        self.active_panel.basename.setText(cfg.get('image', 'basename'))
        self.active_panel.comment.setText(cfg.get('image', 'comment'))
        self.active_panel.target.setText(cfg.get('image', 'title'))
        self.active_panel.path.setText(cfg.get('image', 'dir'))

        index = self.active_panel.type.findText(
            cfg.get('image', 'type'), QtCore.Qt.MatchFixedString
        )
        if index >= 0:
            self.active_panel.type.setCurrentIndex(index)


class CentralWidget(QtGui.QFrame):

    def __init__(self):
        super(CentralWidget, self).__init__()
        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.basename = TextField("Basename: ", "samfp_scan")
        self.path = TextField("Remote path:", "/home2/images/SAMFP/")
        self.target_name = TextField("Target name:", "NGC0000")
        self.comment = TextField("Comment:", "---")
        self.obs_type = ComboBox("Observation type: ",
                                ["DARK", "DFLAT", "OBJECT", "SFLAT", "ZERO"])

        self.exp_time = TextField("Exposure time [s]:", "1.0")
        self.frames_per_channel = TextField("Frames per channel:", "1")

        grid.addWidget(self.basename.label, 0, 0)
        grid.addWidget(self.basename.line_edit, 0, 1)

        grid.addWidget(self.path.label, 1, 0)
        grid.addWidget(self.path.line_edit, 1, 1)

        grid.addWidget(self.obs_type.label, 2, 0)
        grid.addWidget(self.obs_type.combo_box, 2, 1)

        grid.addWidget(self.target_name.label, 3, 0)
        grid.addWidget(self.target_name.line_edit, 3, 1)

        grid.addWidget(self.comment.label, 4, 0)
        grid.addWidget(self.comment.line_edit, 4, 1)

        grid.addWidget(self.HLine(), 5, 0, 1, 2)

        grid.addWidget(self.exp_time.label, 6, 0)
        grid.addWidget(self.exp_time.line_edit, 6, 1)

        grid.addWidget(self.frames_per_channel.label, 7, 0)
        grid.addWidget(self.frames_per_channel.line_edit, 7, 1)

        notebook = QtGui.QTabWidget()
        grid.addWidget(notebook, 0, 2, 8, 1)

        page1 = SimpleScan()
        notebook.addTab(page1, "Simple Scan")

        self.setLayout(grid)

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto


class SimpleScan(QtGui.QWidget):

    def __init__(self):

        super(SimpleScan, self).__init__()

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.scan_id = TextField("Scan ID:", "")
        self.n_channels = TextField("Number of channels:", "1")
        self.sleep_time = TextField("Sleep time [s]:", "0.0")
        self.z_start = TextField("Z Start [bcv]:", "0")
        self.z_step = TextField("Z Step [bcv]:", "0")

        self.scan_id.add_button("Get ID")
        grid.addWidget(self.scan_id.label, 0, 0)
        grid.addWidget(self.scan_id.line_edit, 0, 1)
        grid.addWidget(self.scan_id.button, 0, 2)

        grid.addWidget(self.n_channels.label, 1, 0)
        grid.addWidget(self.n_channels.line_edit, 1, 1)

        grid.addWidget(self.sleep_time.label, 2, 0)
        grid.addWidget(self.sleep_time.line_edit, 2, 1)

        grid.addWidget(self.z_start.label, 3, 0)
        grid.addWidget(self.z_start.line_edit, 3, 1)

        grid.addWidget(self.z_step.label, 4, 0)
        grid.addWidget(self.z_step.line_edit, 4, 1)

        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)


class ComboBox(QtGui.QWidget):

    def __init__(self, label, options):

        super(ComboBox, self).__init__()

        self.label = QtGui.QLabel(label)
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(options)


class TextField(QtGui.QWidget):

    def __init__(self, label, text):
        """
        Initialize field that contains a label (QtGui.QLabel) and a text field
         (QtGui.QLineEdit).

        Parameters
        ----------
        label (string) : the field label
        text (string) : the text that will be inside the text box
        """
        super(TextField, self).__init__()

        self.button = None
        self.label = QtGui.QLabel(label)
        self.line_edit = QtGui.QLineEdit(text)
        self.line_edit.setAlignment(QtCore.Qt.AlignRight)

    def add_button(self, label):
        self.button = QtGui.QPushButton(label)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())