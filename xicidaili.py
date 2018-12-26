import requests
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import time
from pymongo import MongoClient

client = MongoClient(host="127.0.0.1", port=27017)
db = client['proxypool']
collection = db['test']

# 爬取西刺代理
def get_proxy():
    data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400',
        'referer': 'https://www.xicidaili.com/'
    }
    proxies = {
        'https': 'https://217.19.209.253:8080'
    }
    for i in range(1, 5):
        url = 'https://www.xicidaili.com/nn/{}'.format(i)
        res = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        print(res.status_code)
        data = etree.HTML(res.text)
        time.sleep(2)

        contents = data.xpath('//tr[@class]')  # 去掉标题行
        for content in contents:
            ip = content.xpath('./td[2]/text()')[0]
            port = content.xpath('./td[3]/text()')[0]
            type = content.xpath('./td[6]/text()')[0]
            proxy = '{0}://{1}:{2}'.format(type, ip, port)
            print(proxy)
            data.append(proxy)
    return data

# 验证proxy的可用性并存入数据库
def test_proxy(proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400'
    }
    ip = {
        "https": "https://" + proxy
    }
    try:
        res = requests.get('https://www.baidu.com/', headers=headers, proxies=ip, timeout=5)
        if res.status_code == 200:
            items = {
                'proxies': "https://" + proxy
            }
            collection.insert(items)
            print('有效', proxy)
    except:
        print('无效')
        pass

# 多线程
data = get_proxy()
print(data)
executor = ThreadPoolExecutor(max_workers=2)
for proxy in data:
    all_task = [executor.submit(test_proxy, (proxy))]
