import requests
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import time

client = MongoClient(host="127.0.0.1", port=27017)
db = client['test']
collection = db['proxypool']


# 从提取文件中导入proxies
def get_proxy():
    data = []
    for line in open("proxies.txt", "r"):
        data.append(line[:-1])
    print("总数：", len(data))
    return data


# 验证proxy的可用性并存入数据库
def test_proxy(proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.6788.400 QQBrowser/10.3.2864.400'
    }
    ip = {
        "https": "https://" + proxy  # 根据目标网址的协议修改
    }
    try:
        res = requests.get('https://brucegao.cn', headers=headers, proxies=ip, timeout=5)
        if res.status_code == 200:
            items = {
                'proxy': proxy
            }
            collection.insert(items)
            print('有效', proxy)
    except:
        print('无效')
        pass


# 多线程
data = get_proxy()
executor = ThreadPoolExecutor(max_workers=10)
for proxy in data:
    time.sleep(2)
    all_task = [executor.submit(test_proxy, proxy)]


