
import io
import unittest
import sys

from samfp.io.logger import get_logger, SamFpLogger


class TestLogFormat(unittest.TestCase):

    def setUp(self):
        self.held_stdout, sys.stdout = sys.stdout, io.StringIO()
        self.held_stderr, sys.stderr = sys.stderr, io.StringIO()
        self.streamer = sys.stderr

    def tearDown(self):
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr

    def test_debug(self):

        logger = get_logger('TestLogFormatApp')
        logger.debug("debug message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\[D\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_info(self):
        logger = get_logger('TestLogFormatApp')
        logger.info("info message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\[I\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_warning(self):
        logger = get_logger('TestLogFormatApp')
        logger.warning("warning message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\[W\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_error(self):
        logger = get_logger('TestLogFormatApp')
        logger.error("error message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\[E\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_critical(self):
        logger = get_logger('TestLogFormatApp')
        logger.critical("critical message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\[C\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_color(self):
        logger = get_logger('TestLogFormatApp')
        logger.critical("critical message")
        log_message = self.streamer.getvalue().strip()

        self.assertRegex(log_message, r'(\x1b)')


class TestLogger(unittest.TestCase):

    log_name = 'TestLogger'

    def setUp(self):
        self.logger = get_logger(self.log_name, use_color=False)

        self.held_stdout, sys.stdout = sys.stdout, io.StringIO()
        self.held_stderr, sys.stderr = sys.stderr, io.StringIO()
        self.streamer = sys.stderr

    def test_instance(self):
        self.assertIsInstance(self.logger, SamFpLogger)

    def trigger_logger(self):
        self.logger.debug("debug message")
        self.logger.info("info message")
        self.logger.warning("warning message")
        self.logger.error("error message")
        self.logger.critical("critical message")

    def test_verbose(self):
        self.logger.set_verbose(True)

        with self.assertLogs(self.log_name, level='INFO') as cm:
            self.logger.info('info message')
            print(cm.output)

    @unittest.skip
    def test_debug(self):
        self.logger.set_debug(True)
        self.trigger_logger()

        self.logger.set_debug(False)
        self.trigger_logger()

    def tearDown(self):
        pass