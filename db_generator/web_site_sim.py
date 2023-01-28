import simpy
import random
import numpy as np
import os
from logger import FileLogger

class OnlineShop(object):
    def __init__(self, env):
        self.env = env
        self.add_to_cart_p = 0.1 #Вероятность добавления в корзину
        self.purchase_cart_p = 0.7 #Вероятность покупки корзины
        self.main_page_p = 0.4 #Вероятность попадания на сайт через главную страницу
        self.page_404_p = 0.1 #Вероятность попадания на 404
        self.page_404_continue_p = 0.4 #Вероятность продолжения использования сайта после 404
        self.avg_product_visit = 5 #среднее количство посещенных страниц с товаром
        self.dispersion_product_visit = 30 #дисперсия посещенных страниц с товаром
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
        cart_count = 0
        if random.random() < self.page_404_p: # Иногда появляются переходы на 404
            yield self.env.process(self.pages['404'].open(self.env,logger,visitor))
            if random.random() > self.page_404_continue_p: # Продолжает пользоваться сайтом или уходит
                return
            
        if random.random() < self.main_page_p: #Если попадаем на сайт через главную старницу
            yield self.env.process(self.pages['main'].open(self.env,logger,visitor))
            yield self.env.process(self.pages['catalog'].open(self.env,logger,visitor))# открываем каталог

        choose_catalog = random.choice(list(self.catalog))
        choose_catalog_url = self.domain+'catalog/'+ choose_catalog + "/" 
        yield self.env.process(WebPage(choose_catalog_url,"GET",20).open(self.env,logger,visitor))# открываем случайный раздел из каталога

        for i in range(int(np.abs(np.random.normal(self.avg_product_visit, self.dispersion_product_visit)))): # просматривает несколько товаров
            choose_product_id = str(random.choice(self.catalog[choose_catalog]))
            choose_product_url = choose_catalog_url+ choose_product_id + "/"
            yield self.env.process(WebPage(choose_product_url,"GET",20).open(self.env,logger,visitor))#переходит на страницу товара
            if random.random() < self.add_to_cart_p:
                yield self.env.process(self.pages['add-to-cart'].open(self.env,logger,visitor))# добавляет в корзину 
                yield self.env.process(WebPage(choose_product_url,"GET",5).open(self.env,logger,visitor))#редирект обратно на страницу продукта
                cart_count += 1
            yield self.env.process(WebPage(choose_catalog_url,"GET",20).open(self.env,logger,visitor))#возвращается обратано в каталог
        
        if cart_count > 0:
            yield self.env.process(self.pages['cart'].open(self.env,logger,visitor))#Переходит в корзину
            if random.random() < self.purchase_cart_p:# оплачивает ли заказ
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



def generate_visitor():
    with open('user_agent_top_50.txt') as file:
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