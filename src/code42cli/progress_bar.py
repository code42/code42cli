# -*- coding: utf-8 -*-

from code42cli.logger import get_progress_logger


class ProgressBar(object):
    _FILL = u"█"
    _LENGTH = 100

    def __init__(self, total_items, logger=None):
        self._total_items = total_items
        self._logger = logger or get_progress_logger()

    def update(self, iteration, message):
        bar = self._create_bar(iteration)
        progress = u"{}  {}".format(bar, message.strip())
        self._logger.info(progress)

    def _create_bar(self, iteration):
        fill_length = self._calculate_fill_length(iteration)
        return self._FILL * fill_length + u"-" * (self._LENGTH - fill_length)

    def _calculate_fill_length(self, idx):
        filled_length = int(self._LENGTH * idx // self._total_items)
        return filled_length

    def clear_bar_and_print_final(self, final_message):
        clear = (self._LENGTH + len(final_message)) * u" "
        self._logger.info(u"{}{}\n".format(final_message, clear))
