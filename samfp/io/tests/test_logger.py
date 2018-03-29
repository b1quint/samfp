
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
