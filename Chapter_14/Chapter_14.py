__author__ = 'fmy'

import abc
import collections
import re
import reprlib

"可迭代的对象、迭代器和生成器"
# 迭代是数据的基石,扫描内存中放不下的数据集时,我们要找到一种惰性获取数据项的方式
# 即按需一次获取一个数据项,这就是迭代器模式

# 所有生成器都是迭代器,因为生成器安全实现了迭代器接口
# 迭代器用于从集合中取出元素;生成器用于'凭空'生成元素

# 在Python中,所有集合都可以迭代,Python中迭代器用于支持:
# · for循环
# · 构建和扩展集合类型
# · 逐行遍历文本文件
# · 元组拆包
# · 调用函数时,使用*拆包实参

# 本章涵盖以下话题:
# · 语言内部使用 iter(...) 内置函数处理可迭代对象的方式
# · 如何使用 Python 实现经典的迭代器模式
# · 详细说明生成器函数的工作原理
# · 如何使用生成器函数或生成器表达式代替经典的迭代器
# · 如何使用标准库中通用的生成器函数
# · 如何使用 yield from 语句合并生成器
# · 案例分析:在一个数据库转换工具中使用生成器函数处理大型数据集
# · 为什么生成器和协程看似相同,实则差别很大,不能混淆

# --------------------------------------------------
# 14.1 Sentence类第1版:单词序列
print('*' * 50)
# Sentence,将句子划分为单词序列
RE_WORD = re.compile('\w+')


class Sentence:
    def __init__(self, text):
        self.text = text
        # re.findall函数返回一个字符串列表,里面的元素是正则表达式的全部非重叠匹配
        self.words = RE_WORD.findall(text)

    def __getitem__(self, index):
        return self.words[index]

    def __len__(self):
        return len(self.words)

    def __repr__(self):
        # reprlib.repr函数用于生成大型数据结构的简略字符串表示形式
        return f'Sentence({reprlib.repr(self.text)})'


# 测试结果
s = Sentence("'The time has come,' the Walrus said,")
print(s)
for word in s:
    print(word)
print(list(s))
print(s[0])
print(s[5])
print(s[-1])

# 序列可以迭代的原因:iter函数
# 解释器需要迭代对象x时,会自动调用iter()
# 内置的iter函数有以下作用:
# · 检查对象是否实现了__iter__方法,如果实现了就调用它,获取一个迭代器
# · 如果没有实现__iter__方法,但是实现了__getitem__方法,Python会创建一个迭代器
#   尝试按顺序(从索引0开始)获取元素
# · 如果尝试失败,Python抛出TypeError异常,通常会提示'-- object is not iterable'
#   其中C是目标对象所属的类

# 任何Python序列都可迭代的原因是它们都实现了__getitem__方法,其实标准的序列都实现了__iter__方法
# 之所以对__getitem__方法做特殊处理是为了向后兼容


class Foo:
    def __iter__(self):
        pass


print(issubclass(Foo, collections.abc.Iterable))
f = Foo()
print(isinstance(f, collections.abc.Iterable))
# 前面定义的Sentence类是可以迭代的,但却无法通过issubclass测试
print(issubclass(Sentence, collections.abc.Iterable))


# --------------------------------------------------
# 14.2 可迭代的对象与迭代器的对比
print('*' * 50)
# 可迭代的对象:
# --使用iter内置函数可以获取迭代器的对象,若对象实现了能返回迭代器的__iter__方法
# --则对象是可迭代的.序列都可以迭代;实现了__getitem__方法而且参数是从0开始的索引,这种对象也可以迭代
s = 'ABC'
for char in s:
    print(char)
# 这里'ABC'是可迭代的对象

# 若没有for语句
s = 'ABC'
it = iter(s)  # 使用可迭代的对象构造迭代器
while True:
    try:
        print(next(it))  # 不断在迭代器上调用next函数,获取下一个字符
    except StopIteration:  # 若没有字符了,迭代器抛出StopIteration异常
        del it  # 释放对it的引用,即废弃迭代器对象
        break
# StopIteration异常表明迭代器到头了,Python语言内部会处理for循环和其他迭代上下文中的StopIteration异常


# 标准的迭代器接口有两个方法:
# __next__:返回下一个可用的元素,如果没有了抛出StopIteration
# __iter__:返回self,以便在应该使用可迭代对象的地方使用迭代器


class Iterator(collections.abc.Iterable):
    __slots__ = ()

    @abc.abstractmethod
    def __next__(self):
        raise StopIteration

    def __iter__(self):
        return self

    @classmethod
    def __subclasscheck__(cls, C):
        if cls is Iterator:
            if (any('__next__' in B.__dict__ for B in C.__mro__)) and \
                    (any('__iter__' in B.__dict__ for B in C.__mro__)):
                return True
        return NotImplemented


s3 = Sentence('Pig and Pepper')
it = iter(s3)
print(repr(it))
print(next(it))
print(next(it))
print(next(it))
# print(next(it))  # StopIteration
print(list(it))
print(list(iter(s3)))
# 迭代器只需__next__和__iter__两个方法,所以除了调用next()方法
# 以及捕获StopIteration异常之外,没有办法检查是否还有遗留的元素
# 此外也没有办法还原迭代器,若想再次迭代就要调用iter(...),传入之前构建迭代器的可迭代对象
# 传入迭代器本身没用,因为前面说过Iterator.__iter__方法的实现方式是返回实例本身
# 所以传入迭代器无法还原已经耗尽的迭代器

# 迭代器:
# --迭代器是这样的对象:实现了无参数的__next__方法,返回序列中的下一个元素,如果没有元素了
# --那么抛出StopIteration异常,Python中的迭代器实现了__iter__方法,因此迭代器也可以迭代


# --------------------------------------------------
# 14.3 Sentence类第2版:典型的迭代器
print('*' * 50)


# 使用迭代器模式实现Sentence类
RE_WORD = re.compile('\w+')


class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        # 根据可迭代协议,__iter__方法实例化并返回一个迭代器
        return SentenceIterator(self.words)


class SentenceIterator:
    def __init__(self, words):
        self.words = words
        self.index = 0

    def __next__(self):
        try:
            word = self.words[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return word

    def __iter__(self):
        return self


# 把Sentence变成迭代器:坏主意
# 可迭代的对象有个__iter__方法,每次都实例化一个新的迭代器
# 而迭代器要实现__next__方法,返回单个元素,此外还有实现__iter__方法,返回迭代器本身
# 迭代式模式可用来:
# · 访问一个聚合对象的内容而无需暴露它的内部表示
# · 支持对聚合对象的多种遍历
# · 为遍历不同的聚合结构提供一个统一的接口
s3 = Sentence('Pig and Pepper')
print(s3)
for word in s3:
    print(word)
print('-' * 10)
it = iter(s3)
print(it)
for word in it:
    print(word)


# --------------------------------------------------
# 14.4 Sentence类第3版:生成器函数
print('*' * 50)


# --------------------------------------------------
# 14.5 Sentence类第4版:惰性实现
print('*' * 50)


# --------------------------------------------------
# 14.6 Sentence类第5版:生成器表达式
print('*' * 50)

# --------------------------------------------------
# 14.7 何时使用生成器表达式
print('*' * 50)


# --------------------------------------------------
# 14.8 另一个示例:等差数列生成器
print('*' * 50)


# --------------------------------------------------
# 14.9 标准库中的生成器函数
print('*' * 50)


# --------------------------------------------------
# 14.10 Python3.3中新出现的句法:yield from
print('*' * 50)


# --------------------------------------------------
# 14.11 可迭代的归约函数
print('*' * 50)


# --------------------------------------------------
# 14.12 深入分析iter函数
print('*' * 50)


# --------------------------------------------------
# 14.13 案例分析:在数据库转换工具中使用生成器
print('*' * 50)


# --------------------------------------------------
# 14.14 把生成器当成协程
print('*' * 50)


# --------------------------------------------------
# 14.15 本章小结
print('*' * 50)