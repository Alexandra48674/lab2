import random
import time
from threading import Thread


class WorkerThread(Thread):
    def run(queue):
        while True:
            item = queue.get()
            if not item is None:
                res = item.func(*item.argl, **item.argd)
                item.future.setResult(res)
            if not queue.work:
                return


class Future:
    def __init__(self):
        self.res = None
        self.hasResult = False

    def setResult(self, res):
        self.res = res
        self.hasResult = True

    def result(self):
        while not self.hasResult:
            pass
        return self.res


class Item:
    def __init__(self, func, *argl, **argd):
        self.func = func
        self.argl = argl
        self.argd = argd
        self.inWork = False
        self.future = Future()

    def __str__(self):
        return str(self.future.res)


class CustomExecute:
    def __init__(self, threads=4):
        self.thr = []
        self.queue = []
        self.work = True
        for i in range(threads):
            self.thr.append(Thread(target=WorkerThread.run, args=[self], daemon=True))
            self.thr[-1].start()

    def execute(self, func, *argl, **argd):
        i = Item(func, *argl, **argd)
        self.queue.append(i)
        return i

    def map(self, func, args_array):
        l = []
        for i in args_array:
            i = Item(func, i)
            l.append(i)
            self.queue.append(i)
        return l

    def shutdown(self):
        while True:
            if not False in [i.future.hasResult for i in self.queue]:
                self.work = False
                [i.join() for i in self.thr]
                return

    def get(self):
        for i in self.queue:
            if not i.inWork:
                i.inWork = True
                return i


def test(text):
    r = random.randint(1, 6)
    time.sleep(r)
    print(text, r)
    return r


e = CustomExecute(4)
i = e.execute(test, "12345")
print(i.future.hasResult)
r = i.future.result()
print(i.future.hasResult)
print(r)

lst = e.map(test, list(range(10)))
e.shutdown()
