import time
import datetime

#UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S"

ISOTIMEFORMAT='%Y-%m-%d %X'

def getlocalstrtime():
    return time.strftime(ISOTIMEFORMAT,time.localtime(time.time()))

def getNowAfterHours(ours=8):
    after=datetime.datetime.now()+datetime.timedelta(hours=ours)
    return after.strftime(LOCAL_FORMAT)

def getUTCstrtime():
    return time.strftime(ISOTIMEFORMAT,time.gmtime(time.time()))

def utc2local(utc):
    utc_st=datetime.datetime.strptime(utc, UTC_FORMAT)
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st.strftime(LOCAL_FORMAT)

def local2utc(local):
    local_st=datetime.datetime.strptime(local, LOCAL_FORMAT)
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st.strftime(UTC_FORMAT)

def utc2Msecs(utc):
    timeArray = time.strptime(utc, LOCAL_FORMAT)
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def msecs2local(msecs):
    timeArray = time.localtime(msecs)
    otherStyleTime = time.strftime(LOCAL_FORMAT, timeArray)
    return otherStyleTime

def msecs2utc(msecs):
    timeArray = time.localtime(msecs)
    otherStyleTime = time.strftime(UTC_FORMAT, timeArray)
    return otherStyleTime
