import time 
import eventlet 


class Timer():
    def __init__(self, interval, func, args):
        self.interval = interval
        self.func = func
        self.args = args
        #self.gt = eventlet.spawn(func, args)

    def start(self):
        self.gt = eventlet.spawn(self._fun)
	#while True:
        #    eventlet.greenthread.sleep(self.interval)

    def _fun(self):
        while True:
            self.func(self.args)
            eventlet.greenthread.sleep(self.interval)


    def stop(self):
        self.gt.wait()

def sayhello(args=[]):
    print "hello"
    print args


if __name__ == "__main__":
    t = Timer(5, sayhello, ["this", "is", "timer"])
    t.start()
