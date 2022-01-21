__author__ = 'fmy'

import collections
import io
import numbers
import tkinter

"继承的优缺点"
# 对Python而言十分重要的两个细节:
# · 子类化内置类型的缺点
# · 多重继承和方法解析顺序

# --------------------------------------------------
# 12.1 子类化内置类型很麻烦
print('*' * 50)


# 内置类型不会调用用户定义的类覆盖的特殊方法
# 内置类型dict的__init__和__update__方法会忽略我们覆盖的__setitem__方法
class DoppelDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)


dd = DoppelDict(one=1)
print(repr(dd))
dd.update(three=3)
print(repr(dd))
dd['two'] = 2  # []运算符会调用我们覆盖的__setitem__方法,按预期那样工作
print(repr(dd))


# dict.update会忽略AnswerDict.__getitem__方法
class AnswerDict(dict):
    def __getitem__(self, key):
        return 42


ad = AnswerDict(a='foo')
print(ad['a'])
d = {}
d.update(ad)
print(d['a'])
print(d)
# dick.update方法忽略了AnswerDict.__getitem__方法

# 直接子类化内置类型容易出错,因为内置类型的方法通常会忽略用户覆盖的方法
# 不要子类化内置类型,用户自己定义的类应该继承collections模块中的类


# adoppelDict2和AnswerDict2能像预期那样使用,因为它们扩展的是UserDict而不是dict
class DoppelDict2(collections.UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, [value] * 2)


print('-' * 10)
dd = DoppelDict2(one=1)
print(repr(dd))
dd.update(three=3)
print(repr(dd))
dd['two'] = 2
print(repr(dd))


class AnswerDict2(collections.UserDict):
    def __getitem__(self, key):
        return 42


ad = AnswerDict2(a='foo')
print(ad['a'])
d = {}
d.update(ad)
print(d['a'])
print(d)


# --------------------------------------------------
# 12.2 多重继承和方法解析顺序
print('*' * 50)


# 任何实现多重继承的语言都要处理潜在的命名冲突
class A:
    def ping(self):
        print('ping:', self)


class B(A):
    def pong(self):
        print('pong:', self)


class C(A):
    def pong(self):
        print('PONG:', self)


class D(B, C):
    def ping(self):
        super().ping()
        print('post-ping:', self)

    def pingpong(self):
        self.ping()
        super().ping()
        self.pong()
        super().pong()
        C.pong(self)


d = D()
d.ping()
d.pong()  # 直接调用.pong()运行的是B类中的方法
C.pong(d)  # 超类中的方法都可以直接调用,此时要把实例作为显式参数传入
print('-' * 10)
d.pingpong()
# Python能区分d.pong()调用的哪个方法,是因为Python会按照特定的顺序遍历继承图,这个循序是方法解析循序
# 类都有一个名为__mro__的属性,它的值是一个元组,按照方法解析顺序列出各个超类,从当前类一直向上,直到object 类
print(D.__mro__)

# 若想把方法调用委托给超类,推荐的方式是使用super()函数

# 查看几个类的__mro__属性
print(bool.__mro__)


def print_mro(cls):  # 使用更紧凑的方式显示解析循序
    print('->'.join(c.__name__ for c in cls.__mro__))


print_mro(bool)
print_mro(numbers.Integral)
print_mro(io.BytesIO)
print_mro(io.TextIOWrapper)
print_mro(tkinter.Text)


# --------------------------------------------------
# 12.3 多重继承的真实作用
print('*' * 50)
# 看看Tkinterd解析顺序
print_mro(tkinter.Toplevel)
print_mro(tkinter.Widget)
print_mro(tkinter.Button)
print_mro(tkinter.Entry)
print_mro(tkinter.Text)


# --------------------------------------------------
# 12.4 处理多重继承
print('*' * 50)
# 一些理论知识经验:
# 1).把接口继承和实现继承区分开
# 使用多重继承,一定要明确一开始为什么创建子类
# · 继承接口,创建子类型,实现'是什么'关系
# · 继承实现,通过重用避免代码重复
# 2).使用抽象基类显示表示接口
# 若类的作用是定义接口,应该明确把它定义为抽象基类
# 3).通过混入重用代码
# 若类的作用是为多个不相关的子类提供方法实现,从而实现重用,但不体现'是什么'关系
# 应该把类明确地定义为混入类
# 4).在名称中明确指明混入
# 因为Python没有把类声明为混入的正规方式,所以强烈推荐把名称中如...Mixin后缀
# 5).抽象基类可以作为混入,反过来不可以
# 6).不要子类化多个具体类
# 具体类可以没有,或最多只有一个具体超类.
# 即具体类的超类中除了这一具体超类之外,其余的都是抽象基类或混入
# 7).为用户提供聚合类
# 若抽象基类或混入的组合非常有用,那就提供一个类,使用易于理解的方式把他们结合起来
# 8).优先使用对象组合,而不是类继承


# --------------------------------------------------
# 12.5 一个现代示例:Django通用视图中的混入
print('*' * 50)
# 在Django中,视图是可调用的对象,它的参数是表示HTTP请求的对象,返回值是一个表示HTTP响应的对象
# 我们关注的是这些响应对象,响应可以是简单的重定向,没有主体内容,也可以是复杂的内容
# 起初Django提供一系列函数(通用视图),实现常见的用例
# 最初的通用视图是函数,不能扩展,之后引入基于类的视图,通过基类,混入和具体类提供了一些通用视图类


# --------------------------------------------------
# 12.6 本章小结
print('*' * 50)
# 内置类型的原生方法使用C语言实现,不会调用子类中覆盖的方法
# 因此定值list,dict或str类型时,子类化UserList,UserDict或UserString更简单
# __mro__类属性蕴藏方法解析顺序,这一机制保证继承的方法不产生冲突
# __super__()函数会按照__mro__属性给出的顺序调用超类的方法
