import logging 
import os

#LOG_FILE = 'monitor.log'
LOG_FILE = '/var/log/mana/monitor.log'
#logging.basicConfig(filename = os.path.join(os.getcwd(), LOG_FILE), 
logging.basicConfig(filename = LOG_FILE,
                    level = logging.DEBUG, 
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', 
                    datefmt= '%m-%d %H:%M') 

console = logging.StreamHandler()  
console.setLevel(logging.INFO) 
logging.getLogger('').addHandler(console)  

def GetLog(name):
    log = logging.getLogger(name)
    return log 


if __name__ == "__main__":
    log  =  GetLog(__name__)
    log.info("hello world!")
    log.debug("hello python!")
    log.warn("warn!!!!")
    log.error("error!!") 