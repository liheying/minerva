## Minerva

![智慧女神号](/minerva/conf/1.png "minerva")

Minerva(智慧女神号)旨在提供**简单可依赖的分布式数据定向抓取工具**,目前已经实现有:
+ 获取点评的POI信息
+ 获取知乎的问题&答案

#### 特点
+ 使用redis存储linkbase信息:抓取url的FIFO队列由redis的list维护,已抓取url集合由redis的set维护
+ 页面解析存储在mongo,字段易存储、易扩展
+ spider可在多台机器单进程运行,充分利用机器资源
+ master和slave间方法调用采用Thrift RPC服务框架,效率高

#### Usage:
启动master: `python master.py`, 启动spider: `python spider.py`

#### 相关的依赖库:
+ pymongo (3.4.0)
+ redis (2.10.5)
+ thriftpy (0.3.9)
+ BeautifulSoup (3.2.1)
+ requests (2.13.0)


