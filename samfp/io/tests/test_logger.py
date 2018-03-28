
import io
import logging
import unittest
import sys

from samfp.io.logging import get_logger


class TestLogFormat(unittest.TestCase):

    def setUp(self):
        self.held_stdout, sys.stdout = sys.stdout, io.StringIO()
        self.help_stderr, sys.stderr = sys.stderr, io.StringIO()

    def tearDown(self):
        sys.stdout = self.held_stdout
        sys.stderr = self.help_stderr

    def test_debug(self):

        logger = get_logger('TestLogApp')
        logger.debug("debug message")
        log_message = sys.stderr.getvalue().strip()

        self.assertRegex(log_message, r'(\[D\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    def test_info(self):
        logger = get_logger('TestLogApp')
        logger.info("info message")
        log_message = sys.stderr.getvalue().strip()

        self.assertRegex(log_message, r'(\[I\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    @unittest.skip
    def test_warning(self):
        logger = get_logger('TestLogApp')
        logger.warning("warning message")
        log_message = sys.stderr.getvalue().strip()

        self.assertRegex(log_message, r'(\[W\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    @unittest.skip
    def test_error(self):
        logger = get_logger('TestLogApp')
        logger.error("error message")
        log_message = sys.stderr.getvalue().strip()

        self.assertRegex(log_message, r'(\[E\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')

    @unittest.skip
    def test_critical(self):
        logger = get_logger('TestLogApp')
        logger.critical("critical message")
        log_message = sys.stderr.getvalue().strip()

        self.assertRegex(log_message, r'(\[C\s\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s\w*\]\s)')
