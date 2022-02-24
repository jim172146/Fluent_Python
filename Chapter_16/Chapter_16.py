__author__ = 'fmy'

import collections
import functools
import inspect

"协程"
# 本章主题:
# · 生成器作为协程使用时的行为和状态
# · 使用装饰器自动预激协程
# · 调用放如何使用生成器对象的.close()和.throw()方法控制协程
# · 协程终止时如何返回值
# · yield from新句法的用途和语义
# · 使用案例--使用协程管理仿真系统中的并发活动


# --------------------------------------------------
# 16.1 生成器如何进化成协程
print('*' * 50)
# 协程是指一个过程,这个过程的作用是终止生成器
# 生成器可以返回一个值
# 引入 yield from 句法,使用它可以把复杂的生成器重构成小型的嵌套生成器


# --------------------------------------------------
# 16.2 用作协程的生成器的基本行为
print('*' * 50)


# 协程简单演示
def simple_coroutine():  # 协程使用生成器函数定义,定义体中有yield关键字
    print('->coroutine started')
    x = yield
    # yield是在表达式中使用,如果协程只需从客户那接收数据,那么产出的值是None
    # 这个值是隐式指定的,因为yield关键字右边没有表达式
    print('->coroutine received:', x)


my_coro = simple_coroutine()
print(my_coro)  # 与创建生成器的方式一样,调用函数得到生成器对象
# 首先调用next()函数,因为生成器还没启动,没在yield处暂停,所以开始无法发送数据
next(my_coro)
"""
调用这个方法后,协程定义体中的yield表达式会计算出42
现在协程会恢复,一直运行到下一个yield表达式,或者终止
next(my_coro.send(42))  # Traceback:StopIteration
控制权流动到协程定义体末尾,导致生成器抛出StopIteration异常
"""
# 协程有四个状态,当前状态可以使用inspect.getgeneratorstate()函数确定
# 'GEN_CREATED'等待开始执行
# 'GEN_RUNNING'解释器正在执行
# 'GEN_SUSPENDED'在yield表达式处暂停
# 'GEN_CLOSED'执行结束

# 创建协程对象后立即把None之外的值发给它
my_coro = simple_coroutine()
"""
TypeError: can't send non-None value to a just-started generator
my_coro.send(1729)
"""
# 最先调用next()这一步称为'预激'(prime)协程


# 产出两个值的协程
def simple_coro2(a):
    print('->Started: a =', a)
    b = yield a
    print('->Started: b =', b)
    c = yield a + b
    print('->Started: c =', c)


my_coro2 = simple_coro2(14)
print(inspect.getgeneratorstate(my_coro2))
next(my_coro2)
print(inspect.getgeneratorstate(my_coro2))
my_coro2.send(28)
try:
    my_coro2.send(99)  # Traceback:StopIteration
except StopIteration:
    print(inspect.getgeneratorstate(my_coro2))
# 协程在yield关键字所在的位置暂停执行,等号右边的代码在赋值之前执行
# 对于 b = yield a, 等到客户端代码再激活协程时才会设定b的值


# --------------------------------------------------
# 16.3 示例:使用协程计算移动平均值
print('*' * 50)


# 定义一个计算移动平均值的协程
def average():
    total = 0.0
    count = 0
    average = None
    while True:
        # 当调用方在协程上调用.close()或没有对协程的引用而被垃圾回收程序回收时,这个协程才会终止
        term = yield print(average)
        total += term
        count += 1
        average = total/count


coro_average = average()  # 创建协程对象
next(coro_average)
coro_average.send(10)
coro_average.send(30)
coro_average.send(5)


# --------------------------------------------------
# 16.4 预激协程的装饰器
print('*' * 50)
# 如果不预激那么协程没什么用,# 调用my_coro.send(x)之前,一定要调用next(my_coro)


# 预激协程的装饰器
def coroutine(func):
    """装饰器:向前执行到yield表达式,预激协程"""
    @functools.wraps(func)
    def prime(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return prime


@coroutine
def average():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield average
        total += term
        count += 1
        average = total/count


coro_ave = average()
print(inspect.getgeneratorstate(coro_ave))
print(coro_ave.send(5))
print(coro_ave.send(15))
print(coro_ave.send(25))


# --------------------------------------------------
# 16.5 终止协程和异常处理
print('*' * 50)

# 未处理的异常会导致协程终止
my_ave = average()
print(my_ave.send(5))
print(my_ave.send(15))
# print(my_ave.send('spam'))  # 由于在协程内没有处理异常,协程会终


# 在协程中处理异常
class DemoException(Exception):
    """为这次演示定义的异常类型"""


def demo_exc_handling():
    print('-> coroutine started')
    while True:
        try:
            x = yield
        except DemoException:
            print('''***DemoException handled. Continuing...***''')
        else:
            print('-> coroutine received: {!r}'.format(x))
    raise RuntimeError('This line should never run.')


exc_coro = demo_exc_handling()
next(exc_coro)
exc_coro.send(11)
exc_coro.send(22)
exc_coro.close()
print(inspect.getgeneratorstate(exc_coro))

# 把DemoException异常传入demo_exc_handling协程,它会处理然后继续运行
print('-' * 10)
exc_coro = demo_exc_handling()
next(exc_coro)
exc_coro.send(11)
exc_coro.throw(DemoException)
print(inspect.getgeneratorstate(exc_coro))

# 如果传入协程的异常没有处理,协程会停止,即状态变成'GEN_CLOSED'
print('-' * 10)
exc_coro = demo_exc_handling()
next(exc_coro)
exc_coro.send(11)
exc_coro.send(ZeroDivisionError)
print(inspect.getgeneratorstate(exc_coro))


# 若不管协程如何结束都想做些清理工作,要把协程定义体中相关的代码放入try/finally块中
class DemoException(Exception):
    """为这次演示定义的异常类型"""


def demo_exc_handling():
    print('-> coroutine started')
    try:
        while True:
            try:
                x = yield
            except DemoException:
                print('''***DemoException handled. Continuing...***''')
            else:
                print('-> coroutine received: {!r}'.format(x))
            raise RuntimeError('This line should never run.')
    finally:
        print('-> coroutine ending')


# --------------------------------------------------
# 16.6 让协程返回值
print('*' * 50)
Result = collections.namedtuple('Result', 'count average')


def average():
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield
        if term is None:
            break
        total += term
        count += 1
        average = total/count
    return Result(count, average)


coro_avg = average()
next(coro_avg)
coro_avg.send(10)
coro_avg.send(30)
coro_avg.send(6.5)
# coro_avg.send(None)  # 发送None会终止循环,导致协程结束返回结果
# return表达式的值会偷偷传给调用方,赋值给StopIteration异常的一个属性

# 捕获StopIteration异常,获取averager返回的值
coro_avg = average()
next(coro_avg)
coro_avg.send(10)
coro_avg.send(30)
coro_avg.send(6.5)
try:
    coro_avg.send(None)
except StopIteration as exc:
    result = exc.value
print(result)


# --------------------------------------------------
# 16.7 使用yield from
print('*' * 50)


def gen():
    for c in 'AB':
        yield c
    for i in range(1, 3):
        yield i


print(list(gen()))


def gen():
    yield from 'AB'
    yield from range(1, 3)


print(list(gen()))


def chain(*iterables):
    for it in iterables:
        yield from it


s = 'ABC'
t = tuple(range(3))
print(list(chain(s, t)))

# 委派生成器:包含yield from<iterable>表达式的生成器函数
# 子生成器:从yield from表达式中<iterable>部分获取的生成器
# 调用方:代指调用伪生成器的客户端代码

# 使用yield from计算平均值并输出统计报告
Result = collections.namedtuple('Result', 'count average')


# 子生成器
def average():  # 与averager协程一样,这里作为子生成器使用
    total = 0.0
    count = 0
    average = None
    while True:
        term = yield  # main函数中的客户代码发送的各个值绑定到这里的term变量上
        if term is None:  # 至关重要的终止条件,如果不这么做使用yield from调用这个协程的生成器会永远阻塞
            break
        total += term
        count += 1
        average = total/count
    return Result(count, average)  # 返回的Result会成为grouper函数中yield from表达式的值


# 委派生成器
def grouper(result, key):
    while True:  # 这个循环每次迭代时会新建一个averager实例;每个实例都是作为协程使用的生成器对象
        result[key] = yield from average()  # grouper发送的每个值都会经由yield from处理,通过管道传给averager实例


# 客户端代码,即调用方
def main(data):  # main函数是客户端代码
    results = {}
    for key, values in data.items():
        group = grouper(results, key)
        # group是调用grouper函数得到的生成器对象,传给grouper函数的第一个参数是results用于收集结果;第二个参数是某个键
        next(group)  # 预激group协程
        for value in values:
            group.send(value)
            # 把各个value传给grouper,传入的值最终到达averager函数中term=yield那一行;grouper永远不知道传入的值是什么
        group.send(None)
        # 把None传入grouper,导致当前的averager实例终止,也让grouper继续运行,再建一个averager实例,处理下一组值
    print(results)
    report(results)


# 输出报告
def report(results):
    for key, result in sorted(results.items()):
        group, unit = key.split(';')
        print('{:<3}{:<5} averaging {:<7.2f}{}'.format(result.count, group, result.average, unit))


data = {
    'girls;kg':
        [40.9, 38.5, 44.3, 42.2, 45.2, 41.7, 44.5, 38.0, 40.6, 44.5],
    'girls;m':
        [1.6, 1.51, 1.4, 1.3, 1.41, 1.39, 1.33, 1.46, 1.45, 1.43],
    'boys;kg':
        [39.0, 40.8, 43.2, 40.8, 43.1, 38.6, 41.4, 40.6, 36.3],
    'boys;m':
        [1.38, 1.5, 1.32, 1.25, 1.37, 1.48, 1.25, 1.49, 1.46],
}

if __name__ == '__main__':
    main(data)

#  运作方式
# • 外层for循环每次迭代会新建一个grouper实例,赋值给group变量,group是委派生成器
# • 调用next(group),预激委派生成器grouper,此时进入while True循环,
#   调用子生成器averager后,在yield from表达式处暂停
# • 内层for循环调用group.send(value),直接把值传给子生成器averager
#   同时,当前的grouper实例(group)在yield from表达式处暂停
# • 内层循环结束后,group实例依旧在yield from表达式处暂停,因此,grouper函数定义体中
#   为results[key]赋值的语句还没有执行
# • 如果外层for循环的末尾没有group.send(None),那么averager子生成器永远不会终止
#   委派生成器group永远不会再次激活,因此永远不会为results[key]赋值
# • 外层for循环重新迭代时会新建一个grouper实例,然后绑定到group变量上
#   前一个grouper实例(以及它创建的尚未终止的averager子生成器实例)被垃圾回收程序回收


# --------------------------------------------------
# 16.8 yield from 的意义
print('*' * 50)
# 六点说明了yield from的行为：
# 1).子生成器产出的值都直接传给委派生成器的调用方(即客户端代码)
# 2).使用send()方法发给委派生成器的值都直接传给子生成器,若发送的值是None则调用子生成器的__next__()方法
#    若None则会调用子生成器的send()方法
#    若如果调用的方法抛出StopIteration异常则委派生成器恢复运行,任何其他异常都会向上冒泡,传给委派生成器
# 3).生成器退出时,生成器(或子生成器)中的return expr表达式会触发StopIteration(expr)异常抛出
# 4).yield from表达式的值是子生成器终止时传给StopIteration异常的第一个参数

# yield from结构的另外两个特性与异常和终止有关
# 5).传入委派生成器的异常,除了GeneratorExit之外都传给子生成器的throw()方法
#    若调用throw()方法时抛出StopIteration异常，委派生成器恢复运行
#    StopIteration之外的异常会向上冒泡，传给委派生成器
# 6).若把GeneratorExit异常传入委派生成器,或者在委派生成器上调用close()方法,
#    那么在子生成器上调用close()方法,如果它有的话.
#    如果调用close()方法导致异常抛出，那么异常会向上冒泡,传给委派生成器;
#    否则,委派生成器抛出GeneratorExit异常


# --------------------------------------------------
# 16.9 使用案例:使用协程做离散时间的仿真
print('*' * 50)


# --------------------------------------------------
# 16.10 本章小结
print('*' * 50)

