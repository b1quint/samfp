# -*- coding: utf-8 -*-

from __future__ import print_function, division
from PyQt4 import QtCore, QtGui, Qt

import configparser
import logging
import sys

logging.basicConfig()
log = logging.getLogger("samfp.scan")
log.setLevel(logging.DEBUG)


class Communicate(QtCore.QObject):
    closeApp = QtCore.pyqtSignal()


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

        self.c = Communicate()
        self.c.closeApp.connect(self.close)

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

        basename = QtGui.QLabel('Basename:')
        basename_edit = QtGui.QLineEdit()
        basename_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(basename, 0, 0)
        grid.addWidget(basename_edit, 0, 1)

        path = QtGui.QLabel('Remote path:')
        path_edit = QtGui.QLineEdit()
        path_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(path, 1, 0)
        grid.addWidget(path_edit, 1, 1)

        type = QtGui.QLabel('Observation type:')
        type_combo = QtGui.QComboBox()
        type_combo.addItems(["DARK", "DFLAT", "OBJECT", "SFLAT", "ZERO"])
        grid.addWidget(type, 2, 0)
        grid.addWidget(type_combo, 2, 1)

        target = QtGui.QLabel('Target name:')
        target_edit = QtGui.QLineEdit()
        target_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(target, 3, 0)
        grid.addWidget(target_edit, 3, 1)

        comment = QtGui.QLabel('Comment:')
        comment_edit = QtGui.QLineEdit()
        comment_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(comment, 4, 0)
        grid.addWidget(comment_edit, 4, 1)

        grid.addWidget(self.HLine(), 5, 0, 1, 2)

        exptime = QtGui.QLabel('Exposure time [s]:')
        exptime_edit = QtGui.QLineEdit()
        exptime_edit.setText("{:0.1f}".format(1.0))
        exptime_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(exptime , 6, 0)
        grid.addWidget(exptime_edit, 6, 1)

        nframes = QtGui.QLabel('Frames per channel:')
        nframes_edit = QtGui.QLineEdit()
        nframes_edit.setText("{:d}".format(1))
        nframes_edit.setAlignment(QtCore.Qt.AlignRight)
        grid.addWidget(nframes, 7, 0)
        grid.addWidget(nframes_edit, 7, 1)

        notebook = QtGui.QTabWidget()
        grid.addWidget(notebook, 0, 2, 8, 1)

        page1 = SimpleScan()
        notebook.addTab(page1, "Simple Scan")

        self.setLayout(grid)

        self.basename = basename_edit
        self.comment = comment_edit
        self.notebook = notebook
        self.target = target_edit
        self.type = type_combo
        self.path = path_edit

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto

class SimpleScan(QtGui.QWidget):

    def __init__(self):
        super(SimpleScan, self).__init__()
        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        id_lbl = QtGui.QLabel("Scan ID:")
        id_txt = QtGui.QLineEdit(alignment=QtCore.Qt.AlignRight)
        id_btm = QtGui.QPushButton("Get ID")
        grid.addWidget(id_lbl, 0, 0)
        grid.addWidget(id_txt, 0, 1)
        grid.addWidget(id_btm, 0, 2)

        nchannels_lbl = QtGui.QLabel("Number of channels:")
        nchannels_txt = QtGui.QLineEdit(alignment=QtCore.Qt.AlignRight)
        nchannels_txt.setText("1")
        grid.addWidget(nchannels_lbl, 1, 0)
        grid.addWidget(nchannels_txt, 1, 1)

        stime_lbl = QtGui.QLabel("Sleep time [s]:")
        stime_txt = QtGui.QLineEdit("0")
        stime_txt.setAlignment(QtCore.Qt.AlignRight)

        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)

        self.id = id_txt
        self.nchannels = nchannels_txt


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())