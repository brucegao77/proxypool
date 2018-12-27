from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import requests


client = MongoClient()
db = client['proxypool']
collection = db['proxies']

# 访问mongodb数据
proxies = []
for i in collection.find({}, {'_id': 0, 'proxy': 1}):
    proxies.append(i['proxy'])


# 验证proxy的可用性并更新数据库
def test_proxy(proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400'
    }
    ip = {
        "https": proxy
    }
    try:
        res = requests.get('https://httpbin.org/ip', headers=headers, proxies=ip, timeout=5)
        if res.status_code != 200:
            items = {
                'proxies': proxy
            }
            collection.delete_one(items)
            proxies.pop(proxy)
            print('已删除', len(proxies))
        else:
            print('有效', proxy)

    except:
        items = {
            'proxies': proxy
        }
        collection.delete_one(items)
        proxies.pop(proxy)
        print('已删除', len(proxies))


print(len(proxies))
executor = ThreadPoolExecutor(max_workers=50)
for proxy in proxies:
    all_task = [executor.submit(test_proxy, proxy)]
