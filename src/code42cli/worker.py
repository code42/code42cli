from threading import Thread, Lock

from code42cli.compat import queue
from code42cli.logger import get_error_logger


class Worker(object):
    def __init__(self, thread_count):
        self._queue = queue.Queue()
        self._thread_count = thread_count
        self._error_logger = get_error_logger()
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
            finally:
                self._queue.task_done()

    def __start(self):
        for _ in range(0, self._thread_count):
            t = Thread(target=self._process_queue)
            t.daemon = True
            t.start()
