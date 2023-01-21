import simpy
import random
import numpy as np
import statistics
import datetime
import time 

import os

class OnlineShop(object):
    def __init__(self, env):
        self.env = env
        self.domain = "http://krep.com/"
        self.pages = {
            'main': WebPage(self.domain,"GET",5),
            'catalog': WebPage(self.domain+'catalog/',"GET",10),
            'cart': WebPage(self.domain+'cart/',"GET",5),
            'thanks': WebPage(self.domain+'thanks/',"GET",5),
            'add-to-cart': WebPage(self.domain+'add-to-cart/',"POST",0,http_status=303),
            'order': WebPage(self.domain+'order/',"GET",15),
            'order-data': WebPage(self.domain+'order-data/',"POST",0,http_status=303),
            '404': WebPage(self.domain+'404/',"POST",2,http_status=404),
        }
        self.catalog = {'gvozdi':range(1000),'dyubeli':range(1000,2000),'zaklyopki':range(2000,3000),'xomuty':range(3000,4000),'takelaz':range(4000,5000),'samorezy':range(5000,6000)}
    def run_visitor(self,logger, visitor):
        yield self.env.process(self.pages['main'].open(self.env,logger,visitor))
        yield self.env.process(self.pages['catalog'].open(self.env,logger,visitor))# открываем каталог

        choose_catalog = random.choice(list(self.catalog))
        choose_catalog_url = self.domain+'catalog/'+ choose_catalog + "/" 
        yield self.env.process(WebPage(choose_catalog_url,"GET",20).open(self.env,logger,visitor))# открываем случайный раздел из каталога

        for i in range(random.randint(1,10)): # просматривает случаное число товаров
            choose_product_id = str(random.choice(self.catalog[choose_catalog]))
            choose_product_url = choose_catalog_url+ choose_product_id + "/"
            yield self.env.process(WebPage(choose_product_url,"GET",20).open(self.env,logger,visitor))#переходит на страницу товара
            if random.choice([False,False,True]):
                yield self.env.process(self.pages['add-to-cart'].open(self.env,logger,visitor))# добавляет в корзину 
                yield self.env.process(WebPage(choose_product_url,"GET",5).open(self.env,logger,visitor))#редирект обратно на страницу продукта
            yield self.env.process(WebPage(choose_catalog_url,"GET",20).open(self.env,logger,visitor))#возвращается обратано в каталог
        
            
        yield self.env.process(self.pages['cart'].open(self.env,logger,visitor))#Переходит в корзину
        yield self.env.process(self.pages['order'].open(self.env,logger,visitor))#Переходит на страницу заказа
        yield self.env.process(self.pages['order-data'].open(self.env,logger,visitor))# Отправляет данные о заказе
        yield self.env.process(self.pages['thanks'].open(self.env,logger,visitor))# Редирект на страницу спасибо за заказ

            
        

        


class WebPage:
    def __init__(self, url,method,avg_active_time,http_status=200):
        self.url = url
        self.method = method
        self.http_status = http_status
        self.avg_active_time = avg_active_time
    def open(self,env,logger, visitor):
        request_time = visitor.get_request_time()
        visit_time = np.abs(np.random.normal(5, 6))
        logger.append_log(env,self,visitor,request_time)
        yield env.timeout(request_time+visit_time)

class Visitor:
    def __init__(self,ip,avg_request_time,connection_stability,user_agent):
        self.avg_request_time = avg_request_time
        self.connection_stability = connection_stability
        self.ip = ip
        self.user_agent = user_agent
    def get_request_time(self):
        return np.abs(np.random.normal(self.avg_request_time, self.connection_stability))

class Logger:
    def __init__(self,base_time = datetime.datetime.now()):
        self.base_time = base_time
        self.buffer = []
        self.max_buffer_size = 100000
    def append_log(self,env,web_page,visitor,request_time):
        data = [self.base_time + datetime.timedelta(seconds=env.now),web_page.url,web_page.method,web_page.http_status,visitor.user_agent,visitor.ip,request_time]
        self.buffer.append(data)
        if len(self.buffer) >= self.max_buffer_size:
            self._send_buffer()

    def _send_buffer(self):
        pass

class FileLogger(Logger):
    def __init__(self,file_name,base_time = datetime.datetime.now()):
        self.base_time = base_time
        self.file_name = file_name
        self.buffer = []
        self.max_buffer_size = 100000
    def _send_buffer(self):
        with open(self.file_name, "a+") as f:
            buffer_str = map(str,self.buffer)
            f.write("\n".join(buffer_str))
        self.buffer.clear()

class ClickhouseLogger(Logger):
    def __init__(self,client,table_name, base_time = datetime.datetime.now()):
        self.base_time = base_time
        self.client = client
        self.table_name = table_name
        self.buffer = []
        self.max_buffer_size = 100000
    def _send_buffer(self):
        self.client.insert(self.table_name, self.buffer, column_names=['timestamp','request','request_method','http_status','user_agent','user_ip','request_time'])
        self.buffer.clear()

def generate_visitor():
    with open('user-agents.txt') as file:
        user_agents = [line.rstrip() for line in file]
    ip = str(random.randint(0,255))+'.'+str(random.randint(0,255))+'.'+str(random.randint(0,255))+'.'+str(random.randint(0,255))
    avg_request_time = np.abs(np.random.normal(2, 20))
    connection_stability = np.abs(np.random.normal(1, 20))
    user_agent = random.choice(user_agents)
    return Visitor(ip,avg_request_time,connection_stability,user_agent)

def run_online_shop(env,logger,visitors_per_hour):
    online_shop = OnlineShop(env)
    avg_timeout = 3600/visitors_per_hour
    while True:
        yield env.timeout(np.abs(np.random.normal(avg_timeout, avg_timeout)))  
        visitor = generate_visitor()
        env.process(online_shop.run_visitor(logger,visitor))
    

def generate_logs(logger,seed,visitors_per_hour,sim_duration):
    random.seed(seed)
    
    env = simpy.Environment()
    env.process(run_online_shop(env,logger,visitors_per_hour))
    env.run(sim_duration)

if __name__ == "__main__":
    print(os.listdir())
    logger = FileLogger('log.txt')
    generate_logs(logger,52,100,7200)
    logger._send_buffer()