__author__ = 'fmy'

import contextlib
import mirror

"上下文管理器和else块"
# 其他语言中不常见的一些流程控制特性:
# --with语句和上下文管理器
# --for,while和try语句的else子句
# with语句会设置一个临时的上下文,交给上下文管理器对象控制并且负责清理上下文


# --------------------------------------------------
# 15.1 先做这个,在做那个:if语句之外的else块
print('*' * 50)
# else子句不仅能在if语句中使用,还能在for、while和try语句中使用
# for:仅当for循环运行完毕时才运行else块
# while:仅当while循环因为条件为假值而退出时才运行else块
# try:仅当try块中没有异常抛出时才运行else块
"""
my_list =[]
for item in my_list:
    if item.flavor == 'banana':
        break
else:
    raise ValueError('No banana flavor found!')



try:
    dangerous_call()
    after_call()
except OSError:
    log('OSError...')


try:
    dangerous_call()
except OSError:
    log('OSError...')
else:
    after_call()
# try块防守的是dangerous_call()可能出现的错误而不是 after_call()
# 而且很明显,只有try块不抛出异常,才会执行after_call()
"""

# --------------------------------------------------
# 15.2 上下文管理器和with块
print('*' * 50)
# 上下文管理器对象存在的目的是管理with语句
# 就像迭代器的存在是为了管理for语句一样

# 上下文管理器协议包含__enter__和__exit__两个方法
# 最常见的例子是确保关闭文件对象
# 执行with后面的表达式得到的结果是上下文管理器对象
with mirror.LookingGlass() as what:
    print('Alice, Kitty and Snowdrop')  # 打印出的内容是反向的
    print(what)
print(what)

# 解释器调用__enter__方法时,除了隐式的self之外,不会传入任何参数
# 传给 __exit__方法的三个参数列举如下:
# exc_type:异常类
# exc_value:异常示例
# traceback:traceback对象

# 在 with 块之外使用 LookingGlass 类
manage = mirror.LookingGlass()
print(manage)
monster = manage.__enter__()
print(monster == 'YKCOWREBBAJ')
print(monster)
print(manage)
manage.__exit__(None, None, None)
print(monster)


# --------------------------------------------------
# 15.3 contextlib模块中的实用工具上下文管理器和with块
print('*' * 50)
# 除了前面提到的redirect_stdout函数,contextlib模块中还有一些类和其他函数,使用范围更广
# closing:
# --如果对象提供了close()方法,但没有实现 __enter__/__exit__ 协议
# --那么可以使用这个函数构建上下文管理器
# suppress:
# --构建临时忽略指定异常的上下文管理器
# @contextmanager:
# --这个装饰器把简单的生成器函数变成上下文管理器
# --这样就不用创建类去实现管理器协议了
# ContextDecorator:
# --这是个基类,用于定义基于类的上下文管理器
# --这种上下文管理器也能用于装饰函数,在受管理的上下文中运行整个函数
# ExitStack:
# --这个上下文管理器能进入多个上下文管理器
# --with块结束时,ExitStack按照后进先出的顺序调用栈中各个上下文管理器的__exit__方法
# --如果事先不知道with块要进入多少个上下文管理器,可以使用这个类


# --------------------------------------------------
# 15.4 使用@contextmanager
print('*' * 50)


# 使用生成器实现的上下文管理器
@contextlib.contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    # 产出一个值,这个值会绑定到with语句中as子句的目标变量上
    # 执行with块中的代码时,这个函数会在这一点暂停
    yield 'JABBERWOCKY'
    sys.stdout.write = original_write


with looking_glass() as what:
    print('Alice, Kitty and Snowdrop')
    print(what)
print(what)
# ontextlib.contextmanager装饰器会把函数包装成实现__enter__和__exit__方法的类
# 这个类的__enter__方法有如下作用:
# · 调用生成器函数,保存生成器对象(这里把它称为gen)
# · 调用next(gen),执行到yield关键字所在的位置
# · 返回next(gen)产生的值,以便把产出的值绑定到with/as语句中的目标变量上
# with块终止时,__exit__方法会做以下几件事:
# · 检查有没有把异常传给exc_type：如果有，调用gen.throw(exception)
#   --在生成器函数定义体中包含yield关键字的那一行抛出异常
# · 否则调用next(gen),继续执行生成器函数定义体中yield语句之后的代码


# 基于生成器的上下文管理器,实现了异常处理
@contextlib.contextmanager
def looking_glass():
    import sys
    original_write = sys.stdout.write

    def reverse_write(text):
        original_write(text[::-1])

    sys.stdout.write = reverse_write
    msg = ''
    try:
        yield 'JABBERWOCKY'
    except ZeroDivisionError:
        msg = 'Please DO NOT divide by zero!'
    finally:
        sys.stdout.write = original_write
        if msg:
            print(msg)


# --------------------------------------------------
# 15.5 本章小结
print('*' * 50)
# 本章从简单的话题入手,先讨论了for、while和try语句的else子句
# 讨论了上下文管理器和 with 语句的作用
# 实现了一个上下文管理器——含有__enter__/__exit__方法的LookingGlass类,说明了如何在__exit__方法中处理异常
# with不仅能管理资源,还能用于去掉常规的设置和清理代码,或者在另一个过程前后执行的操作
# 分析了标准库中contextlib模块里的函数
# --其中@contextmanager装饰器能把包含一个yield语句的简单生成器变成上下文管理器
