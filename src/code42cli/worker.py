from threading import Thread, Lock

from code42cli.compat import queue
from code42cli.logger import get_error_logger


class WorkerStats(object):
    """Stats about the tasks that have run."""

    _total = 0
    _total_errors = 0
    __total_lock = Lock()
    __total_errors_lock = Lock()

    @property
    def total(self):
        """The total number of tasks executed."""
        return self._total

    @property
    def total_errors(self):
        """The amount of errors that occurred."""
        return self._total_errors

    def increment_total(self):
        """+1 to self.total"""
        with self.__total_lock:
            self._total += 1

    def increment_total_errors(self):
        """+1 to self.total_errors"""
        with self.__total_errors_lock:
            self._total_errors += 1


class Worker(object):
    def __init__(self, thread_count):
        self._queue = queue.Queue()
        self._thread_count = thread_count
        self._error_logger = get_error_logger()
        self._stats = WorkerStats()
        self.__started = False
        self.__start_lock = Lock()

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
        self._queue.put({u"func": func, u"args": args, u"kwargs": kwargs})

    @property
    def stats(self):
        """Stats about the tasks that have been executed, such as the total errors that occurred.
        """
        return self._stats

    def wait(self):
        """Wait for the tasks in the queue to complete. This should usually be called before 
        program termination."""
        self._queue.join()

    def _process_queue(self):
        while True:
            try:
                task = self._queue.get()
                func = task[u"func"]
                args = task[u"args"]
                kwargs = task[u"kwargs"]
                func(*args, **kwargs)
            except Exception as ex:
                self._error_logger.error(ex)
                self._stats.increment_total_errors()
            finally:
                self._stats.increment_total()
                self._queue.task_done()

    def __start(self):
        for _ in range(0, self._thread_count):
            t = Thread(target=self._process_queue)
            t.daemon = True
            t.start()
