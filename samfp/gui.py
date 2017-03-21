# -*- coding: utf-8 -*-

from __future__ import print_function, division
from PyQt4 import QtCore, QtGui

import logging

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

        # Create an action to leave the program
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        # Create the status bar
        self.statusBar()

        # Create the menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        # Create the central widget
        central = SimpleScan()
        self.setCentralWidget(central)

        # Set the geometry
        self.resize(300, 200)
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

class SimpleScan(QtGui.QWidget):

    def __init__(self):
        super(SimpleScan, self).__init__()
        self.initUI()

    def initUI(self):

        title = QtGui.QLabel('Title')
        author = QtGui.QLabel('Author')
        review = QtGui.QLabel('Review')

        titleEdit = QtGui.QLineEdit()
        authorEdit = QtGui.QLineEdit()
        reviewEdit = QtGui.QTextEdit()

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(title, 1, 0)
        grid.addWidget(titleEdit, 1, 1)

        grid.addWidget(author, 2, 0)
        grid.addWidget(authorEdit, 2, 1)

        grid.addWidget(review, 3, 0)
        grid.addWidget(reviewEdit, 3, 1, 5, 1)

        self.setLayout(grid)

        self.setWindowTitle('Review')
        self.show()