import requests
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import time
from pymongo import MongoClient

client = MongoClient(host="127.0.0.1", port=27017)
db = client['proxypool']
collection = db['runoob6']

# 爬取西刺代理
def get_proxy():
    data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400',
        'referer': 'https://www.xicidaili.com/'
    }

    for i in range(1, 5):
        url = 'https://www.xicidaili.com/nn/{}'.format(i)
        r = requests.get(url, headers=headers)
        s = etree.HTML(r.text)
        time.sleep(2)

        contents = s.xpath('//tr[@class]')  # 去掉标题行
        for content in contents:
            ip = content.xpath('./td[2]/text()')[0]
            port = content.xpath('./td[3]/text()')[0]
            scheme = content.xpath('./td[6]/text()')[0]
            print(ip, port, scheme)
            proxy = {
                'ip_port': '{0}:{1}'.format(ip, port),
                'scheme': scheme
            }
            data.append(proxy)
    return data


# 验证proxy的可用性并存入数据库
def test_proxy(proxy):
    ip_port = proxy['ip_port']
    scheme = proxy['scheme']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400'
    }
    ip = {
        'http': "{}://".format(scheme) + ip_port
    }
    try:
        res = requests.get('http://www.runoob.com/', headers=headers, proxies=ip, timeout=5)
        if res.status_code == 200:
            print(res.content)
            items = {
                'proxy': "{}://".format(scheme) + ip_port
            }
            collection.insert(items)
            print('有效', ip_port)
    except:
        print('无效')
        pass


# 多线程
data = get_proxy()
print('======= 爬取结束  开始验证 =======')
executor = ThreadPoolExecutor(max_workers=10)
for proxy in data:
    time.sleep(2)
    all_task = [executor.submit(test_proxy, proxy)]
