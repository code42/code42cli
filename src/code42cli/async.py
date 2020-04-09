import traceback
from threading import Thread, Lock

from code42cli.compat import queue


class WorkerGroup(object):
    def __init__(self, handlers):
        self._worker_cache = {}
        self._worker_lock = Lock()
        self._handlers = handlers

    def add_and_get_worker(self, guid):
        worker = self._worker_cache.get(guid)
        if worker:
            return worker

        with self._worker_lock:
            worker = self._worker_cache.get(guid)
            if worker:
                return worker
            new_worker = Worker(4, self._handlers)
            self._worker_cache.update({guid: new_worker})
            return new_worker

    def wait_all(self):
        for guid in self._worker_cache:
            worker = self._worker_cache[guid]
            worker.wait()


class Worker(object):
    def __init__(self, thread_count, handlers):
        self._queue = queue.Queue()
        self._thread_count = thread_count
        self.__started = False
        self.__start_lock = Lock()
        self._handlers = handlers

    def do_async(self, func, *args, **kwargs):
        if not self.__started:
            with self.__start_lock:
                if not self.__started:
                    self.__start()
                    self.__started = True
        self._queue.put({"func": func, "args": args, "kwargs": kwargs})

    def wait(self):
        self._queue.join()
        self.__started = False

    def _process_queue(self):
        while True:
            try:
                task = self._queue.get()
                func = task["func"]
                args = task["args"]
                kwargs = task["kwargs"]
                func(*args, **kwargs)
            except Exception:
                trace = traceback.format_exc()
                self._handlers.handle_error(trace)
            finally:
                self._queue.task_done()

    def __start(self):
        for _ in range(0, self._thread_count):
            t = Thread(target=self._process_queue)
            t.daemon = True
            t.start()
