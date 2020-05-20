# -*- coding: utf-8 -*-

import logging

from code42cli.progress_bar import ProgressBar


class TestProgressBar(object):
    def test_update_when_zero_processed_logs_zero_blocks(self, caplog):
        bar = ProgressBar(100)
        bar.update(0, "MESSAGE")
        with caplog.at_level(logging.INFO):
            assert u"█" not in caplog.text
            assert "MESSAGE" in caplog.text

    def test_update_logs_one_block_per_processed(self, caplog):
        bar = ProgressBar(100)
        bar.update(50, "MESSAGE")
        with caplog.at_level(logging.INFO):
            assert u"█" * 50 in caplog.text
            assert "MESSAGE" in caplog.text

    def test_clear_bar_and_print_result_clears_progress_bar(self, caplog):
        bar = ProgressBar(100)
        bar.clear_bar_and_print_final("MESSAGE")
        with caplog.at_level(logging.INFO):
            assert u"█" not in caplog.text
            assert "MESSAGE" in caplog.text
