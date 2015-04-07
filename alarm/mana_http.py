import httplib

class HttpCon():
    def __init__(self, host, port, url, method):
        self.host = host
        self.port = port
        self.url = url
        self.method = method
        self.timeout = 30

    def get(self):
        try:
            self.con = httplib.HTTPConnection(self.host, self.port, self.timeout)
            self.con.request(self.method, self.url)
            response = self.con.getresponse()
            status = response.status 
            if status != 200:
                return NULL
            return response.read()
        except Exception, e:
            print e

    def __del__(self):
        if self.con:
            self.con.close()

if __name__ == "__main__":
    a = HttpCon("www.baidu.com", 80, "/", "GET")
    print a.get()
