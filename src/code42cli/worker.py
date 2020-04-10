import traceback
from threading import Thread, Lock

from code42cli.compat import queue
from code42cli.util import print_error


class Worker(object):
    def __init__(self, thread_count):
        self._queue = queue.Queue()
        self._thread_count = thread_count
        self.__started = False
        self.__start_lock = Lock()

    def do_async(self, func, *args, **kwargs):
        if not self.__started:
            with self.__start_lock:
                if not self.__started:
                    self.__start()
                    self.__started = True
        self._queue.put({u"func": func, u"args": args, u"kwargs": kwargs})

    def wait(self):
        self._queue.join()

    def _process_queue(self):
        while True:
            try:
                task = self._queue.get()
                func = task[u"func"]
                args = task[u"args"]
                kwargs = task[u"kwargs"]
                func(*args, **kwargs)
            except Exception:
                trace = traceback.format_exc()
                print_error(u"Failed to process row. Trace: {0}".format(trace))
            finally:
                self._queue.task_done()

    def __start(self):
        for _ in range(0, self._thread_count):
            t = Thread(target=self._process_queue)
            t.daemon = True
            t.start()
