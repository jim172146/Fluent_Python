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