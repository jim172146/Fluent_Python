__author__ = 'fmy'

import os
import time
import sys
import requests
from concurrent import futures

"使用期物处理并发"
# 期物(future):指一种对象,表示异步执行的操作


# --------------------------------------------------
# 17.1 示例:网络下载的三种风格
print('*' * 50)
# 在公网中测试HTTP并发客户端可能不小心变成拒绝服务

# 1).依次下载的脚本
POP20_CC = ('CN IN US ID BR PK NG BD RU JP '
            'MX PH VN ET EG DE IR TR CD FR').split()
BASE_URL = 'http://flupy.org/data/flags'
DEST_DIR = 'downloads/'


def prepare_work():
    if os.path.exists('downloads'):
        for file in os.listdir(DEST_DIR):
            os.remove(os.getcwd() + '\\downloads\\' + str(file))
    else:
        os.makedirs('downloads')


def save_flag(img, filename):
    path = os.path.join(DEST_DIR, filename)
    with open(path, 'wb') as fp:
        fp.write(img)


def get_flag(cc):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=cc.lower())
    resp = requests.get(url)
    return resp.content


def show(text):
    print(text, end=' ')
    sys.stdout.flush()


def download_many(cc_list):
    for cc in cc_list:
        image = get_flag(cc)
        show(cc)
        save_flag(image, cc.lower() + '.gif')
    return len(cc_list)


def main(download_many):
    prepare_work()
    t0 = time.time()
    count = download_many(POP20_CC)
    elapsed = time.time() - t0
    msg = f'\n{count} flags downloaded in {elapsed:.2f}s'
    print(msg)


# 2).使用concurrent.futures模块下载
def download_one(cc):
    image = get_flag(cc)
    show(cc)
    save_flag(image, cc.lower() + '.gif')
    return cc


def download_many2(cc_list):
    MAX_WORKES = 20
    workers = min(MAX_WORKES, len(cc_list))
    with futures.ThreadPoolExecutor(workers) as executor:
        res = executor.map(download_one, sorted(cc_list))
    return len(list(res))


def main2(download_many2):
    prepare_work()
    t0 = time.time()
    count = download_many2(POP20_CC)
    elapsed = time.time() - t0
    msg = f'\n{count} flags downloaded in {elapsed:.2f}s'
    print(msg)


# 把download_many2函数中的executor.map方法换成executor.submit和futures.as_completed
def download_many3(cc_list):
    cc_list = cc_list[:5]
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        to_do = []
        for cc in sorted(cc_list):
            future = executor.submit(download_one, cc)
            to_do.append(future)
            print(f'Scheduled for {cc}:{future}')

        results = []
        for future in futures.as_completed(to_do):
            res = future.result()
            print(f'{future} result:{res!r}')
            results.append(res)

    return len(results)


def main3(download_many3):
    prepare_work()
    t0 = time.time()
    count = download_many3(POP20_CC)
    elapsed = time.time() - t0
    msg = f'\n{count} flags downloaded in {elapsed:.2f}s'
    print(msg)


# --------------------------------------------------
# 17.2 阻塞型I/O和GIL
print('*' * 50)
# CPython解释器本身就不是线程安全的,因此有全局解释器锁(GIL)
# 一次只允许使用一个线程执行Python字节码
# 因此一个Python进程通常不能同时使用多个CPU核心

# Python标准库中的所有阻塞型I/O函数都会释放GIL,允许其他线程运行
# time.sleep()函数也会释放GIL.
# 因此尽管有GIL,Python线程还是能在I/O密集型应用中发挥作


# --------------------------------------------------
# 17.3 使用concurrent.futures模块启动进程
print('*' * 50)


# ProcessPoolExecutor的价值体现在CPU密集型作业上
def download_many4(cc_list):
    with futures.ProcessPoolExecutor() as executor:
        res = executor.map(download_one, sorted(cc_list))
    return len(list(res))


def main4(download_many4):
    prepare_work()
    t0 = time.time()
    count = download_many4(POP20_CC)
    elapsed = time.time() - t0
    msg = f'\n{count} flags downloaded in {elapsed:.2f}s'
    print(msg)


# --------------------------------------------------
# 17.4 实现Executor.map方法
print('*' * 50)


def display(*args):
    print(time.strftime('[%H:%M:%S]'), end=' ')
    print(*args)


def loiter(n):
    msg = '{}loiter({}):doing nothng for {}s...'
    display(msg.format('\t'*n, n, n))
    time.sleep(n)
    msg = '{}loiter({}):done.'
    display(msg.format('\t'*n, n))
    return n * 10


def main4():
    display('Script starting.')
    executor = futures.ThreadPoolExecutor(max_workers=3)
    results = executor.map(loiter, range(5))
    display('results:', results)
    display('Waiting for individual results:')
    # executor.map方法返回的结果是生成器;不管有多少任务,不管max_workers的值是多少,不会阻塞
    for i, result in enumerate(results):
        display('result {}: {}'.format(i, result))


# --------------------------------------------------
# 17.5 显示下载进度并处理错误
print('*' * 50)


# --------------------------------------------------
# 17.6 本章小结
print('*' * 50)


if __name__ == '__main__':
    main4()
