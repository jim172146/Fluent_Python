__author__ = 'fmy'

import abc
import array
import collections
import decimal
import fractions
import itertools
import math
import numbers
import random
import sys
import numpy

sys.path.append('../Chapter_10')
sys.path.append('../Chapter_09')

import Chapter_9
import Chapter_10

"正确重载运算符"
# 在Python中函数调用(),属性调用.和元素访问/切片[]也是运算符
# 本章我们讨论:
# · Python如何处理中缀运算符中不同类型的操作数
# · 使用鸭子类型或显式类型检查处理不同类型的操作数
# · 中缀运算符如何表明自己无法处理操作数
# · 众多比较运算符(如==,>,<=等)的特殊行为
# · 增量赋值运算符(如+=)的默认处理方式和重载方式


# --------------------------------------------------
# 13.1 运算符重载基础
print('*' * 50)
# Python对重载施加了一些限制,做到灵活性、可用性和安全性方面的平衡
# · 不能重载内置类型的运算符
# · 不能新建运算符,只能重载现有的
# · 某些运算符不能重载,如is,and,or,not(不过|,&,^和~可以)


# --------------------------------------------------
# 13.2 一元运算符
print('*' * 50)
# -(__neg__)
# +(__pos__)
# ~(__invert__),对整数按位取反

print(Chapter_10.Vector([5, 5]))


# 在继承Vector的基础上添加-和+运算符
class EgVector(Chapter_10.Vector):
    def __abs__(self):
        return math.sqrt(sum(x**2 for x in self))

    def __neg__(self):
        return Chapter_10.Vector(-x for x in self)

    def __pos__(self):
        return Chapter_10.Vector(self)


a = EgVector([3, 3, 3])
print(a)
print(-a)

# 算术运算上下文的精度变化可能导致x不等于+x
ctx = decimal.getcontext()  # 获取当前全局算术运算的上下文引用
ctx.prec = 40  # 把算数运算上下文的精度设为40
one_third = decimal.Decimal('1') / decimal.Decimal('3')
print(one_third)
print(one_third == +one_third)
ctx.prec = 28
print(one_third == +one_third)
print(one_third)
print(+one_third)

# 一元运算符 + 得到一个新Counter实例,但是没有零值和负值计数器
ct = collections.Counter('abracadabra')
print(ct)
ct['r'] = -3
ct['d'] = 0
print(ct)
print(+ct)


# --------------------------------------------------
# 13.3 重载向量加法运算符+
print('*' * 50)
# Vector类是序列类型,序列应该支持+运算符(用于拼接),以及*运算符(用于重复复制)
# 但我们使用向量数学运算符实现+和*
# 理想中结果如下:
#  Vector([3, 4, 5]) +  Vector([3, 4, 5]) = Vector([6, 8, 10])
#  Vector([3, 4, 5]) +  Vector([3, 4]) = Vector([6, 8, 5])


# EditVector第1版,__add__方法
class EditVector(Chapter_10.Vector):
    def __add__(self, other):
        # paris是个生成器,会生成(a, b)形式的元组,a来自self,b来自other,使用0填充较短的那个
        pairs = itertools.zip_longest(self, other, fillvalue=0)
        return Chapter_10.Vector(a + b for a, b in pairs)


# 实现一元运算符和中缀运算符的特殊方法一定不能修改操作参数
# 使用这些运算符的表达式期待结果是新对象,只有赋值表达式可能会修改第一个操作数

# EditVector结果展示
v1 = EditVector([3, 4, 5])
v2 = EditVector(numpy.ones(5))
print(v1 + v2)
print(v1 + [1 for _ in range(10)])
# TypeError: can only concatenate list (not "EditVector") to list
# print([1 for _ in range(10)] + v1)


# Python为支持设计不同类型的运算,为中缀运算符特殊方法提供了特殊的分派机制
# 以 a + b 为例,解释器执行以下几步:
# · 若a有__add__方法,返回值不是NotImplemented,调用a.__add__(b),然后返回结果
# · 若a有__add__方法,返回值是NotImplemented,检查b有没有__radd__方法
#   若有,而且没有返回NotImplemented,调用b.__radd__(a),然后返回结果
# · 若b没有__radd__方法,或者调用__radd__方法返回NotImplemented
#   抛出TypeError,并在错误消息中指明操作数据类型不支持

# __radd__是__add__的反向版本,为了使得([1, 2]+v1)能成功,我们实现__radd__方法

# 别把NotImplemented和NotImplementedError搞混了
# 前者是特殊的单例值,若中缀运算符特殊方法不能处理给定的操作数,则把它返回给解释器
# 而NotImplementedError是一种异常,抽象类中的占位方法把它抛出,提醒子类必须覆盖


# EditVector第1版,__add__方法,__radd__方法
class EditVector(Chapter_10.Vector):
    def __add__(self, other):
        pairs = itertools.zip_longest(self, other, fillvalue=0)
        return Chapter_10.Vector(a + b for a, b in pairs)

    def __radd__(self, other):
        return self + other


print('-' * 10)
v1 = EditVector([3, 4, 5])
print([1 for _ in range(10)] + v1)
# TypeError: 'int' object is not iterable
# print(v1 + 1)
# TypeError: unsupported operand type(s) for +: 'float' and 'str'
# print(v1 + 'ABC')
# 如果由于类型不兼容而导致运算符特殊方法无法返回有效的结果
# 那么应该返回NotImplemented,而不是抛出TypeError
# 返回NotImplemented时,另一个操作数所属的类型还有机会执行运算,会尝试调用反向方法


# EditVector第1版,__add__方法,__radd__方法
class EditVector(Chapter_10.Vector):
    def __add__(self, other):
        try:
            pairs = itertools.zip_longest(self, other, fillvalue=0)
            return Chapter_10.Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        return self + other

# 如果中缀运算符方法抛出异常,就终止了运算符分派机制
# 对 TypeError 来说,通常最好将其捕获,然后返回 NotImplemented


# --------------------------------------------------
# 13.4 重载标量乘法运算符*
print('*' * 50)


# EditVector,实现__mul__和__rmul__方法
class EditVector(EditVector):
    def __mul__(self, scalar):
        return EditVector(n * scalar for n in self)

    def __rmul__(self, scalar):
        return self * scalar


v1 = EditVector([3, 4, 5])
print(id(v1))
print(v1 * 10)
v1 *= 10
print(id(v1))
print(v1)
# 但是提供不兼容的操作数时会出问题


# EditVector,实现*运算符
class EditVector(EditVector):
    typecode = 'd'

    def __init__(self, components):
        self._components = array.array(self.typecode, components)

    def __mul__(self, scalar):
        if isinstance(scalar, numbers.Real):
            return EditVector(n * scalar for n in self)
        else:
            # 返回NotImplemented,尝试在scalar操作数上调用__rmul__方法
            return NotImplemented

    def __rmul__(self, scalar):
        return self * scalar


v1 = EditVector([1, 2, 3])
print(14 * v1)
print(v1 * True)
print(repr(v1 * fractions.Fraction(1, 3)))

# 一些中缀运算符号方法的名称
# +:__add__       -:__sub__       *:__mul__
# /:__truediv__  //:__floordiv__  %:__mod__
# divmod():__divmod__      **,pow():__pow__
# @:__matmul__    &:__and__       |:__or__
# ^:__xor__      <<:__lshift__   >>:__rshift__


# --------------------------------------------------
# 13.5 众多比较运算符
print('*' * 50)


class EditVector(EditVector):
    def __eq__(self, other):
        return (len(self) == len(other) and
                all(a == b for a, b in zip(self, other)))


va = EditVector([1, 2, 3])
vb = EditVector(range(1, 4))
print(va == vb)
vc = EditVector([1, 2])
v2dc = Chapter_9.Vector2d(1, 2)
print(vc == v2dc)
v3 = (1, 2, 3)
print(va == v3)
# 对操作数过度宽容可能导致令人惊讶的结果


# 改进EditVector类的__eq__方法
class EditVector(EditVector):
    def __eq__(self, other):
        if isinstance(other, EditVector):
            return (len(self) == len(other) and
                    all(a == b for a, b in zip(self, other)))
        else:
            return NotImplemented


print('-' * 10)
va = EditVector([1, 2, 3])
vb = EditVector(range(1, 4))
print(va == vb)
vc = EditVector([1, 2])
v2dc = Chapter_9.Vector2d(1, 2)
print(vc == v2dc)
v3 = (1, 2, 3)
print(va == v3)

# EditVector实例与Vector2d实例比较时
# 1).为了计算vc ==v2dc,调用EditVector.__eq__(vc, v2dc)
# 2).经EditVector.__eq__确定v2dc不是EditVector实例,因此返回NotImplemented
#    得到NotImplemented,尝试调用Vector2d.__eq__(v2dc, vc)
# 3).Vector2d.__eq__(v2dc, vc)把两个操作数都变成元组,然后比较

# EditVector实例与元组实例比较时
# 1).为了计算va ==v3,调用EditVector.__eq__(va, v3)
# 2).经EditVector.__eq__确定v3不是EditVector实例,因此返回NotImplemented
#    得到NotImplemented,尝试调用tuple.__eq__(v3, va)
# 3).tuple.__eq__(v3, va)不知道EditVector是什么,因此返回NotImplemented
# 4).对==来说,若反向调用返回NotImplemented,Python会比较对象的ID,作最后一搏

# !=运算符我们不用实现它,从object继承的__ne__方法的后备行为满足了需求
# 定义了__eq__方法,而且它不返回NotImplemented,__ne__会对__eq__返回的结果取反
print(va != vb)


# --------------------------------------------------
# 13.6 增量赋值运算符
print('*' * 50)
# 如果一个类没有实现就地运算符,增量赋值运算符只是语法糖:a+=b作用与a=a+b完全一样
# 不可变类型,不可实现就地特殊方法


# AddableBingoCage扩展BingoCage,支持 + 和 +=
class Tombola(abc.ABC):  # 自己定义的抽象基类要继承abc.ABC
    @abc.abstractmethod
    def load(self, iterable):  # 抽象方法使用@abc.abstractmethod装饰器标记,且在定义体中只有文档字符串
        """从可迭代对象添加元素"""

    @abc.abstractmethod
    def pick(self):  # 根据文档字符串,如果没有元素可选,应该抛出LookupError
        """随机删除元素,然后将其返回,如果实例为空,抛出LookupError"""

    def loaded(self):  # 抽象基类可以包含具体方法
        """如果至少有一个元素,返回True,否则返回False"""
        return bool(self.inspect())  # 抽象基类中的具体方法只能依赖抽象基类的接口

    def inspect(self):
        """返回一个有序元组,由当前元素构成"""
        items = []
        while True:  # 我们不知道具体子类如何储存元素,不过为了得到inspect的结果,我们不断调用.pick()方法
            try:
                items.append(self.pick())
            except LookupError:
                break
        self.load(items)  # 然后使用.load()把所有元素放回去
        return tuple(sorted(items))


class BingoCage(Tombola):
    def __init__(self, items):
        # random.SystemRandom使用os.urandom()函数实现random API
        # os.urandom()函数生成'适合用于加密'的随机字节序列
        self._randomizer = random.SystemRandom()
        self._items = []
        self.load(items)  # 委托load方法实现初始加载

    def load(self, items):
        self._items.extend(items)
        # 没有使用random.shuffle函数,而是使用SystemRandom实例的shuffle方法
        self._randomizer.shuffle(self._items)

    def pick(self):
        try:
            return self._items.pop()
        except IndexError:
            raise LookupError('Pick from empty BingoCage')

    def __call__(self):
        self.pick()


class AddableBingoCage(BingoCage):
    def __add__(self, other):
        if isinstance(other, Tombola):
            return AddableBingoCage(self.inspect() + other.inspect())
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, Tombola):
            other_iterable = other.inspect()
        else:
            try:
                other_iterable = iter(other)
            except TypeError:
                self_cls = type(self).__name__
                msg = 'Right opened in += must be {!r} or an iterable'
                raise TypeError(msg.format(self_cls))
        self.load(other_iterable)
        return self


vowel = 'AEIOU'
globe = AddableBingoCage(vowel)
print(globe.inspect())
print(globe.pick())
print(len(globe.inspect()))
globe2 = AddableBingoCage('XYZ')
globe3 = globe + globe2
print(globe3.inspect())
print(len(globe3.inspect()))
# TypeError:unsupported operand type(s) for +:'AddableBingoCage' and 'list'
# void = globe + [10, 20]
print('-' * 10)
globe_orig = globe
print(len(globe.inspect()))
globe += globe2
print(len(globe.inspect()))
globe += ['M', 'N']
print(len(globe.inspect()))
print(globe is globe_orig)
# globe += 1  # TypeError:Right opened in += must be 'AddableBingoCage' or an iterable

# 与+相比,+=运算符对第二个操作数更宽容,+运算符的两个操作数必须是相同类型(这里是AddableBingoCage)
# 否则结果的类型可能让人摸不着头脑.而+=的情况更明确,因为就地修改左操作数,所以结果的类型是确定的
