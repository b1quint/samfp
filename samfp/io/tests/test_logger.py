
import io
import logging
import unittest

from samfp.io.logging import get_logger, SamFpLogFormatter


class TestLogging(unittest.TestCase):

    def test_debug(self):
        logger = get_logger('TestLogApp')
        logger.debug('debug message')

    def test_info(self):
        logger = get_logger('TestLogApp')
        logger.info('info message')

    def test_warning(self):
        logger = get_logger('TestLogApp')
        logger.warning('warning message')

    def test_error(self):
        logger = get_logger('TestLogApp')
        logger.error('error message')

    def test_critical(self):
        logger = get_logger('TestLogApp')
        logger.critical('critical message')