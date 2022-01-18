# registration.py模块
registry = []  # registry保存被@register装饰的函数引用


def register(func):  # register的参数时一个函数
    print('Running register(%s)' % func)  # 为了演示,显示被装饰的函数
    registry.append(func)  # 把func存入registry
    return func  # 返回func,必须返回函数,这里返回的函数与通过参数传入的一样


@register
def f1():
    print('Running f1()')


@register
def f2():
    print('Running f2()')


def f3():
    print('Running f3()')


def main():
    print('Running main()')
    print('registry ->', registry)
    f1()
    f2()
    f3()


if __name__ == '__main__':
    main()
# register在模块中其他函数之前运行（两次）
# 加载模块后,registry中有两个被装饰函数的引用
# f1和f2及f3只在main明确调用它们时才执行
