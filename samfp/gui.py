# -*- coding: utf-8 -*-

from __future__ import print_function, division
from PyQt4 import QtCore, QtGui, Qt

import configparser
import datetime
import logging
import sys
import os

logging.basicConfig()
log = logging.getLogger("samfp.scan")
log.setLevel(logging.DEBUG)

root = "/home/bquint/PycharmProjects/samfp/"

class Main(QtGui.QMainWindow):

    config = {
        'temp_file': '.samfp_temp.ini'
    }

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
        load_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/file-import.png')),
            'Open', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setStatusTip('Load config file.')
        load_action.triggered.connect(self.load_config_file)

        save_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/content-save.png')),
            'Open', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save config file.')
        save_action.triggered.connect(self.save_config_file)

        exit_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/exit-to-app.png'))
            ,'&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        # Create the menu bar
        menubar = self.menuBar()
        menu = menubar.addMenu('&File')
        menu.addAction(load_action)
        menu.addAction(exit_action)

        # Create the toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(load_action)
        self.toolbar.addAction(exit_action)

        # Create the central widget
        central = CentralWidget()
        self.setCentralWidget(central)
        self.active_panel = central

        # Set the geometry
        #self.resize(800, 600)
        self.center()

        self.setWindowTitle('SAM-FP - Data-Acquisition')
        self.setWindowIcon(QtGui.QIcon('web.png'))

        self.load_temp_file()
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

        self.save_temp_file()
        # reply = QtGui.QMessageBox.question(self, 'Message',
        #                                    "Are you sure to quit?",
        #                                    QtGui.QMessageBox.Yes |
        #                                    QtGui.QMessageBox.No,
        #                                    QtGui.QMessageBox.No)
        #
        # if reply == QtGui.QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()



    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def config_parse(self, config_file):

        log.debug('Loading config file: {}'.format(config_file))

        cfg = configparser.RawConfigParser()
        cfg.read("{}".format(config_file))

        self.active_panel.basename.text = cfg.get('image', 'basename')
        self.active_panel.comment.text = cfg.get('image', 'comment')
        self.active_panel.path.text = cfg.get('image', 'dir')
        self.active_panel.target_name.text = cfg.get('image', 'title')

        index = self.active_panel.obs_type.combo_box.findText(
            cfg.get('image', 'type'), QtCore.Qt.MatchFixedString
        )
        if index >= 0:
            self.active_panel.obs_type.combo_box.setCurrentIndex(index)

        self.active_panel.exp_time.value = cfg.getfloat('obs', 'exptime')
        self.active_panel.n_frames.value = cfg.getint('obs', 'nframes')

        scan_page = self.active_panel.scan_page
        scan_page.scan_id.text = cfg.get('scan', 'id')
        scan_page.n_channels.value = cfg.getint('scan', 'nchannels')
        scan_page.n_sweeps.value = cfg.getint('scan', 'nsweeps')
        scan_page.z_start.value = cfg.getint('scan', 'zstart')
        scan_page.z_step.value = cfg.getfloat('scan', 'zstep')
        scan_page.sleep_time.value = cfg.getfloat('scan', 'stime')

    def config_generate(self):

        cfg = configparser.RawConfigParser()
        cfg.add_section('image')
        cfg.set('image', 'basename', self.active_panel.basename.text)
        cfg.set('image', 'comment', self.active_panel.comment.text)
        cfg.set('image', 'dir', self.active_panel.path.text)
        cfg.set('image', 'type',
                self.active_panel.obs_type.combo_box.currentText())
        cfg.set('image', 'title', self.active_panel.target_name.text)

        cfg.add_section('obs')
        cfg.set('obs', 'exptime', self.active_panel.exp_time.value)
        cfg.set('obs', 'nframes', self.active_panel.n_frames.value)

        cfg.add_section('scan')
        cfg.set('scan', 'id', self.active_panel.scan_page.scan_id.text)
        cfg.set('scan', 'nchannels', self.active_panel.scan_page.n_channels.value)
        cfg.set('scan', 'nsweeps', self.active_panel.scan_page.n_sweeps.value)
        cfg.set('scan', 'stime', self.active_panel.scan_page.sleep_time.value)
        cfg.set('scan', 'zstart', self.active_panel.scan_page.z_start.value)
        cfg.set('scan', 'zstep', self.active_panel.scan_page.z_step.value)

        return cfg

    def load_config_file(self):
        # TODO Isolate only configuration files
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.')
        fname = str(fname)
        self.config_parse(fname)

    def load_temp_file(self):
        if os.path.exists(self.config['temp_file']):
            try:
                self.config_parse(self.config['temp_file'])
            except configparser.NoOptionError as error:
                log.warning("{}".format(error.option) + \
                            "option not found in the input config file")
        else:
            log.debug('Temp config file does not exists.')

    def save_config_file(self):

        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', os.getcwd())
        fname = str(fname)

        temp_config = self.config_generate()
        with open(self.config['temp_file'], 'w') as foo:
            temp_config.write(foo)


    def save_temp_file(self):
        temp_config = self.config_generate()
        with open(self.config['temp_file'], 'w') as foo:
            temp_config.write(foo)


class CentralWidget(QtGui.QFrame):

    def __init__(self):
        super(CentralWidget, self).__init__()
        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.basename = LineField_Text("Basename: ", "samfp_scan")
        self.path = LineField_Text("Remote path:", "/home2/images/SAMFP/")
        self.target_name = LineField_Text("Target name:", "NGC0000")
        self.comment = LineField_Text("Comment:", "---")
        self.obs_type = ComboBox("Observation type: ",
                                ["DARK", "DFLAT", "OBJECT", "SFLAT", "ZERO"])

        self.exp_time = LineField_Float("Exposure time [s]:", 1.0)
        self.n_frames = LineField_Int("Frames per channel:", 1)

        self.scan = QtGui.QPushButton("Scan")
        self.abort = QtGui.QPushButton("Abort")
        self.progress = QtGui.QProgressBar()

        self.abort.setDisabled(True)
        self.progress.setDisabled(True)

        grid.addWidget(self.basename.label, 0, 0, 1, 3)
        grid.addWidget(self.basename.line_edit, 0, 1, 1, 3)

        grid.addWidget(self.path.label, 1, 0, 1, 3)
        grid.addWidget(self.path.line_edit, 1, 1, 1, 3)

        grid.addWidget(self.HLine(), 2, 0, 1, 3)

        grid.addWidget(self.obs_type.label, 3, 0)
        grid.addWidget(self.obs_type.combo_box, 3, 1)

        grid.addWidget(self.target_name.label, 4, 0)
        grid.addWidget(self.target_name.line_edit, 4, 1)

        grid.addWidget(self.comment.label, 5, 0)
        grid.addWidget(self.comment.line_edit, 5, 1)

        grid.addWidget(self.HLine(), 6, 0, 1, 2)

        grid.addWidget(self.exp_time.label, 7, 0)
        grid.addWidget(self.exp_time.line_edit, 7, 1)

        grid.addWidget(self.n_frames.label, 8, 0)
        grid.addWidget(self.n_frames.line_edit, 8, 1)

        notebook = QtGui.QTabWidget()
        grid.addWidget(notebook, 3, 2, 6, 1)

        grid.addWidget(self.HLine(), 9, 0, 1, 3)

        grid.addWidget(self.scan, 10, 0)
        grid.addWidget(self.abort, 10, 1)
        grid.addWidget(self.progress, 10, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 3)

        self.scan_page = PageScan()
        notebook.addTab(self.scan_page, "Simple Scan")

        self.calib_page = PageCalibrationScan()
        notebook.addTab(self.calib_page, "Calibration Scan")

        self.sci_page = PageScienceScan()
        notebook.addTab(self.sci_page, "Science Scan")

        self.setLayout(grid)

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto


class ComboBox(QtGui.QWidget):

    def __init__(self, label, options):

        super(ComboBox, self).__init__()

        self.label = QtGui.QLabel(label)
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(options)


class LineField_Text(QtGui.QWidget):

    def __init__(self, label, text):
        """
        Initialize field that contains a label (QtGui.QLabel) and a text field
         (QtGui.QLineEdit).

        Parameters
        ----------
        label (string) : the field label
        text (string) : the text that will be inside the text box
        """
        super(LineField_Text, self).__init__()

        self.button = None
        self.label = QtGui.QLabel(label)
        self.line_edit = QtGui.QLineEdit(text)
        self.line_edit.setAlignment(QtCore.Qt.AlignRight)
        self.line_edit.setMinimumWidth(200)

        self._text = text

    def add_button(self, label):
        self.button = QtGui.QPushButton(label)

    @property
    def text(self):
        x = self.line_edit.text()
        return x

    @text.setter
    def text(self, x):
        self.line_edit.setText(x)
        self._text = x


class LineField_Int(QtGui.QWidget):

    def __init__(self, label, number):
        """
        Initialize field that contains a label (QtGui.QLabel) and a text field
         (QtGui.QLineEdit).

        Parameters
        ----------
        label (string) : the field label
        number (int) : the number that will be set to the field
        """
        assert (isinstance(number, int) or isinstance(number, float))

        super(LineField_Int, self).__init__()

        number = int(number)

        self.button = None
        self.label = QtGui.QLabel(label)
        self.line_edit = QtGui.QLineEdit("{:d}".format(number))
        self.line_edit.setAlignment(QtCore.Qt.AlignRight)

        self._value = number

    @property
    def value(self):
        x = self.line_edit.text()
        x = int(x)
        return x

    @value.setter
    def value(self, x):
        assert (isinstance(x, int) or isinstance(x, float))
        x = int(x)
        self.line_edit.setText("{:d}".format(x))
        self._value = x


class LineField_Float(QtGui.QWidget):

    def __init__(self, label, number):
        """
        Initialize field that contains a label (QtGui.QLabel) and a text field
         (QtGui.QLineEdit).

        Parameters
        ----------
        label (string) : the field label
        number (float) : the number that will be set to the field
        """
        assert (isinstance(number, int) or isinstance(number, float))

        super(LineField_Float, self).__init__()

        number = float(number)

        self.button = None
        self.label = QtGui.QLabel(label)
        self.line_edit = QtGui.QLineEdit("{:.1f}".format(number))
        self.line_edit.setAlignment(QtCore.Qt.AlignRight)

        self._value = number

    @property
    def value(self):
        x = self.line_edit.text()
        x = float(x)
        return x

    @value.setter
    def value(self, x):
        assert (isinstance(x, int) or isinstance(x, float))
        x = float(x)
        self.line_edit.setText("{:.1f}".format(x))
        self._value = x


class PageScan(QtGui.QWidget):
    def __init__(self):
        super(PageScan, self).__init__()

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.scan_id = LineField_Text("Scan ID:", "")
        self.n_channels = LineField_Int("Number of channels:", 1)
        self.n_sweeps = LineField_Int("Number of sweeps:", 1)
        self.z_start = LineField_Int("Z Start [bcv]:", 0)
        self.z_step = LineField_Float("Z Step [bcv]:", 0)
        self.sleep_time = LineField_Float("Sleep time [s]:", 0)

        self.scan_id.add_button("Get ID")
        self.scan_id.button.clicked.connect(self.get_id)

        grid.addWidget(self.scan_id.label, 0, 0)
        grid.addWidget(self.scan_id.line_edit, 0, 1)
        grid.addWidget(self.scan_id.button, 0, 2)

        grid.addWidget(self.n_channels.label, 1, 0)
        grid.addWidget(self.n_channels.line_edit, 1, 1)

        grid.addWidget(self.n_sweeps.label, 2, 0)
        grid.addWidget(self.n_sweeps.line_edit, 2, 1)

        grid.addWidget(self.z_start.label, 3, 0)
        grid.addWidget(self.z_start.line_edit, 3, 1)

        grid.addWidget(self.z_step.label, 4, 0)
        grid.addWidget(self.z_step.line_edit, 4, 1)

        grid.addWidget(self.sleep_time.label, 5, 0)
        grid.addWidget(self.sleep_time.line_edit, 5, 1)

        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)




    def get_id(self):
        now = datetime.datetime.now()
        s = now.strftime("SCAN_%Y%m%d_UTC%H%M%S")
        self.scan_id.text = s


class PageCalibrationScan(QtGui.QWidget):
    def __init__(self):
        super(PageCalibrationScan, self).__init__()


class PageScienceScan(QtGui.QWidget):
    def __init__(self):
        super(PageScienceScan, self).__init__()


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())