# -*- coding: utf-8 -*-

from code42cli.logger import get_main_cli_logger, get_progress_logger


class ProgressBar(object):
    _FILL = u"█"
    _LENGTH = 100

    def __init__(self, stats, logger=None):
        self._stats = stats
        self._logger = logger or get_progress_logger()

    def update(self):
        iteration = self._stats.total_processed
        bar = self._create_bar(iteration)
        stats_msg = self._create_stats_text()
        progress = u"{} {}".format(bar, stats_msg)
        self._logger.info(progress)

    def _create_bar(self, iteration):
        fill_length = self._calculate_fill_length(iteration)
        return self._FILL * fill_length + u"-" * (self._LENGTH - fill_length)

    def _calculate_fill_length(self, idx):
        filled_length = self._LENGTH * idx // self._stats.total
        return int(filled_length)

    def _create_stats_text(self):
        return u"{0} succeeded, {1} failed out of {2}.".format(
            self._stats.total_successes, self._stats.total_errors, self._stats.total
        )

    def clear_bar_and_print_results(self):
        clear = self._LENGTH * u" "
        self._logger.info(u"{}{}\n".format(self._create_stats_text(), clear))
        if self._stats.total_errors:
            get_main_cli_logger().print_errors_occurred_message()
