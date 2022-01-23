__author__ = 'fmy'

import array
import functools
import itertools
import math
import numbers
import operator
import reprlib
import sys

"序列的修改、散列和切片"
# 在Vector2d基础上,拓展Vector的功能:
# · 基本的序列协议--__len__和__getitem__
# · 正确表述拥有很多元素的实例
# · 适当的切片支持,用于生成新的Vector实例
# · 综合各个元素的值计算散列值
# · 自定义的格式语言扩展
# 我们通过__getitem__实现属性的动态存取,取代Vector2d的只读特性
# 讨论一个概念:把协议当作正式接口


# --------------------------------------------------
# 10.1 Vector类,用户定义的序列类型
print('*' * 50)
# 使用组合模式实现Vector类,不使用继承
# 向量的分量存储在浮点数组中,还将实现不可变扁平序列所需的方法
# 实现序列方法前,保证Vector类与Vector2d类兼容


# --------------------------------------------------
# 10.2 Vector类第1版:与Vector2d类兼容
print('*' * 50)
# 如果Vector实例的分量超过6个,repr()生成的字符串就会使用...省略一部分


# 第1版Vector类的实现代码
class Vector:
    typecode = 'd'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包


# reprlib.repr函数用于生成大型结构或递归结构的安全表达方式,它会限制输出字符串的长度
# 编写__repr__方法时,本可以使用reprlib.repr(list(self._components))生成简化的components显示形式
# 但是该做法会把self._cpmponents中的每个元素复制到一个列表,然后使用列表的表示形式

# 本可以让Vector继承Vector2d,但没这样做的原因如下:
# · 两个构造不兼容
# · 想把Vector类当作单独的实例,以此实现序列协议


# --------------------------------------------------
# 10.3 协议和鸭子类型
print('*' * 50)
# 在面向对象编程中,协议时非正式的接口,只在文档中定义,在代码中不定义
# Python的序列协议只需要__len__和__getitem__两个方法
# 协议是非正式的,没有强制力


# --------------------------------------------------
# 10.4 Vector类第2版:可切片的序列
print('*' * 50)


# 第2版Vector类的实现代码
class Vector:
    typecode = 'd'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        return self._components[index]


v1 = Vector([3, 4, 5])
print(f'len(v1)={len(v1)}')
print(f'v1={v1}')
print(f'v1[0]={v1[0]}, v1[1]={v1[1]}')
v7 = Vector(range(7))
print(f'v7[1:4]={v7[1:4]}')
print(f'v7={v7}')
# 目前支持切片,不过尚不完美;如果Vector实例的切片也是Vector实例而不是数组,就更好了
a = v7[1:4]
print(type(v7))
print(type(a))


# 1).切片原理
# 了解__getitem__和切片的行为
class MySeq:
    def __getitem__(self, index):
        return index


s = MySeq()
print(s[1])  # 1
print(s[1:4])  # slice(1, 4, None)
print(s[1:4:2])  # slice(1, 4, 2)
print(s[1:4:2, 9])  # (slice(1, 4, 2), 9)
print(s[1:4:2, 7:9])  # (slice(1, 4, 2), slice(7, 9, None))
# 查看slice类的属性
print(slice)
print(dir(slice))
help(slice.indices)
# indices方法开放了内置序列实现的棘手问题,用于优雅地处理缺失索引和负数索引以及长度超过目标序列的切片
# 假设有个长度为5的序列
print(slice(None, 10, 2))
print(slice(None, 10, 2).indices(5))
print(slice(-3, None, None).indices(5))
print('ABCDE'[:10:2])
print('ABCDE'[-3::])


# 2).能处理切片的__getitem__方法
class Vector:
    typecode = 'd'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        cls = type(self)  # 获取实例属性的类,供后面使用
        if isinstance(index, slice):
            return cls(self._components[index])  # 构建一个新Vector实例
        elif isinstance(index, numbers.Integral):
            return self._components[index]  # 返回_components中相应的元素
        else:
            raise TypeError(f'{cls.__name__} indices must be integers')


# 大量使用isinstance可能表明面向对象设计得不好,不过__getitem__方法中使用它处理切片是合理的
# numbers.Integral是抽象基类,instance中使用抽象基类做测试能让API更灵活更容易更新

# 测试Vector类的性能
print('-' * 10)
v7 = Vector(range(7))
print(v7[-1])
print(v7[-1:])
print(repr(v7[-1:]))
print(v7[1:4])
print(repr(v7[1:4]))
Vector([6.0])
# print(v7[1, 2])  # TypeError: Vector indices must be integers
# Vector不支持多维索引,因此索引元组或多个切片会抛出错误
# print(v7(1, 2))  # TypeError: 'Vector' object is not callable


# --------------------------------------------------
# 10.5 Vector类第3版:动态存取对象
print('*' * 50)


# __getattr__方法实现obj.x,obj.y,obj.z,obj.t前四个分量的读取
class Vector:
    typecode = 'd'
    shortcut_names = 'xyzt'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        cls = type(self)  # 获取实例属性的类,供后面使用
        if isinstance(index, slice):
            return cls(self._components[index])  # 构建一个新Vector实例
        elif isinstance(index, numbers.Integral):
            return self._components[index]  # 返回_components中相应的元素
        else:
            raise TypeError(f'{cls.__name__} indices must be integers')

    def __getattr__(self, name):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos <= len(self._components):
                return self._components[pos]
            raise AttributeError(f'{cls.__name__} object has no attribute {name}')

    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1:
            if name in cls.shortcut_names:
                error = f'readonly attribute {name}'
            elif name.islower():
                error = f"can't set attribute 'a' to 'z' in {cls.__name__}"
            else:
                error = f''
            if error:
                raise AttributeError(error)
        super().__setattr__(name, value)


# 看看目前的效果,未实现__setattr__方法的效果
"""
v5 = Vector(range(5))
print(repr(v5))
print(v5.x)
v5.x = 10
print(v5.x)
print(repr(v5))
"""
# __getattr__运作方式导致的
# · 像v5.x = 10这样的赋值之后,v5对象有了x属性,
#   因此使用v5.x获取x属性时不会调用__getattr__方法,而是直接返回绑定到v5.x上的值
# · 另一方面,__getattr__方法的实现没有考虑到self._components之外的实例属性
#   而是从这个属性中获取shortcut_names中所列的'虚拟属性'


# 实现__setattr__方法
# super()函数用于动态访问超类的方法
# 对Python这样支持多重继承的动态语言来讲,必须能这样做
# 使用这个函数把子类方法的某些任务托给超类在适当的方法


# --------------------------------------------------
# 10.6 Vector类第4版:散列和快速等值测试
print('*' * 50)
# 实现__hash__方法,加上现有的__eq__方法,会把Vector实例变成可散列的对象
# reduce的解释
print(2 * 3 * 4 * 5)
print(functools.reduce(lambda a, b: a * b, range(2, 6)))

# 计算整数0~5的累计异或的3中方式
n = 0
for i in range(1, 6):
    n ^= i
print(n)
print(functools.reduce(lambda a, b: a ^ b, range(1, 6)))
print(functools.reduce(operator.xor, range(6)))


# Vector的新版本
class Vector:
    typecode = 'd'
    shortcut_names = 'xyzt'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        # 以下方式是合适的
        if len(self) != len(other):
            return False
        for a, b in zip(self, other):
            if a != b:
                return False
        return True
        # 上式可以下称如下形式:
        # return len(self) == len(other) and all(a ==b for a, b in zip(self, other))
        # return tuple(self) == tuple(other)
        # 会认为Vector([1, 2])和(1, 2)相等,而且效率很低

    def __hash__(self):
        # hashes = (hash(x) for x in self._components)
        # hashes的另一种方式
        hashes = map(hash, self._components)
        return functools.reduce(operator.xor, hashes, 0)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        cls = type(self)  # 获取实例属性的类,供后面使用
        if isinstance(index, slice):
            return cls(self._components[index])  # 构建一个新Vector实例
        elif isinstance(index, numbers.Integral):
            return self._components[index]  # 返回_components中相应的元素
        else:
            raise TypeError(f'{cls.__name__} indices must be integers')

    def __getattr__(self, name):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos <= len(self._components):
                return self._components[pos]
            raise AttributeError(f'{cls.__name__} object has no attribute {name}')

    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1:
            if name in cls.shortcut_names:
                error = f'readonly attribute {name}'
            elif name.islower():
                error = f"can't set attribute 'a' to 'z' in {cls.__name__}"
            else:
                error = f''
            if error:
                raise AttributeError(error)
        super().__setattr__(name, value)


# reduce函数时最好提供三个函数:reduce(function, iterable, initializer)
# 这样能避免这个异常:TypeError:reduce() or empty sequence with no initial value
# 如果序列为空,initialize时返回的结果;否则,在归约中使用它作为第一个参数,因此因该使用恒等值
# 对+,|和^来说,initialize应该为0,而对*和&来说,因该为1

# zip()函数生成一个由元组构成的生成器,元组中的元素来自参数传入的各个可迭代对象
# zip函数能轻松地并行迭代两个或更多可迭代对象,它返回的元组可以拆包成变量
# zip函数名字曲子自拉链系结物(zipper fastener),因为这个物品用于把两个拉链边的链牙咬合在一起
# zip使用示例
a_zip = zip(range(3), 'ABC')
print(repr(a_zip))
print(list(a_zip))
b_zip = zip(range(3), 'ABC', [0.0, 1.1, 2.2, 3.3])
print(list(b_zip))
# itertools.zip_longest函数的行为有所不同,使用可选的fillvalue(默认值是None)填充缺失的值
c_zip = itertools.zip_longest(range(3), 'ABC', [0.0, 1.1, 2.2, 3.3], fillvalue=-1)
print(list(c_zip))


# --------------------------------------------------
# 10.7 Vector类第5版:格式化
print('*' * 50)
# Vector类的__format__方法与Vector2d的类相似,但不使用极坐标,而是使用球面坐标(也叫超球面坐标)
# Vector类支持n个维度,超过四维,球体变成了'超球体',因此把自定义的格式后缀由'p'改为'h'


# Vector类第5版,__format__的实现
class Vector:
    typecode = 'd'
    shortcut_names = 'xyzt'

    def __init__(self, components):
        # self._components是受保护的实例属性,把Vector分量保存在一个数组中
        self._components = array.array(self.typecode, components)

    def __iter__(self):
        # 为了迭代,我们使用self._components构造一个迭代器
        return iter(self._components)

    def __repr__(self):
        # 使用reprlib.repr函数获取self._components的有限长度表示形式
        components = reprlib.repr(self._components)
        # 把字符串插入Vector的构造方法之前,去掉前面的"array('d', "和后面的")"
        components = components[components.find('['):-1]
        return f'Vector({components})'

    def __str__(self):
        return str(tuple(self))

    def __bytes__(self):
        return (bytes([ord(self.typecode)])) + bytes(self._components)

    def __eq__(self, other):
        # 以下方式是合适的
        if len(self) != len(other):
            return False
        for a, b in zip(self, other):
            if a != b:
                return False
        return True
        # 上式可以下称如下形式:
        # return len(self) == len(other) and all(a ==b for a, b in zip(self, other))
        # return tuple(self) == tuple(other)
        # 会认为Vector([1, 2])和(1, 2)相等,而且效率很低

    def __hash__(self):
        # hashes = (hash(x) for x in self._components)
        # hashes的另一种方式
        hashes = map(hash, self._components)
        return functools.reduce(operator.xor, hashes, 0)

    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self._components))

    def __bool__(self):
        return bool(abs(self))

    def __len__(self):
        return len(self._components)

    def __getitem__(self, index):
        cls = type(self)  # 获取实例属性的类,供后面使用
        if isinstance(index, slice):
            return cls(self._components[index])  # 构建一个新Vector实例
        elif isinstance(index, numbers.Integral):
            return self._components[index]  # 返回_components中相应的元素
        else:
            raise TypeError(f'{cls.__name__} indices must be integers')

    def __getattr__(self, name):
        cls = type(self)
        if len(name) == 1:
            pos = cls.shortcut_names.find(name)
            if 0 <= pos <= len(self._components):
                return self._components[pos]
            raise AttributeError(f'{cls.__name__} object has no attribute {name}')

    def __setattr__(self, name, value):
        cls = type(self)
        if len(name) == 1:
            if name in cls.shortcut_names:
                error = f'readonly attribute {name}'
            elif name.islower():
                error = f"can't set attribute 'a' to 'z' in {cls.__name__}"
            else:
                error = f''
            if error:
                raise AttributeError(error)
        super().__setattr__(name, value)

    def angle(self, n):
        r = math.sqrt(sum(x**2 for x in self[n:]))
        a = math.atan2(r, self[n-1])
        if (n == len(self) - 1) and (self[-1] < 0):
            return math.pi * 2 - a
        else:
            return a

    def angles(self):
        return (self.angle(n) for n in range(1, len(self)))

    def __format__(self, fmt_spec=''):
        if fmt_spec.endswith('h'):
            fmt_spec = fmt_spec[:-1]
            # 使用itertools.chain函数生成生成器表达式,无缝迭代向量的模和各个角坐标
            coords = itertools.chain([abs(self)], self.angles())
            outer_fmt = '<{}>'
        else:
            coords = self
            outer_fmt = '({})'
        components = (format(c, fmt_spec) for c in coords)
        return outer_fmt.format(','.join(components))

    @classmethod
    def frombytes(cls, octets):
        typecode = chr(octets[0])
        memv = memoryview(octets[1:]).cast(typecode)
        return cls(memv)  # 直接把memoryview传给构造方法,不用像前面那样使用*拆包


# 最终结果测试
print(repr(Vector([3.1, 4.2])))
print(repr(Vector((3.1, 4.2))))
print(repr(Vector(range(10))))

print('\n---Tests with two dimensions---')
v1 = Vector([3, 4])
x, y = v1
print(x, y)
print(repr(v1))
v1_clone = eval(repr(v1))
print(v1 == v1_clone)
print(v1)
octets = bytes(v1)
print(octets)
print(abs(v1))
print(bool(v1), bool(Vector((0, 0))))

print('\n---Tests of .frombytes() method---')
v1_clone = Vector.frombytes(bytes(v1))
print(repr(v1_clone))
print(v1 == v1_clone)

print('\n---Tests with three dimensions---')
v1 = Vector([3, 4, 5])
x, y, z = v1
print(x, y, z)
print(repr(v1))
v1_clone = eval(repr(v1))
print(v1 == v1_clone)
print(v1)
print(abs(v1))
print(bool(v1), bool(Vector((0, 0, 0))))

print('\n---Tests with many dimensions--')
v7 = Vector(range(7))
print(repr(v7))
print(abs(v7))


print('\n---Tests of .bytes and .format() methods--')
v1 = Vector([3, 4, 5])
v1_clone = Vector.frombytes(bytes(v1))
print(repr(v1_clone))
print(v1 == v1_clone)

print('\n---Tests of sequence behavior--')
v1 = Vector([3, 4, 5])
print(len(v1))
print(v1[0], v1[len(v1) - 1], v1[-1])

print('\n---Tests of slicing--')
v7 = Vector(range(7))
print(v7[-1])
print(v7[1:4])
print(v7[-1:])
# print(v7[1, 2])  # TypeError: Vector indices must be integers

print('\n---Tests dynamic attribute access--')
v10 = Vector(range(10))
print(v10.x)
print(v10.y, v10.z, v10.t)

print('\n---Dynamic attribute lookup failures--')
"""
print(v10.k)  # AttributeError: Vector object has no attribute k
print(Vector(range(3)).t)  # IndexError: array index out of range
print(Vector(range(3)).spam)  # None
"""

print('\n---Tests of hashing--')
v1 = Vector([3, 4])
v2 = Vector({3.1, 4.2})
v3 = Vector([3, 4, 5])
v6 = Vector(range(6))
print(hash(v1), hash(v2), hash(v3), hash(v6))
# Most hash values of non-integers vary from a 32-bit to 64-bit CPython build
print(hash(v2) == (384307168202284039
                   if sys.maxsize > 2**32 else 357915986))

print('\n---Tests of .format with Cartesian coordinates in 2D--')
v1 = Vector([3, 4])
print(format(v1))
print(format(v1, '.2f'))
print(format(v1, '.3e'))

print('\n---Tests of .format with Cartesian coordinates in 3D and 7D--')
v3 = Vector(range(3))
v7 = Vector(range(7))
print(format(v3))
print(format(v7))

print('\n---Tests of .format with spherical coordinates in 2D, 3D, 4Dand 7D--')
v2 = Vector([1, 1])
v3 = Vector([1, 1, 1])
v4 = Vector([3, 4, 5, 6])
v7 = Vector(range(7))
print(v2)
print(format(v2, 'h'))
print(format(v2, '.3eh'))
print(format(v2, '0.5fh'))
print(format(v3, '0.5fh'))
print(format(v4, '0.5fh'))
print(format(Vector([-1, -1, -1, -1]), '0.5fh'))
print(format(Vector([2, 2, 2, 2]), '0.5fh'))
print(format(Vector([0, 2, 0, 0]), '0.5fh'))


# --------------------------------------------------
# 10.8 本章小结
print('*' * 50)
# 本章所举的Vector示例故意与Vector2d兼容,不过二者的构造方法签名不同
# Vector类的构造方法接受一个可迭代的对象,这与内置的序列类型一样
# Vector类的行为之所以像序列,是因为它实现了__getitem__和__len__方法

# 说明了my_seq[a:b:c]句法背后的工作原理
# 创建slice(a, b, c)对象,交给__getitem__方法处理

# 为 Vector 实例的头几个分量提供了只读访问功能

# 实现__hash__方法特别适合使用functools.reduce函数

# Vector类的最后一项改进是在Vector2d的基础上重新实现__format__方法
