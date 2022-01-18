__author__ = 'fmy'

import builtins
import collections.abc
import sys
import re
from types import MappingProxyType
from unicodedata import name


"字典和集合"

# --------------------------------------------------
# 3.1 泛映射类型
my_dict = {}
print(isinstance(my_dict, collections.abc.Mapping))

tt = (1, 2, (30, 40))
print(hash(tt))
tl = (1, 2, [30, 40])
try:
    print(hash(tl))
except TypeError as e:
    print(e)
tf = (1, 2, frozenset([30, 40]))
print(hash(tf))

a = dict(one=1, two=2, three=3)
b = {'one': 1, 'two': 2, 'three': 3}
c = dict(zip(['one', 'two', 'three'], [1, 2, 3]))
d = dict({'three': 3, 'one': 1, 'two': 2})
print(a == b == c == d)

# --------------------------------------------------
# 3.2 字典推导
print('*' * 50)
DIAL_CODES = [
    (86, 'China'),
    (91, 'India'),
    (1, 'United States'),
    (62, 'Indonesia'),
    (55, 'Brazil'),
    (92, 'Pakistan'),
    (880, 'Bangladesh'),
    (234, 'Nigeria'),
    (7, 'Russia'),
    (81, 'Japan'),
]

country_code = {country: code for code, country in DIAL_CODES}
print(country_code)
country_code1 = {code: country.upper() for code, country in DIAL_CODES
                 if code < 66}
print(country_code1)


# --------------------------------------------------
# 3.3 常见的映射方法
print('*' * 50)
WORD_RE = re.compile(r'\w+')
index = {}
with open(sys.argv[0], encoding='utf-8') as fp:
    for line_no, line in enumerate(fp, 1):
        for match in WORD_RE.finditer(line):
            word = match.group()
            column_no = match.start() + 1
            location = (line_no, column_no)
            occurrences = index.get(word, [])
            occurrences.append(location)
            index[word] = occurrences
for word in sorted(index, key=str.upper):
    print(word, index[word])

WORD_RE = re.compile(r'\w+')
index = {}
with open(sys.argv[0], encoding='utf-8') as fp:
    for line_no, line in enumerate(fp, 1):
        for match in WORD_RE.finditer(line):
            word = match.group()
            column_no = match.start() + 1
            location = (line_no, column_no)
            index.setdefault(word, []).append(location)
for word in sorted(index, key=str.upper):
    print(word, index[word])

# --------------------------------------------------
# 3.4 映射的弹性键查询
print('*' * 50)
# defaultdict:处理找不到键的一个选择

WORD_RE = re.compile(r'\w+')
index = collections.defaultdict(list)
with open(sys.argv[0], encoding='utf-8') as fp:
    for line_no, line in enumerate(fp):
        for match in WORD_RE.finditer(line):
            word = match.group()
            column_no = match.start() + 1
            location = (line_no, column_no)
            index[word].append(location)
for word in sorted(index, key=str.upper):
    print(word, index[word])


# 把 list 构造方法作为 default_factory 来创建一个 defaultdict。
# 如果 index 并没有 word 的记录，那么 default_factory 会被调用，为查询不到的键创造
# 一个值。这个值在这里是一个空的列表，然后这个空列表被赋值给 index[word]，继而被当作
# 返回值返回，因此 .append(location) 操作总能成功。

# 特殊方法__missing__
# 所有的映射类型在处理找不到的键的时候，都会牵扯到 __missing__ 方法
# __missing__ 方法只会被 __getitem__ 调用（比如在表达式 d[k] 中）


class StrKeyDict0(dict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or str(key) in self.keys()


d = StrKeyDict0([('2', 'two'), ('4', 'four')])
print(d['2'])
print(d[4])
# print(d[1])
print(d.get('2'))
print(d.get(4))
print(d.get(1, 'N/A'))
print(2 in d)
print(1 in d)


# --------------------------------------------------
# 3.5 字典的变种
print('*'*50)
# collections.OrderedDict
# 这个类型在添加键的时候会保持顺序,因此键的迭代次序总是一致的.OrderedDict
# 的 popitem 方法默认删除并返回的是字典里的最后一个元素,但是如果像 my_odict.
# popitem(last=False) 这样调用它,那么它删除并返回第一个被添加进去的元素.

# collections.ChainMap
pylook = collections.ChainMap(locals(), globals(), vars(builtins))
print(list(pylook.keys()))

# collections.Counter
# 这个映射类型会给键准备一个整数计数器.每次更新一个键的时候都会增加这个计数
# 器.所以这个类型可以用来给可散列表对象计数,或者是当成多重集来用——多重集合
# 就是集合里的元素可以出现不止一次.
# most_common([n]) 会按照次序返回映射里最常见的 n 个键和它们的计数
ct = collections.Counter('abracadabra')
print(ct)
ct.update('aaaaazzz')
print(ct)
print(ct.most_common(2))

# collections.UserDict
# 这个类其实就是把标准 dict 用纯 Python 又实现了一遍.跟 OrderedDict 、
# ChainMap 和 Counter 这些开箱即用的类型不同, UserDict 是让用户继承写子类


# --------------------------------------------------
# 3.6 子类化UseDict

class StrKeyDict(collections.UserDict):
    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, item):
        self.data[str(key)] = item


dd = StrKeyDict([('2', 'two'), ('4', 'four')])
print(dd['2'])
print(dd[4])
# print(dd[1])
print(dd.get('2'))
print(dd.get(4))
print(dd.get(1, 'N/A'))
print(2 in dd)
print(1 in dd)
# 因为 UserDict 继承的是 MutableMapping,所以 StrKeyDict 里剩下的那些映射类型的方法
# 都是从 UserDict、MutableMapping 和 Mapping 这些超类继承而来的.特别是最后的 Mapping
# 类,它虽然是一个抽象基类（ABC）,但它却提供了好几个实用的方法.以下两个方法值得关注

# MutableMapping.update
# 这个方法不但可以为我们所直接利用,它还用在 __init__ 里,让构造方法可以利用传
# 入的各种参数（其他映射类型、元素是 (key, value) 对的可迭代对象和键值参数）来
# 新建实例.因为这个方法在背后是用 self[key] = value 来添加新值的，所以它其实是
# 在使用我们的 __setitem__ 方法.

# Mapping.get
# 在StrKeyDict0中,我们不得不改写get方法,让它的表现跟__getitem__一致。
# 而在StrKeyDict中就没这个必要了,因为它继承了Mapping.get方法,这个方法
# 的实现方式跟 StrKeyDict0.get 是一模一样的。


# --------------------------------------------------
# 3.7 不可变映射类型
print('*'*50)
d = {1: 'A'}
print(d)
d_proxy = MappingProxyType(d)
print(d_proxy)
print(d_proxy[1])
# d_proxy[2] = 'x'
# print(d_proxy[2])
# d_proxy 是动态的，也就是说对 d 所做的任何改动都会反馈到它上面
d[2] = 'B'
print(d_proxy)
print(d_proxy[2])


# --------------------------------------------------
# 3.8 集合论
print('*'*50)
l = ['spam', 'spam', 'eggs', 'spam']
l_set = set(l)
l_frozenset = frozenset(l)
print(l_set)
print(l_frozenset)
print(list(l_set))

# 集合字面量
# 除空集之外，集合的字面量——{1}、{1, 2}，等等——看起来跟它的数学形式一模一样。
# 如果是空集，那么必须写成 set() 的形式。
# Python 里没有针对 frozenset 的特殊字面量句法，我们只能采用构造方法
ge_frozenset = frozenset(range(10))
print(ge_frozenset)

# 集合推导 setcomps
# 该集合里的每个字符的 Unicode 名字里都有 'SIGN' 这个单词
# 把编码在 32~255 之间的字符的名字里有“SIGN”单词的挑出来，放到一个集合里
set_setcomps = {chr(i) for i in range(32, 256) if 'SIGN' in name(chr(i), '')}
print(set_setcomps)

# 集合的操作
# 集合的数学运算符
# s & z --> s 和 z 的交集
# s &= z
# s | z --> s 和 z 的并集
# s |= z
# s - z --> s 和 z 的差集
# s -= z
# s ^ z --> s 和 z 的对称差集
# s ^=

# 集合的比较运算符
# e in s
# s <= z  <->   s >= z
# s < z   <->   s > z

# 集合类型的其他方法
# s.add(e)
# s.clear()
# s.copy()
# s.discard(e)
# s.__iter__()
# s.__len__()
# s.pop()
# s.remove(e)


# --------------------------------------------------
# 3.9 dict和set的背后
print('*'*50)
# • Python 里的 dict 和 set 的效率有多高？
# • 为什么它们是无序的？
# • 为什么并不是所有的 Python 对象都可以当作 dict 的键或 set 里的元素？
# • 为什么 dict 的键和 set 元素的顺序是跟据它们被添加的次序而定的，以及
#   为什么在映射对象的生命周期中，这个顺序并不是一成不变的？
# • 为什么不应该在迭代循环 dict 或是 set 的同时往里添加元素？

# 字典中的散列表
# 散列表其实是一个稀疏数组(总是有空白元素的数组称为稀疏数组).在一般的数据结构教材中,
# 散列表里的单元通常叫作表元(bucket).在 dict 的散列表当中，每个键值对都占用一个表元,
# 每个表元都有两个部分,一个是对键的引用,另一个是对值的引用.因为所有表元的大小一致,
# 所以可以通过偏移量来读取某个表元
# 要把一个对象放入散列表,首先要计算这个元素键的散列值,Python中可以用hash()方法来做这件事情

# dict的实现及其导致的结果
# 1.键必须是可散列的
# 2.字典在内存上的开销巨大
#   存放数量巨大的记录,那么放在由元组或是具名元组构成的列表中会是比较好的选择
# 3.键查询很快
# 4.键的次序取决于添加顺序
# 5.往字典里添加新键可能会改变已有键的顺序
DIAL_CODES = [
    (86, 'China'),
    (91, 'India'),
    (1, 'United States'),
    (62, 'Indonesia'),
    (55, 'Brazil'),
    (92, 'Pakistan'),
    (880, 'Bangladesh'),
    (234, 'Nigeria'),
    (7, 'Russia'),
    (81, 'Japan'),
]
d1 = dict(DIAL_CODES)
print('d1:', d1.keys())
d2 = dict(sorted(DIAL_CODES))
print('d2:', d2.keys())
d3 = dict(sorted(DIAL_CODES, key=lambda x: x[1]))
print('d3:', d3.keys())
assert d1 == d2 and d2 == d3

# set 的实现以及导致的结果
# set 和 frozenset 的实现也依赖散列表，但在它们的散列表里存放的只有元素的引用
# (就像在字典里只存放键而没有相应的值)
