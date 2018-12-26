import requests
from pymongo import MongoClient

client = MongoClient(host="127.0.0.1", port=27017)
db = client['proxypool']
collection = db['proxies']


# 从提取文件中导入proxies
def get_proxy():
    data = []
    for line in open("proxy.txt", "r"):
        data.append(line[:-1])
    print("总数：", len(data))
    return data


# 验证proxy的可用性并存入数据库
def test_proxy(proxy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'
    }
    type = 'https'
    ip = {
        "https": "https://" + proxy
    }
    try:
        res = requests.get('https://icanhazip.com', headers=headers, proxies=ip, timeout=5)
        if res.status_code == 200:
            proxies = type + "://" + proxy
            items = {
                'proxies': proxies
            }
            if collection.insert(items):
                print('有效', res.status_code, res.text)
    except:
        print('无效')
        pass


# 存入数据库
count = 0
data = get_proxy()
for proxy in data:
    count += 1
    print('====== 当前验证第{}个 ======'.format(count))
    test_proxy(proxy)

