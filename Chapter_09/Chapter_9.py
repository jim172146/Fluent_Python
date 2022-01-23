__author__ = 'fmy'

import array
import math
import datetime

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

    # def __format__(self, fmt_spec=''):
    #     components = (format(c, fmt_spec) for c in self)
    #     return '({}, {})'.format(*components)

    def angle(self):
        return math.atan2(self.y, self.x)

    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('p'):
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)


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
# 内置的format()函数和str.format()方法把各个类型的格式化方式委托给相应的
# .__format__(format_spec)方法,format_spec是格式说明符,它是：
#  format(my_obj, format_spec)的第二个参数
#  str.format()方法的格式字符串,{}里代换字段中冒号后面的部分
brl = 1/2.43
print(brl)
print(format(brl, '0.4f'))
print('1 BRL = {rate:0.2f} USD'.format(rate=brl))
# 这里的rate子串是字段名称,仅仅决定把.format()的哪个参数传给代换字段

# 格式规范微语言为一些内置类型提供专用的表示代码
print(format(42, 'b'))
print(format(2/3, '.1%'))
# 格式规范微语言是课扩展的
now = datetime.datetime.now()
print(format(now, '%H:%M:%S'))
print("It's now {:%I:%M:%p}".format(now))
# 若没定义__format__方法,从object继承的方法会返回str(my_object)
# 我们为Vector2d类定义了__str__方法,因此:
v1 = Vector2d(3, 4)
print(format(v1))
# 若传入格式说明符,object.__format__方法会抛出TypeError
# print(format(v1, '.3f'))

# 实现自己的微语言来解决这个问题
"""
def __format__(self, fmt_spec=''):
    components = (format(c, fmt_spec) for c in self)
    return '{}, {}'.format(*components)
"""
print(format(v1, '.3e'))

# 实现极坐标的显示格式
"""
求得极坐标的角度
def angle(self):
    return math.atan2(self.y, self.x)

实现极坐标
def __format__(self, fmt_spec=''):
    if fmt_spec.endswith('p'):
        fmt_spec = fmt_spec[:-1]
        coords = (abs(self), self.angle())
        outer_fmt = '<{}, {}>'
    else:
        coords = self
        outer_fmt = '({}, {})'
    components = (format(c, fmt_spec) for c in coords)
    return outer_fmt.format(*components)             
"""
print(format(Vector2d(1, 1), 'p'))
print(format(Vector2d(1, 1), '0.3fp'))
print(format(Vector2d(1, 1), '0.3ep'))


# --------------------------------------------------
# 9.6 可散列的Vector2d
print('*' * 50)
# 目前,Vector2d实例是不可散列的,因此不能放入集合(set)中
v1 = Vector2d(1, 1)
# print(hash(v1))  TypeError: unhashable type: 'Vector2d'
# print(set([v1]))  TypeError: unhashable type: 'Vector2d'

# 为了把实例变成可散列的,必须使用__hash__方法(还需__eq__方法, 已经实现)
# 此外,还要让向量不可变,如现在 v1.x = 7 是可变的


# 这里只给出了让Vector2d不可变的代码
class Vector:
    typecode = 'd'

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property  # property装饰器把读值方法标记为特性
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        # 需要读取x,y分量的方法可以保持不变,通过self.x和self.y读取公开特性,而不读取私有属性
        return (i for i in (self.x, self.y))


# Vector2d类的__hash__方法代码
def __hash__(self):
    return hash(self.x) ^ hash(self.y)


# Vector2d的完整代码
class Vector2d:
    # __slots__ = ('__x', '__y')

    typecode = 'd'  # typecode是类属性,在Vector2d实例和字节序列之间转换时使用

    def __init__(self, x, y):
        self.__x = float(x)
        self.__y = float(y)

    @property  # property装饰器把读值方法标记为特性
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __iter__(self):
        # 需要读取x,y分量的方法可以保持不变,通过self.x和self.y读取公开特性,而不读取私有属性
        return (i for i in (self.x, self.y))

    def __len__(self):
        return 2

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    def __repr__(self):
        class_name = type(self).__name__
        # __repr__方法使用{!r}获取各个分量的表示形式,然后插值,构成一个字符串
        # 因为Vector2d是可迭代的对象,所以*self会把x和y分量提供给format函数
        return '{0}({1},{2})'.format(class_name, self.x, self.y)

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

    def angle(self):
        return math.atan2(self.y, self.x)

    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('p'):
            fmt_spec = fmt_spec[:-1]
            coords = (abs(self), self.angle())
            outer_fmt = '<{}, {}>'
        else:
            coords = self
            outer_fmt = '({}, {})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(*components)

    @classmethod  # 类方法使用classmethod装饰器修饰
    def frombytes(cls, octets):  # 不用传入self参数,相反,要通过cls传入类本身
        typecode = chr(octets[0])  # 从第一个字节中读取typecode
        # 使用传入的octets字节序列创建一个memoryview,然后使用typecode转换
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(*memv)  # 拆包转换后的memoryview,得到构造方法所需的一对参数


# 测试Vector2d
v1 = Vector2d(3, 4)
print(v1)
x1, y1 = v1
print(f'(x={x1}, y={y1})')
# v1  Vector2d(3,4)
v1_clone = eval(repr(v1))
print(repr(v1))
print(v1 == v1_clone)
octets = bytes(v1)
print(octets)
print(abs(v1))
print(bool(v1), bool(Vector2d(0, 0)))
print(repr(v1_clone))
print('-' * 10)
print(format(v1))
print(format(v1, '.2f'))
print(format(v1, '.3e'))
print(Vector2d(0, 0).angle())
print(Vector2d(1, 0).angle())
epsilon = 8 ** -8
print((Vector2d(0, 1).angle() - math.pi/2) < epsilon)
print((Vector2d(1, 1).angle() - math.pi/4) < epsilon)
print('-' * 10)
print(format(Vector2d(1, 1), 'p'))
print(format(Vector2d(1, 1), '.3ep'))
print(format(Vector2d(1, 1), '.5fp'))
print('-' * 10)
print(v1.x, v1.y)
# v1.x = 300  AttributeError: can't set attribute 'x'
v1 = Vector2d(3, 4)
v2 = Vector2d(3.1, 4.2)
print(f'hash(v1):{hash(v1)}\n'
      f'hash(v2):{hash(v2)}')
print(f'len(set([v1, v2]))={len(set([v1, v2]))}')
print('-' * 10)
print(Vector2d.frombytes(b'd\x00\x00\x00\x00\x00\x00\x08@\x00\x00\x00\x00\x00\x00\x10@'))


# --------------------------------------------------
# 9.7 Python的私有属性和'受保护的'属性
print('*' * 50)
# 私有属性的名称会被'改写',在前面加上下划线和类名
"""
Vector2d的__slots__属性中没有__dict__
v1 = Vector2d(3, 4)
print(v1.__dict__)
print(v1._Vector2d__x)
"""


# --------------------------------------------------
# 9.8  使用__slots__类属性节省空间
print('*' * 50)
""" 
默认情况下,Python在各个实例中名为__dict__的字典里存储实例属性
为了使用底层的散列表提升访问速度,字典会消耗大量内存
如果要处理数百万个属性不多的实例,通过 __slots__ 类属性,能节省大量内存
方法是让解释器在元组中存储实例属性,而不用字典
"""
# 继承自超类的__slots__属性没有效果,Python只会使用各个类中定义的__slots__ 属性
"""
class Vector2d:
    __slots__ = ('__x', '__y')
    typecode = 'd'
"""
# 类中定义__slots__属性的目的在于告诉解释器,类中的所有实例属性全在这
# 若要处理数百万个对象,应该使用NumPy数组,NumPy数组能高效使用内存

# 在类中定义__slots__属性之后,实例不能再有__slots__中所列名称之外的其他属性
# 若类定义了__slots__属性且想把实例作为弱引用的目标,那么要把'__weakref__'添加到__slots__中

# __slots__的问题
# · 每个子类都要定义__slots__属性,因为解释器会忽略继承的__slots__属性
# · 实例只能拥有__slots__中列出的属性,除非把__dict__加入__slots__中(违背初衷)
# · 不把__weakref__加入__slots__中,实例不能作为弱引用的目标


# --------------------------------------------------
# 9.9 覆盖属性
print('*' * 50)
# 类属性可用于为实例属性提供默认值
# Vector2d实例没有typecode属性,所以self.typecode默认获取Vector2d.typecode类属性的值
# 如果为不存在的实例属性赋值,会新建实例属性
# Vector2d.typecode属性的默认值是'd',及转换成字节序列时使用8字节双精度浮点数表示向量各个分量
# 若把typecode改成'f',即转换时采用4字节单精度浮点数表示各个分量
v1 = Vector2d(1.1, 2.2)
dumpd = bytes(v1)
print(dumpd)
print(len(dumpd))
v1.typecode = 'f'

dumpf = bytes(v1)
print(dumpf)
print(len(dumpf))
print(Vector2d.typecode)


# ShortVector2d时Vector2d的子类,只用于覆盖typecode的默认值
class ShortVector2d(Vector2d):
    typecode = 'f'


sv = ShortVector2d(1/11, 1/27)
print(sv)
print(len(bytes(sv)))


# --------------------------------------------------
# 9.10 本章小结
print('*' * 50)
# 本章讲了这几种特殊方法:
# · 所有用于获取字符串和字节序列表示形式的方法:__repr__,__str__,__format__和__bytes__
# · 把对象转换成数字的几种方法:__abs__,__bool__,__hash__
# · 用于测试字节序列转换和支持散列(连同__hash__方法)__eq__运算符
# 同时为了转换成字节序列,外面还实现了备选方法,即Vector2d.frombytes()
# 讨论了@classmethod(十分有用)和@staticmethod(不太有用)两个装饰器
# 格式规范微语言是可扩展的
# 为了可散列话,外面先把x和y设为私有属性,再以只读特性公开,随后外面实现__hash__方法
# 讨论了如何使用__slots__节省内存
# 说明了通过访问实例属性覆盖类属性
"要构建符合Python风格的对象,就要观察真正的Python对象的行为"
