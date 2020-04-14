import time

from code42cli.worker import Worker


class TestWorker(object):
    def test_is_async(self):
        worker = Worker(5)
        demo_ls = []

        def async_func():
            # Wait so that the line under `do_async` happens first, proving that it's async
            time.sleep(0.01)
            demo_ls.append(2)

        worker.do_async(async_func)
        demo_ls.append(1)
        worker.wait()
        assert demo_ls == [1, 2]
