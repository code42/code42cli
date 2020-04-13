from code42cli.worker import Worker


class TestWorker(object):
    def test_is_async(self):
        # This test starts a thread that waits for the main thread to add an element to list,
        # then it adds an item to list right after. The fact that the new thread waits for the main
        # thread proves it's existence and the fact that it does busy-waiting proves that it's
        # parallel.
        worker = Worker(5)
        test_limit = 100
        demo_ls = []

        def async_func():
            i = 0
            # Wait until the line below `do_async` adds an item to `demo_ls`.
            while demo_ls == [] and i < test_limit:
                i += 1

            # This is to prevent infinite loops.
            if i == test_limit:
                assert False

            demo_ls.append(2)

        worker.do_async(async_func)
        demo_ls.append(1)
        worker.wait()
        assert demo_ls == [1, 2]
