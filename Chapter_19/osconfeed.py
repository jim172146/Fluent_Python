# osconfeed.py：下载osconfeed.json

from urllib.request import urlopen
import warnings
import os
import json

URL = 'http://www.oreilly.com/pub/sc/osconfeed'
JSON = 'data/osconfeed.json'


def load():
    if not os.path.exists(JSON):
        msg = 'downloading {} to {}'.format(URL, JSON)
        warnings.warn(msg)
        # 在with语句中使用两个上下文管理器分别用于读取和保存远程文件
        with urlopen(URL) as remote, open(JSON, 'wb') as local:
            local.write(remote.read())

    with open(JSON) as fp:
        # json.load函数解析JSON文件,返回Python原生对象
        return json.load(fp)

# 我们没有缓存或转换原始数据源.在迭代数据源的过程中,嵌套的数据结构不断被
# 转换成FrozenJSON对象,这么做没问题因为数据集不大,而且这个脚本只用于访问或转换数据
