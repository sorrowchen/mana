from threading import Thread,Event
from views import loop_compute_nodes
import time
def sys_startup():
    print "Sys_startup"

def exe_one_minute():
    print "exe_one_minute"

#t=threading.Timer(5,loop_compute_nodes)
#t.start()

class OneMinuteThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
	print "wait 60s"
	time.sleep(60)
	loop_compute_nodes()
        #while not self.stopped.wait(60):
            #exe_one_minute()

stopFlag = Event()
thread = OneMinuteThread(stopFlag)
thread.start()
# this will stop the timer
#stopFlag.set()






