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
        load_action = self.get_load_action()
        save_action = self.get_save_action()
        exit_action = self.get_exit_action()

        # Create the menu bar
        menubar = self.menuBar()
        menu = menubar.addMenu('&File')
        menu.addAction(load_action)
        menu.addAction(save_action)
        menu.addAction(exit_action)

        # Create the toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(load_action)
        self.toolbar.addAction(exit_action)

        # Create the central widget
        central = myCentralWidget()
        self.setCentralWidget(central)
        self.active_panel = central

        # Set the geometry
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

    def config_parse(self, config_file):

        log.debug('Loading config file: {}'.format(config_file))

        cfg = configparser.RawConfigParser()
        cfg.read("{}".format(config_file))

        self.active_panel.basename(cfg.get('image', 'basename'))
        self.active_panel.comment(cfg.get('image', 'comment'))
        self.active_panel.path(cfg.get('image', 'dir'))
        self.active_panel.target_name(cfg.get('image', 'title'))

        index = self.active_panel.obs_type.combo_box.findText(
            cfg.get('image', 'type'), QtCore.Qt.MatchFixedString
        )
        if index >= 0:
            self.active_panel.obs_type.combo_box.setCurrentIndex(index)

        self.active_panel.exp_time(cfg.getfloat('obs', 'exptime'))
        self.active_panel.n_frames(cfg.getint('obs', 'nframes'))

        scan_page = self.active_panel.scan_page
        scan_page.scan_id(cfg.get('scan', 'id'))
        scan_page.n_channels(cfg.getint('scan', 'nchannels'))
        scan_page.n_sweeps(cfg.getint('scan', 'nsweeps'))
        scan_page.z_start(cfg.getint('scan', 'zstart'))
        scan_page.z_step(cfg.getfloat('scan', 'zstep'))
        scan_page.sleep_time(cfg.getfloat('scan', 'stime'))

        self.active_panel.notebook.setCurrentIndex(
            cfg.getint('gui', 'active_page')
        )

        if cfg.getboolean('calib', 'low_res_fabry_perot'):
            self.active_panel.calib_page.fp_low_res_rb.setChecked(True)
        else:
            self.active_panel.calib_page.fp_high_res_rb.setChecked(True)


    def config_generate(self):

        cfg = configparser.RawConfigParser()
        cfg.add_section('image')
        cfg.set('image', 'basename', self.active_panel.basename())
        cfg.set('image', 'comment', self.active_panel.comment())
        cfg.set('image', 'dir', self.active_panel.path())
        cfg.set('image', 'type',
                self.active_panel.obs_type.combo_box.currentText())
        cfg.set('image', 'title', self.active_panel.target_name())

        cfg.add_section('obs')
        cfg.set('obs', 'exptime', self.active_panel.exp_time())
        cfg.set('obs', 'nframes', self.active_panel.n_frames())

        cfg.add_section('scan')
        cfg.set('scan', 'id', self.active_panel.scan_page.scan_id())
        cfg.set('scan', 'nchannels', self.active_panel.scan_page.n_channels())
        cfg.set('scan', 'nsweeps', self.active_panel.scan_page.n_sweeps())
        cfg.set('scan', 'stime', self.active_panel.scan_page.sleep_time())
        cfg.set('scan', 'zstart', self.active_panel.scan_page.z_start())
        cfg.set('scan', 'zstep', self.active_panel.scan_page.z_step())

        cfg.add_section('gui')
        cfg.set('gui', 'active_page', self.active_panel.notebook.currentIndex())

        cfg.add_section('calib')
        cfg.set('calib', 'low_res_fabry_perot',
                self.active_panel.calib_page.fp_low_res_rb.isChecked())

        return cfg

    def get_exit_action(self):
        exit_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/exit-to-app.png'))
            ,'&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        return exit_action

    def get_load_action(self):
        load_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/file-import.png')),
            'Open', self)
        load_action.setShortcut('Ctrl+O')
        load_action.setStatusTip('Load config file.')
        load_action.triggered.connect(self.load_config_file)
        return load_action

    def get_save_action(self):
        save_action = QtGui.QAction(
            QtGui.QIcon(os.path.join(root, 'samfp/icons/content-save.png')),
            'Open', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save config file.')
        save_action.triggered.connect(self.save_config_file)
        return save_action


    def keyPressEvent(self, e):

        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

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
            except configparser.NoSectionError as error:
                log.warning("{}".format(error.section) + \
                            "section not found in the input config file")
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


class myCentralWidget(QtGui.QFrame):

    def __init__(self):
        super(myCentralWidget, self).__init__()
        self.initUI()

    def initUI(self):

        # Initialize widgets ---
        self.basename = myLineEdit("Basename: ", "samfp_scan")
        self.path = myLineEdit("Remote path:", "/home2/images/SAMFP/")
        self.target_name = myLineEdit("Target name:", "NGC0000")
        self.comment = myLineEdit("Comment:", "---")
        self.obs_type = myComboBox("Observation type: ",
                                   ["DARK", "DFLAT", "OBJECT", "SFLAT", "ZERO"])

        self.exp_time = myLineEdit_Float("Exposure time [s]:", 1.0)
        self.n_frames = myLineEdit_Int("Frames per channel:", 1)

        self.scan = QtGui.QPushButton("Scan")
        self.abort = QtGui.QPushButton("Abort")
        self.progress = QtGui.QProgressBar()

        self.abort.setDisabled(True)
        self.progress.setDisabled(True)

        self.scan_page = PageScan()

        self.notebook = QtGui.QTabWidget()
        self.calib_page = PageCalibrationScan()
        self.sci_page = PageScienceScan()

        # Put some in the left part of the GUI ---------------------------------
        left_group = QtGui.QGroupBox()

        left_grid = QtGui.QGridLayout()
        left_grid.setSpacing(3)

        left_grid.addWidget(self.basename.label, 0, 0)
        left_grid.addWidget(self.basename.line_edit, 1, 0, 1, 3)

        left_grid.addWidget(self.path.label, 2, 0)
        left_grid.addWidget(self.path.line_edit, 3, 0, 1, 3)

        left_grid.addWidget(self.HLine(), 4, 0, 1, 3)

        left_grid.addWidget(self.obs_type.label, 5, 0)
        left_grid.addWidget(self.obs_type.combo_box, 5, 1)

        left_grid.addWidget(self.target_name.label, 6, 0)
        left_grid.addWidget(self.target_name.line_edit, 6, 1)

        left_grid.addWidget(self.comment.label, 7, 0)
        left_grid.addWidget(self.comment.line_edit, 7, 1)

        left_grid.addWidget(self.HLine(), 8, 0, 1, 2)

        left_grid.addWidget(self.exp_time.label, 9, 0)
        left_grid.addWidget(self.exp_time.line_edit, 9, 1)

        left_grid.addWidget(self.n_frames.label, 10, 0)
        left_grid.addWidget(self.n_frames.line_edit, 10, 1)

        left_grid.addWidget(self.scan_page, 11, 0, 1, 2)

        left_grid.setAlignment(QtCore.Qt.AlignLeft)
        left_group.setLayout(left_grid)

        # Put others in the bottom of the GUI ----------------------------------
        bottom_group = QtGui.QGroupBox()

        bottom_grid = QtGui.QGridLayout()
        bottom_grid.setSpacing(3)

        bottom_grid.addWidget(self.scan, 10, 0)
        bottom_grid.addWidget(self.abort, 10, 1)
        bottom_grid.addWidget(self.progress, 10, 2)

        bottom_group.setLayout(bottom_grid)

        # Put others in the notebook on the right ------------------------------
        # self.notebook.addTab(self.scan_page, "Simple Scan")
        self.notebook.addTab(self.calib_page, "Calibration Scan")
        self.notebook.addTab(self.sci_page, "Science Scan")

        # Put all of them in the main grid -------------------------------------
        main_grid = QtGui.QGridLayout()
        main_grid.setSpacing(5)

        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(self.notebook, 0, 1)
        main_grid.addWidget(self.HLine(), 1, 0, 1, 2)
        main_grid.addWidget(bottom_group, 2, 0, 1, 2)

        self.setLayout(main_grid)

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto


class myComboBox(QtGui.QWidget):

    def __init__(self, label, options):

        super(myComboBox, self).__init__()

        self.label = QtGui.QLabel(label)
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(options)


class myLineEdit(QtGui.QWidget):

    def __init__(self, label, value):
        """
        Initialize field that contains a label (QtGui.QLabel) and a text field
         (QtGui.QLineEdit).

        Parameters
        ----------
        label (string) : the field label
        text (string) : the text that will be inside the text box
        """
        super(myLineEdit, self).__init__()

        self.button = None
        self.label = QtGui.QLabel(label)
        self.line_edit = QtGui.QLineEdit(value)
        self.line_edit.setAlignment(QtCore.Qt.AlignRight)
        self._value = value

    def __call__(self, x=None):
        if x is None:
            x = self.line_edit.text()
            return x
        else:
            self.line_edit.setText(x)
            self._value = x

    def add_button(self, label):
        self.button = QtGui.QPushButton(label)

class myLineEdit_Int(myLineEdit):

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
        number = int(number)

        super(myLineEdit_Int, self).__init__(label, "{:d}".format(number))
        self._value = number

    def __call__(self, x=None):
        if x is None:
            x = self.line_edit.text()
            x = int(x)
            return x
        else:
            x = int(x)
            self.line_edit.setText("{:d}".format(x))
            self._value = x


class myLineEdit_Float(myLineEdit):

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
        number = float(number)

        super(myLineEdit_Float, self).__init__(label, "{:.1f}".format(number))
        self._value = number

    def __call__(self, x=None):
        if x is None:
            x = self.line_edit.text()
            x = float(x)
            return x
        else:
            assert (isinstance(x, int) or isinstance(x, float))
            x = float(x)
            self.line_edit.setText("{:.1f}".format(x))
            self._value = x


class PageScan(QtGui.QWidget):
    def __init__(self):
        super(PageScan, self).__init__()

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.scan_id = myLineEdit("Scan ID:", "")
        self.n_channels = myLineEdit_Int("Number of channels:", 1)
        self.n_sweeps = myLineEdit_Int("Number of sweeps:", 1)
        self.z_start = myLineEdit_Int("Z Start [bcv]:", 0)
        self.z_step = myLineEdit_Float("Z Step [bcv]:", 0)
        self.sleep_time = myLineEdit_Float("Sleep time [s]:", 0)

        self.scan_id.add_button("Get ID")
        self.scan_id.button.clicked.connect(self.get_id)
        self.scan_id.button.setMaximumWidth(50)
        self.scan_id.line_edit.setMinimumWidth(175)

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
        grid.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(grid)


    def get_id(self):
        now = datetime.datetime.now()
        s = now.strftime("SCAN_%Y%m%d_UTC%H%M%S")
        self.scan_id(s)


class PageCalibrationScan(QtGui.QWidget):
    def __init__(self):
        super(PageCalibrationScan, self).__init__()


class PageScienceScan(QtGui.QWidget):
    def __init__(self):
        super(PageScienceScan, self).__init__()

class PageCalibrationScan(QtGui.QWidget):

    def __init__(self):
        super(PageCalibrationScan, self).__init__()
        self.initUI()

    def initUI(self):

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        fp_grid = QtGui.QGridLayout()
        fp_grid.setSpacing(1)

        self.lamp = QtGui.QComboBox()
        self.lamp.addItems(
            ['Ne 6600']
        )

        self.fp = QtGui.QGroupBox("Fabry-Perot")

        self.fp_label = QtGui.QLabel("Fabry-Perot")
        self.fp_low_res_rb = QtGui.QRadioButton("Low-Resolution")
        self.fp_high_res_rb = QtGui.QRadioButton("High-Resolution")

        self.fp_order = myLineEdit_Int("Interference order at Ha:", 134)
        self.fp_gap_size = myLineEdit_Float("Gap size [um]:", 44)

        self.queensgate_constant = myLineEdit_Float(
            "Queensgate Constant [A/bcv]:", 0)
        self.finesse = myLineEdit_Float(
            "Finesse [--]:", 0)
        self.free_spectral_range = myLineEdit_Float(
            "Free Spectral Range [bcv]:", 0)

        self.queensgate_constant.add_button("Get")
        self.finesse.add_button("Get")

        #  Add all the widgets to the current layout --------------------------
        grid.addWidget(QtGui.QLabel('Lamp:'), 1, 0)
        grid.addWidget(self.lamp, 1, 1)

        grid.addWidget(self.fp, 2, 0, 3, 3)

        fp_grid.addWidget(self.fp_low_res_rb, 0, 0)
        fp_grid.addWidget(self.fp_high_res_rb, 1, 0)

        fp_grid.addWidget(self.fp_order.label, 2, 0)
        fp_grid.addWidget(self.fp_order.line_edit, 2, 1)

        fp_grid.addWidget(self.fp_gap_size.label, 3, 0)
        fp_grid.addWidget(self.fp_gap_size.line_edit, 3, 1)

        fp_grid.addWidget(self.queensgate_constant.label, 4, 0)
        fp_grid.addWidget(self.queensgate_constant.line_edit, 4, 1)
        fp_grid.addWidget(self.queensgate_constant.button, 4, 2)

        fp_grid.addWidget(self.finesse.label, 5, 0)
        fp_grid.addWidget(self.finesse.line_edit, 5, 1)
        fp_grid.addWidget(self.finesse.button, 5, 2)


        fp_grid.setAlignment(QtCore.Qt.AlignTop)
        self.fp.setLayout(fp_grid)

        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto

    def VLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.VLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    app.setStyle("cleanlooks")
    ex = Main()
    sys.exit(app.exec_())