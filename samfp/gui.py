# -*- coding: utf-8 -*-

from __future__ import print_function, division
from PyQt4 import QtCore, QtGui, Qt

import configparser
import datetime
import logging
import sys
import os
import time

import scan

logging.basicConfig()
log = logging.getLogger("samfp.scan")
log.setLevel(logging.DEBUG)

root = "/home/bquint/PycharmProjects/samfp/"

wavelength = {
        'Ha': 6562.78,
        'SIIf': 6716.47,
        'SIIF': 6730.85,
        'NIIf': 6548.03,
        'NIIF': 6583.41,
        'Ne 6600': 6598.9529
    }

class Main(QtGui.QMainWindow):

    config = {'temp_file': '.samfp_temp.ini'}

    def __init__(self):
        super(Main, self).__init__()
        self.initUI()

    def initUI(self):

        # Set the font of the ToolTip windows
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        # Create the status bar
        self.status_bar = self.statusBar()

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

        try:
            self.active_panel.basename(cfg.get('image', 'basename'))
            self.active_panel.comment(cfg.get('image', 'comment'))
            self.active_panel.path(cfg.get('image', 'dir'))
            self.active_panel.target_name(cfg.get('image', 'title'))

            idx = self.active_panel.obs_type.combo_box.findText(
                cfg.get('image', 'type'), QtCore.Qt.MatchFixedString
            )
            if idx >= 0:
                self.active_panel.obs_type.combo_box.setCurrentIndex(idx)

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

            # The calibration page ---
            idx = self.active_panel.calib_page.lamp.combo_box.findText(
                cfg.get('calib', 'lamp'), QtCore.Qt.MatchFixedString
            )
            if idx >= 0:
                self.active_panel.calib_page.lamp.combo_box.setCurrentIndex(idx)

            if cfg.getboolean('calib', 'low_res_fabry_perot'):
                self.active_panel.calib_page.fp_low_res_rb.setChecked(True)
            else:
                self.active_panel.calib_page.fp_high_res_rb.setChecked(True)

            self.active_panel.calib_page.fp_gap_size(
                cfg.getfloat('calib', 'gap_size')
            )
            self.active_panel.calib_page.fp_order(
                cfg.getfloat('calib', 'order')
            )
            self.active_panel.calib_page.queensgate_constant(
                cfg.getfloat('calib', 'queensgate_constant')
            )
            self.active_panel.calib_page.finesse(
                cfg.getfloat('calib', 'finesse')
            )
            self.active_panel.calib_page.free_spectral_range(
                cfg.getfloat('calib', 'free_spectral_range')
            )
            self.active_panel.calib_page.fwhm(
                cfg.getfloat('calib', 'fwhm')
            )
            self.active_panel.calib_page.oversample_factor(
                cfg.getfloat('calib', 'oversample_factor')
            )
            self.active_panel.calib_page.overscan_factor(
                cfg.getfloat('calib', 'overscan_factor')
            )


        except configparser.NoOptionError as error:
            log.warning("{}".format(error.option) + \
                        " option not found in the input config file")

        except configparser.NoSectionError as error:
            log.warning("{}".format(error.section) + \
                        " section not found in the input config file")

    def config_generate(self):

        cfg = configparser.RawConfigParser()
        cfg.add_section('image')
        cfg.set('image', 'basename', self.active_panel.basename())
        cfg.set('image', 'comment', self.active_panel.comment())
        cfg.set('image', 'dir', self.active_panel.path())
        cfg.set('image', 'title', self.active_panel.target_name())
        cfg.set('image', 'type',
                self.active_panel.obs_type.combo_box.currentText())

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
        if self.active_panel.calib_page.fp_low_res_rb.isChecked():
            cfg.set('calib', 'low_res_fabry_perot', True)
        else:
            cfg.set('calib', 'low_res_fabry_perot', False)

        cfg.set('calib', 'lamp',
                self.active_panel.calib_page.lamp.combo_box.currentText())
        cfg.set('calib', 'order',
                self.active_panel.calib_page.fp_order())
        cfg.set('calib', 'gap_size',
                self.active_panel.calib_page.fp_gap_size())
        cfg.set('calib', 'queensgate_constant',
                self.active_panel.calib_page.queensgate_constant())
        cfg.set('calib', 'finesse',
                self.active_panel.calib_page.finesse())
        cfg.set('calib', 'free_spectral_range',
                self.active_panel.calib_page.free_spectral_range())
        cfg.set('calib', 'fwhm',
                self.active_panel.calib_page.fwhm())
        cfg.set('calib', 'oversample_factor',
                self.active_panel.calib_page.oversample_factor())
        cfg.set('calib', 'overscan_factor',
                self.active_panel.calib_page.overscan_factor())

        # cfg.add_section('science')
        # cfg.set('science', 'low_res_fabry_perot',
        #         self.active_panel.sci_page.fp_low_res_rb.isChecked())

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
            self.config_parse(self.config['temp_file'])
        else:
            log.debug('Temp config file does not exists.')

    def save_config_file(self):
        """Save a new configuration file"""
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save', os.getcwd())
        fname = str(fname)

        temp_config = self.config_generate()
        with open(fname, 'w') as foo:
            temp_config.write(foo)

    def save_temp_file(self):
        """Save a temporary file for persistance"""
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
        self.obs_type = MyComboBox("Observation type: ",
                                   ["DARK", "DFLAT", "OBJECT", "SFLAT", "ZERO"])

        self.exp_time = myLineEdit_Float("Exposure time [s]:", 1.0)
        self.n_frames = myLineEdit_Int("Frames per channel:", 1)

        self.scan_button = QtGui.QPushButton("Scan")
        self.abort_button = QtGui.QPushButton("Abort")
        self.progress_bar = QtGui.QProgressBar()

        self.scan_page = PageScan()

        self.notebook = QtGui.QTabWidget()
        self.calib_page = PageCalibrationScan()
        self.sci_page = PageScienceScan()

        self.set_scan_button = QtGui.QPushButton("Set scan parameters")

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

        bottom_grid.addWidget(self.scan_button, 10, 0)
        bottom_grid.addWidget(self.abort_button, 10, 1)
        bottom_grid.addWidget(self.progress_bar, 10, 2)

        bottom_group.setLayout(bottom_grid)

        # Put others in the notebook on the right ------------------------------
        self.notebook.addTab(self.calib_page, "Calibration Scan")
        self.notebook.addTab(self.sci_page, "Science Scan")

        # Put all of them in the main grid -------------------------------------
        main_grid = QtGui.QGridLayout()
        main_grid.setSpacing(5)

        main_grid.addWidget(left_group, 0, 0, 2, 1)
        main_grid.addWidget(self.notebook, 0, 1)
        main_grid.addWidget(self.set_scan_button, 1, 1)
        main_grid.addWidget(self.HLine(), 2, 0, 1, 2)
        main_grid.addWidget(bottom_group, 3, 0, 1, 2)

        self.setLayout(main_grid)

        # Add the thread for the scan ------------------------------------------
        self.scan_button.setEnabled(True)
        self.abort_button.setDisabled(True)
        self.progress_bar.setDisabled(True)

        self.timer = QtCore.QBasicTimer()
        self.step = 0

        self.scan_button.clicked.connect(self.scan_start)
        self.abort_button.clicked.connect(self.scan_abort)
        self.set_scan_button.clicked.connect(self.set_scan_pars)


    def scan_abort(self):

        self.timer.stop()
        self.scan_button.setEnabled(True)
        self.abort_button.setDisabled(True)
        self.progress_bar.setDisabled(True)
        self.step = 0

    def scan_start(self):

        self.current_sweep = 1
        self.current_channel = 1
        self.z = self.scan_page.z_start()

        self.total_sweeps = self.scan_page.n_sweeps()
        self.total_channels = self.scan_page.n_channels()
        self.total_steps = self.total_channels * self.total_sweeps
        self.step_fraction = 1. / self.total_steps * 100

        self.timer.start(50, self)
        self.scan_button.setDisabled(True)
        self.abort_button.setEnabled(True)
        self.progress_bar.setEnabled(True)

        scan.set_image_path(self.path())
        scan.set_image_basename(self.basename())

        scan.set_image_type(self.obs_type())
        scan.set_target_name(self.target_name())
        scan.set_comment(self.comment())
        scan.set_image_nframes(self.n_frames())
        scan.set_image_exposure_time(self.exp_time())

        scan.set_scan_id(self.scan_page.scan_id())
        scan.set_scan_start(self.scan_page.z_start())
        scan.set_scan_nchannels(self.scan_page.n_channels())

        self.z = self.scan_page.z_start()
        self.current_sweep = 1
        self.current_channel = 1

    def set_scan_pars(self):

        # For calibration cube
        if self.notebook.currentIndex() == 0:

            overscan_factor = self.calib_page.overscan_factor()
            oversample_factor = self.calib_page.oversample_factor()

            n_channels = 2 * self.calib_page.finesse()
            z_step = self.calib_page.fwhm() / oversample_factor

        else:

            oversample_factor = 0
            overscan_factor = 0

            n_channels = 0
            zstep = 0

        n_channels = round(overscan_factor * n_channels)

        self.scan_page.n_channels(n_channels)
        self.scan_page.z_step(- z_step)


    def timerEvent(self, e):

        if self.step >= 100:
            self.timer.stop()
            self.scan_abort()
            return

        if self.z < 0 or self.z > 4095:
            self.timer.stop()
            self.scan_abort()

        log.debug("Sweep: {}, Channel {}, Z {}".format(
            self.current_sweep, self.current_channel, self.z))

        scan.set_scan_current_z(int(round(self.z)))
        scan.set_scan_current_sweep(self.current_sweep)

        time.sleep(self.scan_page.sleep_time())
        scan.expose()

        self.step += self.step_fraction
        self.progress_bar.setValue(self.step)

        self.current_channel += 1
        self.z += self.scan_page.z_step()

        if self.current_channel > self.total_channels:
            self.current_channel = 1
            self.current_sweep += 1
            self.z = self.scan_page.z_start()

    def HLine(self):
        toto = QtGui.QFrame()
        toto.setFrameShape(QtGui.QFrame.HLine)
        toto.setFrameShadow(QtGui.QFrame.Sunken)
        return toto


class MyComboBox(QtGui.QWidget):

    def __init__(self, label, options):

        super(MyComboBox, self).__init__()

        self.label = QtGui.QLabel(label)
        self.combo_box = QtGui.QComboBox()
        self.combo_box.addItems(options)

    def __call__(self):

        return str(self.combo_box.currentText())


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


class myProgressBar(QtGui.QProgressBar):
    def __init__(self, parent=None):
        super(myProgressBar, self).__init__(parent)

        # Set up the user interface from Designer.
        self.setValue(0)

        self.thread = mythread(self, 3)

        self.thread.total.connect(self.setMaximum)
        self.thread.update.connect(self.update)
        self.thread.finished.connect(self.close)

        self.n = 0
        self.thread.start()

    def update(self):
        self.n += 1
        print
        self.n
        self.setValue(self.n)


class mythread(QtCore.QThread):

    total = QtCore.pyqtSignal(object)
    update = QtCore.pyqtSignal()

    def __init__(self, parent, n):
        super(mythread, self).__init__(parent)
        self.n = n

    def run(self):
        self.total.emit(self.n)
        i = 0
        while (i < self.n):
            if (time.time() % 1 == 0):
                i += 1
                # print str(i)
                self.update.emit()


class PageScan(QtGui.QWidget):
    def __init__(self):
        super(PageScan, self).__init__()

        grid = QtGui.QGridLayout()
        grid.setSpacing(5)

        self.scan_id = myLineEdit("Scan ID:", "")
        self.n_channels = myLineEdit_Int("Number of channels:", 1)
        self.n_sweeps = myLineEdit_Int("Number of sweeps:", 1)
        self.z_start = myLineEdit_Int("Z Start [bcv]:", 1024)
        self.z_step = myLineEdit_Float("Z Step [bcv]:", 0)
        self.sleep_time = myLineEdit_Float("Sleep time [s]:", 0)

        self.scan_id.add_button("Get ID")
        self.scan_id.button.clicked.connect(self.get_id)
        self.scan_id.line_edit.setMinimumWidth(200)

        grid.addWidget(self.scan_id.label, 0, 0)
        grid.addWidget(self.scan_id.line_edit, 1, 0)
        grid.addWidget(self.scan_id.button, 1, 1)

        grid.addWidget(self.n_channels.label, 2, 0)
        grid.addWidget(self.n_channels.line_edit, 2, 1)

        grid.addWidget(self.n_sweeps.label, 3, 0)
        grid.addWidget(self.n_sweeps.line_edit, 3, 1)

        grid.addWidget(self.z_start.label, 4, 0)
        grid.addWidget(self.z_start.line_edit, 4, 1)

        grid.addWidget(self.z_step.label, 5, 0)
        grid.addWidget(self.z_step.line_edit, 5, 1)

        grid.addWidget(self.sleep_time.label, 6, 0)
        grid.addWidget(self.sleep_time.line_edit, 6, 1)

        grid.setAlignment(QtCore.Qt.AlignTop)
        grid.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(grid)


    def get_id(self):
        now = datetime.datetime.now()
        s = now.strftime("SCAN_%Y%m%d_UTC%H%M%S")
        self.scan_id(s)


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
        fp_grid.setSpacing(5)

        self.lamp = MyComboBox("Lamp: ", wavelength.keys())

        self.fp = QtGui.QGroupBox("Fabry-Perot")

        self.fp_label = QtGui.QLabel("Fabry-Perot")
        self.fp_low_res_rb = QtGui.QRadioButton("Low-Resolution")
        self.fp_high_res_rb = QtGui.QRadioButton("High-Resolution")

        self.fp_order = myLineEdit_Float("Interference order at Ha:", 0)
        self.fp_gap_size = myLineEdit_Float("Gap size [um]:", 0)

        self.queensgate_constant = myLineEdit_Float(
            "Queensgate Constant [A / bcv]:", 0)
        self.finesse = myLineEdit_Float(
            "Finesse [--]:", 0)
        self.free_spectral_range = myLineEdit_Float(
            "Free Spectral Range [bcv]:", 0)
        self.fwhm = myLineEdit_Float(
            "Full-width at half-maximum [bcv]:", 0)

        self.sampling = myLineEdit_Float(
            "Sampling [bcv / step]:", 1)

        self.oversample_factor = myLineEdit_Float(
            "Oversample factor:", 1)
        self.overscan_factor = myLineEdit_Float(
            "Overscan factor:", 1)

        self.queensgate_constant.add_button("Get")
        self.finesse.add_button("Get")

        key = str(self.lamp.combo_box.currentText())
        self.wavelength = wavelength[key]

        #  Add all the widgets to the current layout --------------------------
        fp_grid.addWidget(self.fp_low_res_rb, 0, 0)
        fp_grid.addWidget(self.fp_high_res_rb, 1, 0)

        grid.addWidget(self.lamp.label, 0, 0)
        grid.addWidget(self.lamp.combo_box, 0, 1)

        grid.addWidget(self.fp, 1, 0, 2, 3)

        grid.addWidget(self.fp_order.label, 3, 0)
        grid.addWidget(self.fp_order.line_edit, 3, 1)

        grid.addWidget(self.fp_gap_size.label, 4, 0)
        grid.addWidget(self.fp_gap_size.line_edit, 4, 1)

        grid.addWidget(self.queensgate_constant.label, 5, 0)
        grid.addWidget(self.queensgate_constant.line_edit, 5, 1)
        grid.addWidget(self.queensgate_constant.button, 5, 2)

        grid.addWidget(self.finesse.label, 6, 0)
        grid.addWidget(self.finesse.line_edit, 6, 1)
        grid.addWidget(self.finesse.button, 6, 2)

        grid.addWidget(self.free_spectral_range.label, 7, 0)
        grid.addWidget(self.free_spectral_range.line_edit, 7, 1)

        grid.addWidget(self.fwhm.label, 8, 0)
        grid.addWidget(self.fwhm.line_edit, 8, 1)

        grid.addWidget(self.HLine(), 9, 0, 1, 3)

        grid.addWidget(self.oversample_factor.label, 10, 0)
        grid.addWidget(self.oversample_factor.line_edit, 10, 1)

        grid.addWidget(self.overscan_factor.label, 11, 0)
        grid.addWidget(self.overscan_factor.line_edit, 11, 1)

        fp_grid.setAlignment(QtCore.Qt.AlignTop)
        self.fp.setLayout(fp_grid)

        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)

        # Connect handlers -----------------------------------------------------
        self.fp_low_res_rb.setChecked(True)
        self.set_fp_pars()

        self.fp_low_res_rb.clicked.connect(self.set_fp_pars)
        self.fp_high_res_rb.clicked.connect(self.set_fp_pars)

        self.lamp.combo_box.currentIndexChanged.connect(self.on_lamp_change)

        self.queensgate_constant.button.clicked.connect(
            self.get_queensgate_constant)
        self.finesse.button.clicked.connect(
            self.get_finesse)

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

    def get_finesse(self):
        """
        Use the current FSR and FWHM to calculate and set the Finesse.
        """
        try:
            self.finesse(calc_finesse(self.free_spectral_range(), self.fwhm()))

        except ZeroDivisionError as error:
            main_widget = self.window()
            main_widget.status_bar.showMessage(
                "Error: Zero division while calculating the Finesse."
            )

    def get_queensgate_constant(self):
        """
        Use the current wavelength and the free-spectral-range to calculate
        and set the Queensgate Constant.
        """
        w = wavelength[self.lamp()]
        FSR = self.free_spectral_range()

        try:
            QGC = calc_queensgate_constant(w, FSR)
            self.queensgate_constant(QGC)

        except ZeroDivisionError as error:

            page_widget = self.parent()
            tab_widget = page_widget.parent()
            central_widget = tab_widget.parent()
            main_widget = central_widget.parent()

            main_widget.status_bar.showMessage(
                "Error: Zero division while calculating the Queensgate "
                "Constant."
            )

    def on_lamp_change(self):
        """
        Does nothing for now. Check with Philippe if he wants this to deppend on
        the source wavelength or not.
        """
        return

    def set_fp_pars(self):

        if self.fp_low_res_rb.isChecked():
            gap_size = 44.
        else:
            gap_size = 200.

        self.fp_gap_size(gap_size)
        self.fp_order(calc_order(wavelength[self.lamp()], gap_size))


def calc_order(wavelength, gap_size):
    """
    Returns the FP interferential order.

    Parameters
    ----------
    wavelength (float):
    gap_size (float):

    Returns
    -------
    order (float)
    """
    return 2 * (gap_size * 1e-6) / (wavelength * 1e-10)


def calc_finesse(FSR, FWHM):
    """
    Returns the FP Finesse.

    Parameters
    ----------
    FSR (float) : free-spectral-range in BCV or A
    FWHM (float) : full-width-at-half-maximum in BCV or A

    Returns
    -------
    F (float) : the finesse

    Observations
    ------------
    Both FSR and FWHM have to have same units.
    """
    return float(FSR) / float(FWHM)


def calc_queensgate_constant(wavelength, free_spectra_range_bcv):
    """
    Returns the Fabry-Perot's Queensgate Constant.

    Parameters
    ----------
    wavelength (float):
    free_spectra_range_bcv (float):


    Returns
    -------
    queensgate_constant (float) :
    """
    return wavelength / free_spectra_range_bcv


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    #app.setStyle("cleanlooks")
    ex = Main()
    sys.exit(app.exec_())