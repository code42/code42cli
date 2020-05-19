import logging

from code42cli.worker import WorkerStats
from code42cli.progress_bar import ProgressBar


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
    
    # def test_update_logs_one_square_per_processed(self, caplog):
    #     stats = WorkerStats(100)
    #     bar = ProgressBar(stats)
    #     bar.update()
    #     with caplog.at_level(logging.INFO):
    #         assert (
    #             "\r----------------------------------------------------------------------------------------------------"
    #             in caplog.text
    #         )

