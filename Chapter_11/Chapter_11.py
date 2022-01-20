__author__ = 'fmy'

import abc
import collections
import random

"接口:从协议到抽象基类"

# --------------------------------------------------
# 11.1 Python文化中的接口和协议
print('*' * 50)
# 类的接口:类实现或继承的公共属性(方法或数据属性),包括特殊方法(如__getitem__,__add__)
# 按照定义,受保护的属性和私有属性不在接口中
# 公开数据属性放入对象接口没有不妥,因为总能实现读值方法和设值方法,把数据属性变成特性

# 接口的补充定义:对象公开方法的子集,让对象在系统中扮演特定的角色

# 协议是接口,但不是正式的(只由文档和约定定义),因此协议不能想正式接口那样施加限制
# 对Python来讲,'X类对象','X协议'和'X接口'是一个意思
# 序列协议是Python最基础的协议


# --------------------------------------------------
# 11.2 Python喜欢序列
print('*' * 50)


# 定义__getitem__方法,只是先序列协议的一部分足以访问元素、迭代和in运算符
class Foo:
    def __getitem__(self, pos):
        return range(0, 30, 10)[pos]


f = Foo()
print(f[1])
for i in f:
    print(i, end='\t')
print(f'\n{20 in f}')
# 虽然没有__iter__方法,但是Foo实例是可迭代对象,因为发现有__getitem__时,Python会调用它
# 传入从0开始的整数索引,尝试迭代对象(这时一种后备机制)
# 同时尽管没有__contains__方法,但Python足够智能,能迭代Foo,也能使用in运算符:Python会全面检查有无指定元素

# 综上,鉴于序列协议的重要性,如果没有__iter__和__contains__方法,Python会调用__getitem__方法

# 第1章那些示例之所以能用,大部分是由于Python会特殊对待看起来像是序列的对象
# Python中的迭代是鸭子类型的一种极端形式:为了迭代对象,解释器会尝试调用两个不同的方法
Card = collections.namedtuple('Card', ['rank', 'suit'])


# 实现序列协议的FrenchDeck类
class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]


# --------------------------------------------------
# 11.3 使用猴子补丁在运行时实现协议
print('*' * 50)
# 上述FrenchDeck类有个重大缺陷:无法洗牌.因此有了shuffle方法
# 实际上如果FrenchDeck实例的行为像序列,不需要shuffle方法,因为已经有了random.shuffle函数可用

# 标准库random.shuffle函数用法
l = list(range(20))
print(l)
random.shuffle(l)
print(l)

# 直接使用打乱FrenchDeck实例,会报错
deck = FrenchDeck()
print(list(deck))


# TypeError: 'FrenchDeck' object does not support item assignment
# random.shuffle(deck)
# 问题的原因是,shuffle函数要调用集合中元素的位置,而FrenchDeck只实现了不可变的序列协议
# 可变的序列还需提供__setitem__方法


# Python是动态语言,因此我们可以在运行时修改这个问题
# 为FrenchDeck打猴子补丁,把它变成可变的,让random.shuffle函数能处理
def set_card(self, position, card):
    self._cards[position] = card


FrenchDeck.__setitem__ = set_card
random.shuffle(deck)  # 现在可以打乱deckl
print(list(deck))

# 这里的关键是,set_card函数要知道deck有一个名为_cards的属性,而且_cards的值必须是可变序列
# 然后我们把set_card函数赋值给特殊方法__setitem__,从而把它依附到FrenchDeck类上
# 猴子补丁:在运行时修改类或模块,而不该动源码
# 猴子补丁强大但是打补丁的代码与要打补丁的程序耦合十分紧密,往往要处理隐藏和没有文档的部分

# 除了猴子补丁,上述例子还说明协议是动态的:random.shuffle函数不关心参数的类型,只要对象实现部分可变序列协议即可

# 本章讨论的主题是'鸭子类型',对象的类型无关紧要,只要实现了特定的协议即可


# --------------------------------------------------
# 11.4 Alex Martelli 的水禽
print('*' * 50)
field_names = 'one, two, three, four'
try:
    field_names = field_names.replace(',', ' ').split()
except AttributeError:
    pass
field_names = tuple(field_names)
print(field_names)
# 抽象基类:抽象基类是用于封装框架引入的一般性概念和抽象的,例如'一个序列'和'一个确切的数'

# 鸭子类型与继承无关,鸭子类型的定义:
# 当看到一只鸟走起来像鸭子、游泳起来像鸭子、叫起来也像鸭子.那么这只鸟就可以被称为鸭子
# 对象类型不重要,只要实现特定协议即可.忽略对象类型,关注对象是否实现所需的方法、签名和语义
# 一个用户定义的类型，不需要真正的继承自抽象基类，但是却可以当作其子类一样来使用

# 白鹅类型的定义：
# 使用抽象基类明确声明接口,子类显示地继承抽象基类,抽象基类会检查子类是否符合接口定义
# 劣势:子类为了经过抽象基类的接口检查,必须实现一些接口,但是这些接口你可能用不到
# 优势:一些直接继承自抽象基类的接口是可以拿来即用的


# --------------------------------------------------
# 11.5 定义抽象基类的子类
print('*' * 50)

# FrenchDec2,collections.MutableSequence的子类
Card = collections.namedtuple('Card', ['rank', 'suit'])


class FrenchDeck2(collections.abc.MutableSequence):
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit)
                       for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, pos):
        return self._cards[pos]

    def __setitem__(self, pos, value):
        self._cards[pos] = value

    def __delitem__(self, pos):
        del self._cards[pos]

    def insert(self, pos, value):
        self._cards.insert(pos, value)


cards = FrenchDeck2()
for card in cards:
    print(repr(card))

# 在collections.abc中,每个抽象基类的具体方法都是作为类的公共接口实现的,因此不用知道实例的内部接口
# 要实现子类,我们可以覆盖从抽象基类中继承的方法,以更高效的方式重新实现
# 如__contains__方法全面扫描序列,可是若定义的序列按照循序保存,则可以从新定义__cotains__方法


# --------------------------------------------------
# 11.6 标准库中的抽象基类
print('*' * 50)
# 大多数抽象基类在collections.abc模块中定义,不过其他地方也有
# 如numbers和io包中有一些抽象基类

# 1).collections.abc模块中的抽象基类
"""
# 标准库中有两个abc模块,这里说的是collections.abc;另一个是abc模块就是abc,定义的是abc.ABC
# collections.abc模块中定义了16个抽象基类
# · Iterable,Container和Sized:
# ----各个集合应该继承着三个抽象基类,或者至少实现兼容的协议
# ----Iterable通过__iter__方法支持迭代
# ----Container通__container__方法支持in运算符
# ----Sized通过__len__方法支持len()函数
# · Sequence,Mapping和Set
# ----这三个是主要的不可变集合类型,而且各自都有可变的子集
# · MappingView
# ----映射方法.items(),.keys()和.values()返回的对象分别是ItemsVie,KeysView和ValueView的实例
# ----前两个类还继承了丰富的接口
# · Callable和Hashable
# ----这两个抽象基类与集合没有太大的关系,只不过因为collections.abc是标准库中定义抽象基类的第一个基类
# ----而它们又太重要,因此把它们放到collections.abc模块中
# ----这两个抽象基类的主要作用是为内置函数isinstance提供支持,以一种安全的方式判断对象能不能调用或散列
# · Iterator
# ----是Iterable的子类
"""

# 2).抽象基类的数字塔
"""
# numbers包定义的是'数字塔'(即各个抽象基类的层次结构是线性的)
# 其中Number是位于最顶端的超类,随后是Complex子类,依次向下,最低端是Integral类:
# Number -> Complex -> Real -> Rational -> Integral
# 因此,检查一个数是不是整数,可以用isinstance(x, numbers.Integral),这样就能接受int,bool(int的子类)
# 或者外部库使用numbers抽象基类注册的其他类型
"""

# --------------------------------------------------
# 11.7 定义并使用一个抽象基类
print('*' * 50)


# 为了证明有必要定义抽象基类,想象一下这个场景：
# 你要在网站或移动应用中显示随机广告,但是在整个广告清单轮转一遍之前不重复显示广告
# 假设在构建一个广告管理框架名为ADAM,它的职责之一是支持用户提供随机挑选的无重复类

# 我们把这个抽象基类命名为Tombola
# Tombola抽象基类有四个方法,其中两个是抽象方法
# --- .load():把元素放入容器
# --- .pick():从容器中随机拿出一个元素,返回选中的元素
# 另外两个是具体方法
# --- .loaded(): 如果容器中至少有一个元素,返回True
# --- . inspect():返回一个有序数组,由容器中的现有元素构成,不会修改容器的内容


# Tombola抽象基类,有两个抽象方法和两个具体方法
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


# 其实抽象方法可以实现代码,即便实现了子类也必须覆盖抽象方法
# 但是在子类中可以使用super()函数调用抽象方法,为它添加功能,而不是从头开始实现
# .inspect方法笨拙,不过目的在于强调抽象基类可以提供具体方法,只要依赖接口中的其他方法就行
# Tombola的具体子类知晓内部数据结构,可以覆盖.inspect方法,使用更聪明的方式实现

# 异常类的部分层次结构
# BaseException
# |-SystemExit
# |-KeyboardInterrupt
# |-GeneratorExit
# |-Exception
#     |-StopIteration
#     |-ArithmeticError
#         |-FloatingPointError
#         |-OverflowError
#         |-ZeroDivisionError
#     |-AssertionError
#     |-AttributeError
#     |-BufferError
#     |-EOFError
#     |-ImportError
#     |-LookupError  # 在Tombola.inspect方法中处理的是LookupError异常
#         |-IndexError  # 是LookupError的子类,尝试从序列中获取索引超过最后位置的元素时抛出
#         |-KeyError  # 使用不存在的键从映射中获取数据时,抛出KeyError异常
#     |-MemoryError
# ...


# 不符合Tombola要求的子类无法蒙混过关
class Fake(Tombola):
    def pick(self):
        return 13


print(Fake)


# f = Fake()
# TypeError:Can't instantiate abstract class Fake with abstract method load
# Python认为Fake是抽象类,因为它没实现load方法,这是Tombola抽象类声明的抽象方法之一

# 1).抽象基类句法详解
# 声明抽象基类最简单的方法是继承abc.ABC或其他抽象基类
# Python 3.4 可以直接继承abc.ABC这个类
# Python 3 旧版本必须在class语句中使用metaclass=关键词,把值设为abc.ABCMeta,如:
# class Tombola(metaclass=abc.ABCmeta):
# Python 2 使用__metaclass__类属性
# @abstractmethod方法在与@classmethod和@staticmethod堆叠时放在最里面,即与def之间无其他值


# 2).定义Tombola抽象基类的子类
# BingoCage类是Tombola的具体子类
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


# BingoCage继承了Tombola耗时的loaded方法和笨拙的inspect方法,这两个方法都可以覆盖
# 变成如下一行代码,如下:
class LotteryBlower(Tombola):
    def __init__(self, iterable):
        self._balls = list(iterable)

    def load(self, iterable):
        self._balls.extend(iterable)

    def pick(self):
        try:
            position = random.randrange(len(self._balls))
        except ValueError:
            raise LookupError('Pick from empty BingoCage')
        return self._balls.pop(position)

    def loaded(self):
        return bool(self._balls)

    def inspect(self):
        return tuple(sorted(self._balls))

# 3).Tombola的虚拟子类
# 注册虚拟子类的方式是在抽象基类上调用register方法,注册的类会变成抽象基类的虚拟子类
# 而且issubclass和isinstance等函数都能识别,但是注册的类不会从抽象基类中继承任何方法或属性
# 虚拟子类不会继承注册的抽象基类,而且不会检查它是否符合基类的接口,即便实例化时也不检查

# register方法通常作为普通的函数调用,不过也可以作为装饰器使用
@Tombola.register  # 注册为Tombola的虚拟子类
class TomboList(list):
    def pick(self):
        if self:
            position = random.randrange(len(self))
            return self.pop(position)
        else:
            raise LookupError('Pop from empty TomboList')

    lpad = list.extend

    def loaded(self):
        return bool(self)

    def inspect(self):
        return tuple(sorted(self))


print(issubclass(TomboList, Tombola))
t = TomboList(range(100))
print(isinstance(t, Tombola))
# 类的继承关系在一个特殊的类属性中指定:__mro__,按顺序列出类和其超类
print(TomboList.__mro__)
# 可以看出其中没有Tombola, 因此TomboList没有从Tombola中继承任何方法


# --------------------------------------------------
# 11.8 Tombola子类的测试方法
print('*' * 50)
# 编写的Tombola用到两个类属性,用他们内省类的继承关系
# __subclasses__():这个方法返回类的直接子类列表,不含虚拟子类
print(Tombola.__subclasses__())
# _abc_registry:只有抽象基类有这个数据属性,其值是一个WeakSet对象,即抽象类注册的虚拟子类的弱引用
# 新版本中已经没有这个属性


# --------------------------------------------------
# 11.9 Python使用register的方式
print('*' * 50)
# 虽然现在可以把register当作装饰器使用了
# 但更常见的做法还是把它当作函数使用,用于注册其他地方定义的类


# --------------------------------------------------
# 11.10 鹅的行为有可能想鸭子
print('*' * 50)


# 即便不注册,抽象基类也能把一个类识别为虚拟子类
class Struggle:
    def __len__(self):
        return 23


print(isinstance(Struggle(), collections.abc.Sized))
print(issubclass(Struggle, collections.abc.Sized))
# 这是因为abc.Sized实现了一个特殊的方法,名为__subclasshook__


# Sized类的源码,Python 3.4
class Sized(metaclass=abc.ABCMeta):
    __slots__ = ()

    @abc.abstractmethod
    def __len__(self):
        return 0

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Sized:
            # 对于C.__mro__(即C及其超类)中所列的类来说,如果类的__dict__属性中有__len__的属性
            if any('__len__' is B.__dict__ for B in C.__mro__):
                return True
            return NotImplemented


# __subclasshook__在白鹅类型中添加了一些鸭子类型的踪迹
# 我们可以使用抽象基类定义正式接口,可以始终使用isinstance检查
# 也可以完全使用不相关的类,只要实现特定的方法即可


# --------------------------------------------------
# 11.11 本章小结
print('*' * 50)
# · 介绍了非正式接口(协议)高度动态本性,后讲解了抽象基类的静态接口声明
#   最后指出了抽象基类的动态特性:虚拟子类

# · 尽管抽象基类使得类型检查变得更容易了,但不应该在程序中过度使用它
#   Python核心在于它是一门动态语言，它带来了极大的灵活性
#   如果处处都强制实行类型约束，那么会使代码变得更加复杂，而本不应该如此
#   我们应该拥抱Python的灵活性
