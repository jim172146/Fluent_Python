__author__ = 'fmy'

import abc
import collections
import decimal
import fractions
import itertools
import operator
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
RE_WORD = re.compile('\w+')


class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = RE_WORD.findall(text)

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        for word in self.words:  # 迭代self.words
            yield word  # 产生当前的word
        return  # 这个return语句不是必要的,这个函数可以直接'落空',自动返回

    def __getitem__(self, index):
        return self.words[index]


s = Sentence('Pig and Pepper')
print(s)
for word in s:
    print(word)
print(s[1])

# 生成器函数的工作原理
# 只要Python函数的定义体中有yield关键字,该函数就是生成器函数
# 调用生成器函数时会返回一个生成器对象


# 一个简单的函数说明生成器的行为:
def gen_123():
    yield 1
    yield 2
    yield 3


print('-' * 10)
print(repr(gen_123()))
for i in gen_123():
    print(i)
g = gen_123()
print(next(g))
print(next(g))
print(next(g))
# print(next(g))  # StopIteration

# 生成器函数会创建一个生成器对象,包装生成器函数的定义体
# 把生成器传给next()函数时生成器函数会向前执行函数定义体中的下一个yield函数,返回产生的值并暂停在当前位置
# 最终函数的定义体返回时外层的生成器对象会抛出StopIteration异常


# 运行时打印消息的生成器函数
def gen_AB():
    print('start')
    yield 'A'
    print('continue')
    yield 'B'
    print('end')


for c in gen_AB():
    print(f'-->{c}')
# 到达生成器函数定义体的末尾时,生成器对象抛出StopIteration异常
# for机制会捕获异常,因此循环终止时没有报错


# --------------------------------------------------
# 14.5 Sentence类第4版:惰性实现
print('*' * 50)
# re.finditer函数是re.findall函数的惰性版本,返回的不是列表而是一个生成器
# 按需生成re.MatchObject实例
RE_WORD = re.compile('\w+')


class Sentence:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        # finditer函数构建一个迭代器,包含 self.text中匹配RE_WORD的单词
        for match in RE_WORD.finditer(self.text):
            #  match.group()方法从MatchObject实例中提取匹配正则表达式的具体文本
            yield match.group()


s = Sentence('Pig and Pepper')
print(s)
for word in s:
    print(word)


# --------------------------------------------------
# 14.6 Sentence类第5版:生成器表达式
print('*' * 50)
# 生成器表达式可以理解为列表推导的惰性版本:不会迫切地构建列表,而是返回一个生成器,按需惰性生成元素
# 如果列表推导是制造列表的工厂,那么生成器表达式就是制造生成器的工厂


# 现在列表推导中使用gen_AB生成器函数,然后在生成器表达式中使用
def gen_AB():
    print('start')
    yield 'A'
    print('continue')
    yield 'B'
    print('end')


res1 = [x*3 for x in gen_AB()]  # 列表推导迫切地迭代gen_AB()函数生成的生成器对象产出的元素
print(repr(res1))
for i in res1:  # 这个for循环迭代列表推导生成的res1列表
    print(f'-->{i}')
print('-' * 10)
res2 = (x*3 for x in gen_AB())  # 把生成器表达式返回的值赋值给res2
print(repr(res2))  # res2是一个生成器对象
for i in res2:  # 只有for循环迭代res2时,gen_AB函数的定义体才会真正执行
    print(f'-->{i}')


# 使用生成器表达式实现Sentence类
RE_WORD = re.compile('\w+')


class Sentence:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return f'Sentence({reprlib.repr(self.text)})'

    def __iter__(self):
        return (match.group() for match in RE_WORD.finditer(self.text))
        # for match in RE_WORD.finditer(self.text):
        #     yield match.group()


# --------------------------------------------------
# 14.7 何时使用生成器表达式
print('*' * 50)
# 遇到简单的情况时,可以使用生成器表达式
# 如果生成器表达式要分成多行写,定义生成器函数更合适


# --------------------------------------------------
# 14.8 另一个示例:等差数列生成器
print('*' * 50)
# 典型的迭代器模式作用很简单--遍历数据结构


class ArithmeticProgression:
    def __init__(self, begin, step, end=None):
        self.begin = begin
        self.step = step
        self.end = end  # None -> 无穷数列

    def __iter__(self):
        # 这一行把self.begin赋值给result,不过会先强制转换成前面的加法算式得到的类型
        result = type(self.begin + self.step)(self.begin)
        forever = self.end is None
        index = 0
        while forever or result < self.end:
            yield result
            index += 1
            result = self.begin + self.step * index


ap = ArithmeticProgression(0, 1, 3)
print(list(ap))
ap = ArithmeticProgression(0, .5, 3)
print(list(ap))
ap = ArithmeticProgression(0, 1/3, 1)
print(list(ap))
ap = ArithmeticProgression(0, fractions.Fraction(1, 3), 1)
print(list(ap))
ap = ArithmeticProgression(0, decimal.Decimal(.1), .3)
print(list(ap))


#  ap_gen的生成器函数,作用与ArithmeticProgression类一样
def ap_gen(begin, step, end=None):
    result = type(begin + step)(begin)
    forever = end is None
    index = 0
    while forever or result < end:
        yield result
        index += 1
        result = begin + step * index


# 使用itertools模块生成等差数列
gen = itertools.count(1, 0.5)
print(next(gen))
print(next(gen))
print(next(gen))
# itertools.count函数不停止,因此若调用list(count())
# Python会创建一个特别大的列表,超出可用内存,在调用失败之前电脑会疯狂地运转

gen = itertools.takewhile(lambda n: n < 3, itertools.count(1, 0.5))
print(list(gen))
# itertools.takewhile函数则不同,它会生成一个使用另一个生成器的生成器
# 在指定的条件计算结果为False时停止


# 使用takewhile和count创建ap_gen函数
def ap_gen(begin, step, end=None):
    first = type(begin + step)(begin)
    number_gen = itertools.count(first, step)
    if end is not None:
        number_gen = itertools.takewhile(lambda n: n < end, number_gen)
    return number_gen
# ap_gen不是生成器函数,因为定义体中没有yield关键字
# 但是它会返回一个生成器,因此它与其他生成器函数一样,也是生成器工厂函数


# --------------------------------------------------
# 14.9 标准库中的生成器函数
print('*' * 50)
# 不过本节专注于通用的函数:
# 参数为任意的可迭代对象,返回值是生成器,用于生成选中的、计算出的和重新排列的元素

# 1).用于过滤的生成器函数:
# 从输入的可迭代对象中产出元素的子集,且不修改元素本身
# itertools.compress(it, select_it)
# itertools.dropwhile(predicate, it)
# filter(predicate, it)
# itertools.filterfalse(predicate, it)
# itertools.islice(it, stop)  itertools.islice(it, start, stop, step=1)
# itertools.takewhile(predicate, it)


# 演示用于过滤的生成器函数
def vowel(c):
    return c.lower() in 'aeiou'


print(list(filter(vowel, 'Aardvark')))
print(list(itertools.filterfalse(vowel, 'Aardvark')))
print(list(itertools.dropwhile(vowel, 'Aardvark')))  # 预测False及后所以值
print(list(itertools.takewhile(vowel, 'Aardvark')))  # 预测False前所以判断True的值
print(list(itertools.compress('Aardvark', (1, 0, 1, 0))))
print(list(itertools.islice('Aardvark', 4)))
print(list(itertools.islice('Aardvark', 4, 7)))
print(list(itertools.islice('Aardvark', 0, 8, 2)))

# 2).用于映射的生成器函数:
# 在输入的单个可迭代对象(map和starmap可处理多个可迭代对象)中的各个元素上做计算,然后返回结果
# itertools.accumulate(it, [func])
# enumerate(iterable, start=0)
# map(func, it1, [it2, ..., itn])
# itertools.starmap(func, it)

# itertools.accumulate函数的几个用法
print('-' * 10)
sample = [5, 4, 2, 8, 7, 6, 3, 0, 9, 1]
print(list(itertools.accumulate(sample)))
print(list(itertools.accumulate(sample, min)))
print(list(itertools.accumulate(sample, min)))
print(list(itertools.accumulate(sample, operator.mul)))
print(list(itertools.accumulate(range(1, 11), operator.mul)))

# 其他用于映射的生成器函数
print('-' * 10)
print(list(enumerate('albatroz', 10)))
print(list(map(operator.mul, range(11), range(11))))
# 计算两个可迭代对象对应位置元素之积,元素最少的可迭代对象到头后就停止
print(list(map(operator.mul, range(11), [2, 4, 8])))
print(list(map(lambda a, b: (a, b), range(11), [2, 4, 8])))
# 作用等同于内置的zip函数
print(list(zip(range(11), [2, 4, 8])))
print(list(itertools.starmap(operator.mul, enumerate('albatroz', 1))))
sample = [5, 4, 2, 8, 7, 6, 3, 0, 9, 1]
print(list(itertools.starmap(lambda a, b: b/a, enumerate(itertools.accumulate(sample), 1))))

# 3).用于合并的生成器函数:
# 这些函数都从输入的多个可迭代对象中产出元素
# chain和chain.from_iterable按顺序(一个接一个)处理输入的可迭代对象
# 而product、zip和zip_longest并行处理输入的各个可迭代对象
# itertools.chain(it1, ..., itn)
# itertools.chain.from_iterable(it)
# itertools.product(it1, ..., itn, repeat=1)
# zip(it1, ..., itn)
# itertools.zip_longest(it1, ..., itn, fillvalue=None)

# 演示用于合并的生成器函数:
print('-' * 10)
print(list(itertools.chain('ABC', range(2))))
# 如果只传入一个可迭代的对象,那么chain函数没什么用
print(list(itertools.chain(enumerate('ABC'))))
print(list(enumerate('ABC')))
# chain.from_iterable函数从可迭代的对象中获取每个元素,然后按顺序把元素连接起来
print(list(itertools.chain.from_iterable(enumerate('ABC'))))
print(list(zip('ABC', range(5))))
print(list(zip('ABC', range(5), [10, 20, 30, 40])))
print(list(itertools.zip_longest('ABC', range(5))))
print(list(itertools.zip_longest('ABC', range(5), fillvalue='?')))

# 演示itertools.product生成器函数:
print('-' * 10)
print(list(itertools.product('ABC', range(2))))
suits = 'spades hearts diamonds clubs'.split()
print(list(itertools.product('AK', suits)))
print(list(itertools.product('ABC')))
print(list(itertools.product('ABC', repeat=2)))
print(list(itertools.product(range(2), repeat=3)))
rows = itertools.product('AB', range(2), repeat=2)
for row in rows:
    print(row)

# 4).有些生成器函数会从一个元素中产出多个值,扩展输入的可迭代对象
# itertools.combinations(it, out_len)
# itertools.combinations_with_replacement(it, out_len)
# itertools.count(start=0, step=1)
# itertools.cycle(it)
# itertools.permutations(it, out_len=None)
# itertools.repeat(item, [times])

# 演示count,repeat和cycle的用法:
ct = itertools.count()
print('-' * 10)
print(next(ct))
print(next(ct))
print(list(itertools.islice(itertools.count(1, 0.3), 3)))
cy = itertools.cycle('ABC')
print(next(cy))
print(list(itertools.islice(cy, 7)))
rp = itertools.repeat(7)  # 构建一个repeat生成器始终产出数字7
print(next(rp), next(rp))
print(list(itertools.repeat(8, 4)))
print(list(map(operator.mul, range(11), itertools.repeat(5))))

# 演示combinations,combinations_with_replacement和permutations的用法:、
print('-' * 10)
print(list(itertools.combinations('ABC', 2)))
print(list(itertools.combinations_with_replacement('ABC', 2)))
print(list(itertools.permutations(range(3), 2)))
print(len(list(itertools.permutations(range(3), 2))))
print(list(itertools.product('ABC', repeat=2)))

# 5).用于重新排列元素的生成器函数
# 用于产出输入的可迭代对象中的全部元素,会以某种方式重新排列
# itertools.groupby(it, key=None)
# reversed(seq)
# itertools.tee(it, n=2)

# itertools.groupby函数的用法
print('-' * 10)
print(list(itertools.groupby('LLLLAAGGG')))
for char, group in itertools.groupby('LLLLAAGGG'):
    print(f'{char}->{list(group)}')
animals = ['duck', 'eagle', 'rat', 'giraffe', 'bear',
           'bat', 'dolphin', 'shark', 'lion']
animals.sort(key=len)
print(animals)
for length, group in itertools.groupby(animals, len):
    print(f'{length}->{list(group)}')
for length, group in itertools.groupby(reversed(animals), len):
    print(f'{length}->{list(group)}')

# itertools.tee函数产出多个生成器,每个生成器都可以产出输入的各个元素
print('-' * 10)
print(list(itertools.tee('ABC')))
g1, g2 = itertools.tee('ABC')
print(next(g1))
print(next(g2))
print(next(g2))
print(list(g1))
print(list(g2))
print(list(zip(*itertools.tee('ABC', 3))))


# --------------------------------------------------
# 14.10 Python3.3中新出现的句法:yield from
print('*' * 50)



"""
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
"""
