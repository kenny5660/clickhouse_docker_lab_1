
import datetime

class Logger:
    def __init__(self,base_time = datetime.datetime.now(),buffer_size = 10000):
        self.base_time = base_time
        self.buffer = []
        self.buffer_size = buffer_size
    def append_log(self,env,web_page,visitor,request_time):
        data = [self.base_time + datetime.timedelta(seconds=env.now),web_page.url,web_page.method,web_page.http_status,visitor.user_agent,visitor.ip,request_time]
        self.buffer.append(data)
        if len(self.buffer) >= self.buffer_size:
            self._send_buffer()

    def _send_buffer(self):
        pass

class FileLogger(Logger):
    def __init__(self,file_name,base_time = datetime.datetime.now(),buffer_size = 10000):
        self.base_time = base_time
        self.file_name = file_name
        self.buffer = []
        self.buffer_size = buffer_size
    def _send_buffer(self):
        with open(self.file_name, "a+") as f:
            buffer_str = map(str,self.buffer)
            f.write("\n".join(buffer_str))
        self.buffer.clear()

class ClickhouseLogger(Logger):
    def __init__(self,client,table_name, base_time = datetime.datetime.now(),buffer_size = 10000):
        self.base_time = base_time
        self.client = client
        self.table_name = table_name
        self.buffer = []
        self.buffer_size = buffer_size
    def _send_buffer(self):
        self.client.insert(self.table_name, self.buffer, column_names=['timestamp','request','request_method','http_status','user_agent','user_ip','request_time'])
        self.buffer.clear()