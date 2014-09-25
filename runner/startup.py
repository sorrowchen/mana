from threading import Thread,Event
from minions.views import loop_compute_nodes
import time

def sys_startup():
	print "salt__startup"
	stopFlag = Event()
	thread = SaltThread(stopFlag)
	thread.start()

class SaltThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
	#time.sleep(10)
	loop_compute_nodes()
        #while not self.stopped.wait(60):
            #exe_one_minute()


#stopFlag = Event()
#thread = OneMinuteThread(stopFlag)
#thread.start()
# this will stop the timer
#stopFlag.set()





