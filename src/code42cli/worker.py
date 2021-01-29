import queue
from threading import Lock
from threading import Thread
from time import sleep

from py42.exceptions import Py42ForbiddenError
from py42.exceptions import Py42HTTPError

from code42cli.errors import Code42CLIError
from code42cli.logger import get_main_cli_logger


class WorkerStats:
    """Stats about the tasks that have run."""

    def __init__(self, total):
        self.total = total

    _total_processed = 0
    _total_errors = 0
    _results = []
    __total_processed_lock = Lock()
    __total_errors_lock = Lock()
    __results_lock = Lock()

    @property
    def total_processed(self):
        """The total number of tasks executed."""
        return self._total_processed

    @property
    def total_errors(self):
        """The amount of errors that occurred."""
        return self._total_errors

    @property
    def total_successes(self):
        val = self._total_processed - self._total_errors
        return val if val >= 0 else 0

    @property
    def results(self):
        return self._results

    def __str__(self):
        return "{} succeeded, {} failed out of {}".format(
            self.total_successes, self._total_errors, self.total
        )

    def increment_total_processed(self):
        """+1 to self.total_processed"""
        with self.__total_processed_lock:
            self._total_processed += 1

    def increment_total_errors(self):
        """+1 to self.total_errors"""
        with self.__total_errors_lock:
            self._total_errors += 1

    def add_result(self, result):
        """add a result to the list"""
        with self.__results_lock:
            self._results.append(result)

    def reset_results(self):
        with self.__results_lock:
            self._results = []


class Worker:
    def __init__(self, thread_count, expected_total, bar=None):
        self._queue = queue.Queue()
        self._thread_count = thread_count
        self._stats = WorkerStats(expected_total)
        self._tasks = 0
        self.__started = False
        self.__start_lock = Lock()
        self._logger = get_main_cli_logger()
        self._bar = bar

    def do_async(self, func, *args, **kwargs):
        """Execute the given func asynchronously given *args and **kwargs.

        Args:
            func (callable): The function to execute asynchronously.
            *args (iter): Positional args to pass to the function.
            **kwargs (dict): Key-value args to pass to the function.
        """
        if not self.__started:
            with self.__start_lock:
                if not self.__started:
                    self.__start()
                    self.__started = True
        self._queue.put({"func": func, "args": args, "kwargs": kwargs})
        self._tasks += 1

    @property
    def stats(self):
        """Stats about the tasks that have been executed, such as the total errors that occurred.
        """
        return self._stats

    def wait(self):
        """Wait for the tasks in the queue to complete. This should usually be called before
        program termination."""
        while self._stats.total_processed < self._tasks:
            sleep(0.5)

    def _process_queue(self):
        while True:
            try:
                task = self._queue.get()
                func = task["func"]
                args = task["args"]
                kwargs = task["kwargs"]
                self._stats.add_result(func(*args, **kwargs))
            except Code42CLIError as err:
                self._increment_total_errors()
                self._logger.log_error(err)
            except Py42ForbiddenError as err:
                self._increment_total_errors()
                self._logger.log_verbose_error(http_request=err.response.request)
                self._logger.log_error(
                    "You do not have the necessary permissions to perform this task. "
                    "Try using or creating a different profile."
                )
            except Py42HTTPError as err:
                self._increment_total_errors()
                self._logger.log_verbose_error(http_request=err.response.request)
            except Exception:
                self._increment_total_errors()
                self._logger.log_verbose_error()
            finally:
                self._stats.increment_total_processed()
                if self._bar:
                    self._bar.update(1)
                self._queue.task_done()

    def __start(self):
        for _ in range(0, self._thread_count):
            t = Thread(target=self._process_queue)
            t.daemon = True
            t.start()

    def _increment_total_errors(self):
        self._stats.increment_total_errors()
