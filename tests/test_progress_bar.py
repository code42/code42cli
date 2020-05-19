# -*- coding: utf-8 -*-

import logging

from code42cli.worker import WorkerStats
from code42cli.progress_bar import ProgressBar
from code42cli.logger import get_view_exceptions_location_message


class TestProgressBar(object):
    def test_update_when_zero_processed_logs_blank_line(self, caplog):
        stats = WorkerStats(100)
        bar = ProgressBar(stats)
        bar.update()
        with caplog.at_level(logging.INFO):
            assert (
                "\r----------------------------------------------------------------------------------------------------"
                in caplog.text
            )

    def test_update_logs_one_square_per_processed(self, caplog):
        stats = WorkerStats(100)
        stats._total_processed = 50
        bar = ProgressBar(stats)
        bar.update()
        with caplog.at_level(logging.INFO):
            assert (
                "\r██████████████████████████████████████████████████--------------------------------------------------"
                in caplog.text
            )

    def test_clear_bar_and_print_results_when_errors_occur_prints_error_message(self, caplog):
        stats = WorkerStats(100)
        stats._total_errors = 50
        bar = ProgressBar(stats)
        bar.clear_bar_and_print_results()
        with caplog.at_level(logging.ERROR):
            assert get_view_exceptions_location_message() in caplog.text

    def test_clear_bar_and_print_results_when_no_errors_occur_does_not_print_error_message(
        self, caplog
    ):
        stats = WorkerStats(100)
        stats._total_errors = 0
        bar = ProgressBar(stats)
        bar.clear_bar_and_print_results()
        with caplog.at_level(logging.ERROR):
            assert get_view_exceptions_location_message() not in caplog.text

    def test_clear_bar_and_print_result_clears_progress_bar(self, caplog):
        stats = WorkerStats(100)
        stats._total_errors = 0
        bar = ProgressBar(stats)
        bar.clear_bar_and_print_results()
        with caplog.at_level(logging.INFO):
            assert "█" not in caplog.text
