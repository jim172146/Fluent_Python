__author__ = 'fmy'

import collections.abc
import html
import time
import functools
import numbers

"函数装饰器和闭包"
# 装饰器用于在源码中'标记'函数,以某种方式增强函数的行为；功能强大,进一步了解需要闭包的概念
# 闭包除了在装饰器中有用处之外,闭包还是回调式异步编程和函数式编程风格的基础
# 本章目的在于解释清楚函数装饰器的工作原理,包括简单的注册装饰器和复杂的参数化装饰器
# 本章讨论话题如下:
# · Python如何计算装饰器语法
# · Python如何判断变量是不是局部
# · 闭包存在的原因和工作原理
# · nonlocal能解决什么问题

# 掌握这些基础知识后,进一步讨论装饰器:
# · 实现行为良好的装饰器
# · 标准库中有用的装饰器
# · 实现一个参数化装饰器


# --------------------------------------------------
# 7.1 装饰器基础知识
print('*' * 50)


# 装饰器是可调用对象,其参数是另一个函数(被装饰的函数)


# 先定义一个装饰器
def decorate(func):
    def wrapper():
        print('-' * 10)
        func()
        print('-' * 10)

    return wrapper


@decorate
def target():
    print('Run target()')


target()


# 上述代码与下述相同:
def target():
    print('Run target()')


target = decorate(target)
target()


# 装饰器通常把话说农户替换成另一个函数
def deco(func):
    def inner():
        print('Running inner()')

    return inner  # deco返回inner函数对象


@deco
def target():  # 使用deco装饰target
    print('Running target()')


target()  # 调用被装饰的target其实会运行inner
print(target)  # 审查对象,发现target是inner的引用
# 严格来说,装饰器只是语法糖;抓鬼呢十七可以像常规的可调用对象那样调用,其参数是另一个函数
# 装饰器的一大特性:能把装饰的函数替换成其他函数;装饰器加载模块时立即执行


# --------------------------------------------------
# 7.2 Python何时执行装饰器
print('*' * 50)
# 装饰器的一个关键特性是,它们在被装饰的函数定义之后立即运行
# 导入registration.py模块(不作为脚本运行),输出如下:
import registration
# Running register(<function f1 at 0x00000231308C8040>)
# Running register(<function f2 at 0x00000231308C80D0>)
print(registration.registry)

# 以上说明,函数装饰器在导入模块时立即执行,而被装饰的函数只在明确调用时运行
# 实际中,装饰器通常在一个模块中定义,然后应用到其他模块中的函数上
# register装饰器返回的函数与通过参数传入的相同,实际中大多数装饰器会在内部定义一个函数,然后将其返回


# --------------------------------------------------
# 7.3 使用装饰器改进'策略'模式
print('*' * 50)
# 上一章promotions列表中的值使用daa_promotion装饰器填充
promotions = []


# add_promotion装饰器,把promotion_func添加到promotions类表中,然后原封不动地将其返回
def add_promotion(promotion_func):
    promotions.append(promotion_func)
    return promotion_func


@add_promotion
def fidelity(order):
    return order.total() * 0.05 if order.customer.fidelity >= 1000 else 0


@add_promotion
def bulk_item(order):
    discount = 0
    for item in order.cart:
        if item.quanlity >= 20:
            discount += item.total() * 0.1
    return discount


@add_promotion
def large_order(order):
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * 0.07
    return 0


def best_promotion(order):
    return max(promotion(order) for promotion in promotions)


# 相比于上一章节,该方案的优点:
# · 促销策略函数无需使用特殊的名称(即不用以_promotions结尾)
# · @promotion装饰器突出了被装饰的函数的作用,还便于零食禁用某个促销策略:只需把装饰器注释掉
# · 促销策略可以在其他模块中定义,在系统的任何地方都行,只要使用@promotion装饰即可


# --------------------------------------------------
# 7.4 变量作用域规则
print('*' * 50)


# 一个函数,读取一个局部变量和一个全局变量
def f1(a):
    print(a)
    print(b)


# f1(3) Traceback NameError:name 'b' is not defined
b = 6
f1(3)


# b时局部变量,因为在函数的定义中给它赋值了
b = 66


def f2(a):
    print(a)
    print(b)  # 局部变量在赋值前调用
    b = 99


# f2(33) Traceback UnboundLocalError:local variable 'b' referenced before assignment

# b作为全局变量
b = 666


def f3(a):
    global b
    print(a)
    print(b)  # 局部变量在赋值前调用
    b = 999


f3(333)
print(b)
b = 444
print(b)


# --------------------------------------------------
# 7.5 闭包
print('*' * 50)
# 闭包指延申了作用域的函数,其中包含函数定义体中引用、但不在定义体中定义的非全局变量


# avg函数,作用是计算不断增加的系列值的均值
# 初学者用类实现,计算移动平均值的类
class Average(object):
    def __init__(self):
        self.series = []

    def __call__(self, new_value):
        self.series.append(new_value)
        total = sum(self.series)
        return total/len(self.series)


avg = Average()
print(avg(10))
print(avg(11))
print(avg(12))


# 用函数实现,计算移动平均值的高阶函数
def make_average():
    series = []

    def average(new_value):
        series.append(new_value)
        total = sum(series)
        return total/len(series)
    return average


avg = make_average()
print(avg(10))
print(avg(11))
print(avg(12))

# 这两个示例有共通之初:调用Average()或make_average()得到一个可调用对象avg,它会更新历史值然后计算均值
# 前者,avg是Average的实例,后者，avg是内部函数average
# Average类的实例属性avg.series存储历史值
# series是make_average函数的局部变量,函数定义时初始化了series,在调用average时
# make_average函数已经返回了,而它的本地作用域也一去不复返了,average函数中,series时自由变量
# 自由变量:指代未在本地作用域中绑定的变量

# 审查make_average创建的函数
print(avg.__code__.co_varnames)
print(avg.__code__.co_freevars)
print(avg.__closure__)
print(avg.__closure__[0].cell_contents)

# 综上,闭包是一种函数,它会保留定义函数时存在的自由变量的绑定
# 这样调用函数时,虽然定作用域不可用,但仍能使用那些绑定
# 注:只有嵌套在其他函数中的函数才可能需要处理不再全局作用域中的外部变量


# --------------------------------------------------
# 7.6 nonlocal声明
print('*' * 50)


# 上述make_average函数不足在于,每次新增时需要重新运算
# 计算移动平均值的高阶函数,不保存所有历史值,但有缺陷
"""
def make_average():
    count = 0
    total = 0

    def average(new_value):
        count += 1
        total += new_value
        return total/count
    return make_average()

缺陷->当count是数字或任何不可边类型时,count += 1语句的作用其实与count = count + 1一样
      因此,average的定义体中为count赋值了,这回把count变成局部变量,total也一样
"""


# 为了解决这个问题,Python3中引入了nonlocal声明,它的作用时把变量标记为自由变量
# 即使在函数中为变量赋予新值了,也会变成只有变量
def make_average():
    count = 0
    total = 0

    def average(new_value):
        nonlocal count, total
        count += 1
        total += new_value
        return total/count
    return average


avg = make_average()
print(avg(100))
print(avg(110))
print(avg(120))


# --------------------------------------------------
# 7.7 实现一个简单的装饰器
print('*' * 50)


# 一个简单的装饰器,输出函数的运行时间
def clock(func):
    def cloked(*args):  # 定义内部函数clocked,它接受任意个数定位参数
        t_0 = time.perf_counter()
        result = func(*args)  # 这行代码可用,因为cloked的闭包中包含自由变量func
        elapsed = time.perf_counter() - t_0
        name = func.__name__
        arg_str = ','.join(repr(arg) for arg in args)
        print(f'[{elapsed:.8f}s] {name}({arg_str}) -> {result}')
        return result
    return cloked  # 返回内部函数,取代被装饰的函数


@clock
def snooze(seconds):
    time.sleep(seconds)


@clock
def factorial(n):
    return 1 if n < 2 else n*factorial(n-1)


if __name__ == '__main__':
    print('-' * 10, 'Calling snooze(.123)', '-' * 10)
    snooze(.123)
    print('-' * 10, 'Calling factorial(10)', '-' * 10)
    factorial(10)


# 工作原理
""""
@clock
def factorial(n):
    return 1 if n < 2 else n*factorial(n-1)
等价于:
def factorial(n):
    return 1 if n < 2 else n*factorial(n-1)
factorial = clock(factorial)
在两个示例中,factorial作为func参数传给clock,然后clock函数返回clocked函数
Python解释器会在背后把clocked赋值给factorial
"""
print(factorial.__name__)  # factorial函数保存的是clocked函数的引用
# 每次运行factorial函数,实际上运行的是clocked函数
# clocked大致做以下几件事:
# · 记录初始时间t_0
# · 调用原来的factorial函数,保存结果
# · 计算经过的时间
# · 格式化收集的数据并打印出来
# · 返回第2步保存的结果

# 这时装饰器的典型行为:把被装饰的函数替换成新函数,两者接受相同的参数
# 而且返回被装饰的函数本该返回的值,同时还会做额外的操作


# clock装饰器存在几个缺点:不支持关键字参数,而且遮盖力被装饰函数的__name__和__doc__属性
# 改进的clock装饰器
def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t_0 = time.perf_counter()
        result = func(*args, **kwargs)
        elpased = time.perf_counter() - t_0
        name = func.__name__
        arg_lst = []
        if args:
            arg_lst.append(','.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_lst.append(','.join(pairs))
        arg_str = ','.join(arg_lst)
        print(f'[{elpased:.8f}s] {name}({arg_str}) -> {result}')
        return result
    return clocked


# --------------------------------------------------
# 7.8 标准库中的装饰器
print('*' * 50)
# Python内置了三个用于装饰方法的函数:property,classmethod和staticmethod
# 另一个常用的装饰器是functools.wraps,它的作用是协助构建行为良好的装饰器
# 标准库最值得关注的两个装饰器是lru_cache和全新singledispatch,都在functools模块下


# 1).使用functools.lru_cache做备忘
# 生成第n个fibonacci数,递归方式非常耗时
@clock
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-2) + fibonacci(n-1)


print(fibonacci(6))


# 使用缓存实现,速度更快
@functools.lru_cache()
@clock  # 这里叠放了装饰器,@lru_cache()应用到@clock返回的函数上
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-2) + fibonacci(n-1)


print(fibonacci(60))

# 除了优化递归算法外,lru_cache在从Web中获取信息的应用中也能发挥巨大作用
# lru_cache(maxsize=128, typed=False)
# maxsize参数指定存储多少个调用的结果,缓存满了后,旧的结果会被扔掉,为了得到最佳性能,maxsize因设为2的幂
# typed参数如果设定为True,把不同参数类型得到的结果分开保存,即通常认为相等的浮点数和整数参数分开(1和1.0)


# 2).单分派反函数
# 开发一个调试Web应用的工具,我们想生成HTML,显示不同类型的Python对象
# 我们可能些这样的函数:
def htmlize(obj):
    content = html.escape(repr(obj))
    return f'<pre>{content}</pre>'


# 这个哈桑农户适用于任何Python类型,但我们想做扩展时,让它使用特殊的方式显示某些类型
# · str:把内部的转行符替换为'<br>\n';不使用<pre>,而是用<p>
# · int:以十进制和十六进制显示数字
# · list:输出一个HTML列表,根据各个元素的类型进行格式化
# 如今的结果以及我们想要的结果(后面标注是想要的结果形式)
print(htmlize({1, 2, 3}))  # '<pre>{1, 2, 3}</pre>'
print(htmlize(abs))  # '<pre>&lt;built-in function abs&gt;</pre>'
print(htmlize('Heimlize & Co.\n- a game'))  # '<p>Heimlich &amp; Co.<br>\n- a game</p>'
print(htmlize(42))  # '<pre>42 (0x2a)</pre>'
print(htmlize(['alpha', 66, {3, 2, 1}]))
# <ul>
# <li><p>alpha</p></li>
# <li><pre>66 (0x42)</pre></li>
# <li><pre>{1, 2, 3}</pre></li>
# </ul>


# sinledispatch创建一个自定义的htmlize.register装饰器,把多个函数绑在一起组成一个反函数
@functools.singledispatch  # 标记处理object类型的基函数
def htmlize(obj):
    content = html.escape(repr(obj))
    return f'<pre>{content}</pre>'


@htmlize.register(str)  # 各个专门函数使用@base_function.register(type)装饰
def _(text):  # 专门函数的名称无关紧要;_是个不错的选择
    content = html.escape(text).replace('\n', '<br>\\n')
    return f'<p>{content}</p>'


@htmlize.register(numbers.Integral)  # 为每个需要特殊处理的类型注册一个函数,numbers.Integral是int的虚拟超类
def _(n):
    return f'<pre>{n} (0x{n:x})</pre>'


@htmlize.register(tuple)  # 可以叠放多个register装饰器,让统一和函数支持不同类型
@htmlize.register(collections.abc.MutableSequence)
def _(seq):
    inner = '</li>\n<li>'.join(htmlize(item) for item in seq)
    return '<ul>\n<li>' + inner + '</li>\n</ul>'
# singledispatch机制的一个显著特征是,你可以在系统的任何地方和任何模块中注册专门函数
# 若后来在新的模块中定义新的类型,可以轻松地添加一个新的专门函数来处理那个类型


print('-' * 10)
print(htmlize({1, 2, 3}))  # '<pre>{1, 2, 3}</pre>'
print(htmlize(abs))  # '<pre>&lt;built-in function abs&gt;</pre>'
print(htmlize('Heimlize & Co.\n- a game'))  # '<p>Heimlich &amp; Co.<br>\n- a game</p>'
print(htmlize(42))  # '<pre>42 (0x2a)</pre>'
print(htmlize(['alpha', 66, {3, 2, 1}]))
# <ul>
# <li><p>alpha</p></li>
# <li><pre>66 (0x42)</pre></li>
# <li><pre>{1, 2, 3}</pre></li>
# </ul>


# --------------------------------------------------
# 7.9 叠放装饰器
print('*' * 50)
# 把@d1和@d2两个装饰器按顺序应用到f函数上,作用相当于f = d1(d2(f))


# --------------------------------------------------
# 7.10 参数化装饰器
print('*' * 50)
# registration的删减版
registry = []


def register(func):
    print(f'Running register({func})')
    registry.append(func)
    return func


@register
def f1():
    print('Running f1()')


print('Running main()')
print('registry ->', registry)
f1()

# 1).一个参数化的注册装饰器
# 为了便于启动或禁用register执行的函数注册工能,给它提供一个可选的active参数
# 为了接受参数,新的register装饰器必须作为函数调用
registry = set()  # registry是一个set对象,这样添加和删除函数的速度更快


def register(active=True):  # register接受一个看选的active关键字参数
    def decorate(func):  # decorate这个内部的函数是真正的装饰器
        print(f'Running register(active={active}) -> decorate({func})')
        if active:  # 只有active值为True时,才注册func
            registry.add(func)
        else:
            registry.discard(func)  # func函数若在registry中,把它从中删除
        return func  # decorate是装饰器,必须返回一个函数
    return decorate  # register是装饰器工厂函数,因此返回decorate


@register(active=False)
def f1():
    print('Running f1()')


@register()  # 即使不传入参数,register也要作为函数调用,加()
def f2():
    print('Running f2()')


def f3():
    print('Running f3()')


print('-' * 10)
import registration_param
print(registration_param.registry)

# 如果不使用@句法，那就要像常规函数那样使用register;若想把f添加到registry中
# 则装饰f函数的句法是register()(f);不想添加(或把它删除)的话,句法是register(active=False)(f)
print('-' * 10)
from registration_param import *
print(registry)
print(register()(f3))
print(registry)
print(register(active=False)(f2))
print(registry)

# 2).参数化clock装饰器
# 本节再次探讨clock装饰器,为它添加一个功能;让用户传入一个格式字符串,控制被装饰函数的输出
print('-' * 10)
DEFAULT_FMT = '[{elapsed:0.8f}s] {name}({args}) -> {result}'


def clock(fmt=DEFAULT_FMT):  # clock是参数化装饰器工厂函数
    def decorate(func):  # decorate是真正的装饰器
        def cloked(*_args):  # clocked包装被装饰的函数
            t_0 = time.perf_counter()
            _result = func(*_args)  # 是被装饰函数返回的真正结果
            elapsed = time.perf_counter() - t_0
            name = func.__name__
            args = ','.join(repr(arg) for arg in _args)  # _args是clocked的参数,args是用于显示的字符串
            result = repr(_result)  # result是_result的字符串表示形式,用于显示
            print(fmt.format(**locals()))  # **locals()是为了在fmt中引用clocked的局部变量
            return _result  # clocked会取代被装饰的函数,因此它应该返回被装饰的函数返回的值
        return cloked  # decorate返回clocked
    return decorate  # clock返回decorate


@clock()
def snooze(seconds):
    time.sleep(seconds)


for i in range(3):
    snooze(0.123)


@clock('{name}:{elapsed:.8f}s')
def snooze(seconds):
    time.sleep(seconds)


for i in range(3):
    snooze(0.5)


@clock('{name}({args}):dt={elapsed:.3f}s')
def snooze(seconds):
    time.sleep(seconds)


for i in range(3):
    snooze(0.5)
