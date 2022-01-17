__author__ = 'fmy'

import array
import math

"符合Python风格的对象"
# 本章包含以下话题:
# · 支持用于生成对象其他表示形式的内置函数(如repr(),bytes()等等)
# · 使用一个类方法实现备选构造方法
# · 扩展内置的format()函数和str.format()方法使用的格式微语言
# · 实现只读属性
# · 把对象变为可散列的,以便在集合中及作为dict的键使用
# · 利用__slot__节省内存

# 并讨论两个概念:
# · 如何以及何时使用@classmethod和@staticmethod装饰器
# · Python的私有属性和受保护属性的用法、约定和局限


# --------------------------------------------------
# 9.1 对象表示方式
print('*' * 50)
# repr():以便开发者理解的方式返回对象的字符串表示形式
# str():以便用户理解的方式返回对象的字符串表示形式
# 要实现__repr__和__str__特殊方法,为repr()和str()提供支持
# 为了给对象提供其他的表示形式,还会用到另外两个特殊方法:__bytes__和__format__
# __bytes__方法和__str__方法类似,bytes()函数用于获取对象的字节序列表示形式
# __format__方法会被内置的format()函数和str.format()方法调用


# --------------------------------------------------
# 9.2 再谈向量类
print('*' * 50)


# Vector2d实例有多种表示形式
class Vector2d:
    typecode = 'd'  # typecode是类属性,在Vector2d实例和字节序列之间转换时使用

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self):
        # 定义__iter__方法,把实例编程可迭代的对象,这样才能拆包,如(x, y = my_vector)
        return (i for i in (self.x, self.y))

    def __repr__(self):
        class_name = type(self).__name__
        # __repr__方法使用{!r}获取各个分量的表示形式,然后插值,构成一个字符串
        # 因为Vector2d是可迭代的对象,所以*self会把x和y分量提供给format函数
        return '{}({!r},{!r})'.format(class_name, *self)

    def __str__(self):
        # 从可迭代的Vector2d实例中获取得到一个元组,显示一个有序对
        return str(tuple(self))

    def __bytes__(self):
        # 为了生成字节序列,我们把typecode转换成字节序列
        # 然后迭代Vector2d实例,得到一个数组,再把数组转换成字节序列
        return (bytes([ord(self.typecode)])) + \
               bytes(array.array(self.typecode, self))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(abs(self))


v1 = Vector2d(3, 4)
print(f'v1.x={v1.x}, v1.y={v1.y}')
x, y = v1
print(f'x={x},y={y}')
print(v1)
# v1  Vector2d:3.0,4.0
v1_clone = eval(repr(v1))
print(v1 == v1_clone)
octets = bytes(v1)
# octets  b'd\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x10@'
print(octets)
print(abs(v1))
print(bool(v1), bool(Vector2d(0, 0)))


# --------------------------------------------------
# 9.3 备选构造方法
print('*' * 50)


@classmethod  # 类方法使用classmethod装饰器修饰
def frombytes(cls, octets):  # 不用传入self参数,相反,要通过cls传入类本身
    typecode = chr(octets[0])  # 从第一个字节中读取typecode
    # 使用传入的octets字节序列创建一个memoryview,然后使用typecode转换
    memv = memoryview(octets[1:]).cast(typecode)
    return cls(*memv)  # 拆包转换后的memoryview,得到构造方法所需的一对参数


# --------------------------------------------------
# 9.4 classmethod与staticmethod
print('*' * 50)


# 比较classmethod与staticmethod的行为
class Demo:
    @classmethod
    def klassmeth(*args):
        return args  # klassmeth返回全部参数

    @staticmethod
    def statmeth(*args):
        return args  # statmeth也是


print(Demo.klassmeth())  # 不管如何调用Demo.klassmeth,它的第一个参数始终是Demo类
print(Demo.klassmeth('spam'))
print(Demo.statmeth())  # Demo.statmeth的行为与普通的函数相似
print(Demo.statmeth('spam'))


# --------------------------------------------------
# 9.5 格式化显示
print('*' * 50)
