# -*- coding: utf-8 -*-

import sys, logging

from code42cli.logger import (
    logger_has_handlers,
    logger_deps_lock,
    get_standard_formatter,
    add_handler_to_logger,
    get_main_cli_logger,
)


def get_logger_for_progress_bar():
    logger = logging.getLogger(u"code42cli_progress_bar")
    if logger_has_handlers(logger):
        return logger

    with logger_deps_lock:
        if not logger_has_handlers(logger):
            handler = InPlaceStreamHandler()
            formatter = get_standard_formatter()
            logger.setLevel(logging.INFO)
            return add_handler_to_logger(logger, handler, formatter)
    return logger


class InPlaceStreamHandler(logging.StreamHandler):
    def __init__(self):
        super(InPlaceStreamHandler, self).__init__(sys.stdout)
        self.terminator = u"\r"


class ProgressBar(object):
    _FILL = u"█"
    _LENGTH = 100

    def __init__(self, stats, logger=None):
        self._stats = stats
        self._logger = logger or get_logger_for_progress_bar()
        self._logger.terminator = u"\r"

    def update(self):
        iteration = self._stats.total_processed
        bar = self._create_bar(iteration)
        stats_msg = self._create_stats_text()
        progress = u"\r{} {}".format(bar, stats_msg)
        self._logger.info(progress)

    def _create_bar(self, iteration):
        fill_length = self._calculate_fill_length(iteration)
        return self._FILL * fill_length + u"-" * (self._LENGTH - fill_length)

    def _calculate_fill_length(self, idx):
        filled_length = self._LENGTH * idx // self._stats.total
        # if filled_length * self._LATENCY < self._LENGTH:
        #     filled_length *= self._LATENCY
        return int(filled_length)

    def _create_stats_text(self):
        return u"{0} succeeded, {1} failed out of {2}.".format(
            self._stats.total_successes, self._stats.total_errors, self._stats.total
        )

    def clear_bar_and_print_results(self):
        clear = self._LENGTH * u" "
        self._logger.info(u"\r{}{}\n".format(self._create_stats_text(), clear))
        if self._stats.total_errors:
            get_main_cli_logger().print_errors_occurred_message()
