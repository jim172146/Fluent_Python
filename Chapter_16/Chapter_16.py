__author__ = 'fmy'

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
        term = yield average
        total += term
        count += 1
        average = total/count


coro_average = average()
next(coro_average)
print(coro_average.send(10))
print(coro_average.send(30))
print(coro_average.send(5))
