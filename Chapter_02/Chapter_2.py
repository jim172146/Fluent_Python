__author__ = 'fmy'

import dis
import os
from collections import namedtuple
from collections import deque
import bisect
import sys
import random
from array import array
import numpy
from time import perf_counter


"序列构成的数组"

# --------------------------------------------------
# list 可变序列、容器序列
# list comprehension（列表推导）简称listcomps
# generator expression（生成式表达器）简称genexps

symbols = '$¢£¥€¤'
codes1 = []
for symbol in symbols:
    codes1.append(ord(symbol))
print(codes1)
codes2 = [ord(symbol) for symbol in symbols]
print(codes2)
"""
Python 会忽略代码里 []、{} 和 () 中的换行，因此如果你的
代码里有多行的列表、列表推导、生成器表达式、字典这一类的，可以
省略不太好看的续行符\
"""
# Python3 表达式内部有自己的局部作用域
x = 'ABC'
dummy = [ord(x) for x in x]
print(x)
print(dummy)

symbols = '$¢£¥€¤'
beyond_ascii1 = [ord(symbol) for symbol in symbols
                 if ord(symbol) > 127]
print(beyond_ascii1)
beyond_ascii2 = list(filter(lambda ord_x: ord_x > 127,
                            map(ord, symbols)))
print(beyond_ascii2)

# 列表推导计算笛卡尔积
colors = ['black', 'white']
sizes = ['S', 'M', 'L']
tshirts1 = [(color, size) for color in colors
            for size in sizes]
print(tshirts1)
for color in colors:
    for size in sizes:
        print(color, size)
tshirts2 = [(color, size) for size in sizes
            for color in colors]
print(tshirts2)

# 生成器表达式用()表示，相比于列表推导式，能节约内存
symbols = '$¢£¥€¤'
a = tuple(ord(symbol) for symbol in symbols)
print(a)

# --------------------------------------------------
# tuple 不可变序列 容器序列
print('*' * 50)
# 元组与记录
lax_coordinates = (33.9425, -118.408056)
city, year, pop, chg, area = ('Tokyo', 2003, 32450, 0.66, 8014)
traveler_ids = [('USA', '31195855'), ('BRA', 'CE342567'),
                ('ESP', 'XDA205856')]
for passport in sorted(traveler_ids):
    print('%s/%s' % passport)

for country, _ in traveler_ids:
    print(country)

# 元组拆包
lax_coordinates = (33.9425, -118.408056)
latitude, longitude = lax_coordinates
t = (20, 8)
print(divmod(*t))
quotient, remainder = divmod(*t)
print(quotient, remainder)
_, filename = os.path.split('/home/luciano/.ssh/idrsa.pub')
print(filename)
a, b, *rest = range(5)
print(a, b, rest)
a, b, *rest = range(3)
print(a, b, rest)
a, b, *rest = range(2)
print(a, b, rest)
# ValueError: not enough values to unpack
# a, b, *rest = range(1)
# print(a, b, rest)
a, *body, c, d = range(5)
print(a, body, c, d)
a, *body, c, d = range(3)
print(a, body, c, d)
# ValueError: not enough values to unpack
# a, *body, c, d = range(2)
# print(a, body, c, d)
*head, b, c = range(5)
print(head, b, c)

# 嵌套元组拆包
metro_areas = [
    ('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
    ('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
    ('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
    ('New York-Newark', 'US', 20.104, (40.808611, -74.020386)),
    ('Sao Paulo', 'BR', 19.649, (-23.547778, -46.635833)),
]
print('{:15}|{:^9}|{:^9}'.format('', 'lat.', 'long.'))
fmt = '{:15}|{:^9.2f}|{:^9.2f}'
# ^居中对其 <左对齐 >右对齐
for name, cc, pop, (latitude, longitude) in metro_areas:
    if longitude <= 0:
        print(fmt.format(name, latitude, longitude))

# 具名元组
# collections.namedtuple：工厂函数，可构建带字段名的元组和有名字的类
City = namedtuple('City', 'name country population coordinates')
tokyo = City('Tokyo', 'Jp', 36.933, (35.68722, 139.691667))
print(tokyo)
print(tokyo.population)
print(tokyo.coordinates)
print(tokyo[1])
# 类属性_fields是包含类所有字段名称的元组
print(City._fields)
# _make()可以通过接受一个可迭代对象来生成实例
LatLong = namedtuple('LatLong', 'lat long')
delhi_data = ('Delhi NCR', 'IN', 21.935, LatLong(28.613889, 77.208889))
delhi = City._make(delhi_data)
print(delhi)
print(delhi.coordinates)
# _asdict()把具名元组以collection.OrderedDict的形式返回
print(delhi._asdict())
for key, value in delhi._asdict().items():
    print(key + ':', value)

# 作为不可变列表的元组
# 如果要把元组当作列表来用的话，最好先了解一下它们的相似度如何。
# 除了跟增减元素相关的方法之外，元组支持列表的其他所有方法。
# 还有一个例外，元组没有 __reversed__ 方法，但是这个方法只是个优化而已，
# reversed(my_tuple) 这个用法在没有 __reversed__ 的情况下也是合法的。


# --------------------------------------------------
# 切片
print('*' * 50)
# 为什么切片和区间会忽略最后一个元素
# 1.当只有最后一个位置信息时，我们也可以快速看出切片和区间里有几个元素：
# range(3)和my_list[:3]都返回3个元素。
# 2.当起止位置信息都可见时，我们可以快速计算出切片和区间的长度，
# 用后一个数减去第一个下标（stop - start）即可。
# 3.这样做也让我们可以利用任意一个下标来把序列分割成不重叠的两部分，
# 只要写成 my_list[:x] 和 my_list[x:] 就可以了
my_list = [10, 20, 30, 40, 50]
print(my_list[:2])
print(my_list[2:])

# 可以用 s[a:b:c] 的形式对s在a和b之间以c为间隔取值。
# c的值还可以为负，负值意味着反向取值。

# 对对象进行切片
invoice = """
0.....6.................................40..........52.55........
1909  Pimoroni PiBrella                 $17.50      3  $52.50
1489  6mm Tactile Switch x20            $4.95       2  $9.90 
1510  Panavise Jr. - PV-201             $28.00      1  $28.00
1601  PiTFT Mini Kit 320x240            $34.95      1  $34.95
"""

SKU = slice(0, 6)
DESCRIPTION = slice(6, 40)
UNIT_PRICE = slice(40, 52)
QUANTITY = slice(52, 55)
ITEM_TOTAL = slice(55, None)
line_items = invoice.split('\n')[2:-1]
for item in line_items:
    print(item[ITEM_TOTAL], item[QUANTITY], item[UNIT_PRICE],
          item[DESCRIPTION], item[SKU])

# 多维切片和省略
# 在 NumPy 中，... 用作多维数组切片的快捷方式。如果 x 是四维数组，
# 那么 x[i, ...] 就是 x[i, :, :, :] 的缩写

# 给切片赋值
my_list = list(range(10))
print(my_list)
# my_list[3::2] = [11, 22]
# print(my_list)
# Traceback->ValueError: attempt to assign sequence of size 2 to extended slice of size 4
my_list[2:5] = [20, 30]
print(my_list)
del my_list[5:7]
print(my_list)
my_list[3::2] = [11, 22]
print(my_list)
# my_list[2:5] = 100
# Traceback->TypeError: can only assign an iterable
my_list[2:5] = [100]
print(my_list)

# 对序列使用+和*
l = [1, 2, 3]
print(l * 5)
print(5 * 'a b c d ' + 'e f g')
# 如果在a * n这个语句中，序列a里的元素是对其他可变对象的引用的话，
# 需格外注意了，因为结果可能会出乎意料。比如用my_list = [[]] * 3
# 来初始化一个由列表组成的列表，但是你得到的列表里包含的3个元素其实是3个引用
# 而且这3个引用指向的都是同一个列表.

# 建立由列表组成的列表
board = [['_'] * 3 for i in range(3)]
print(board)
board[1][2] = 'X'
print(board)
# 错误的方法如下
print('错误的方法')
weird_board = [['_'] * 3] * 3
print(weird_board)
weird_board[1][2] = 0
print(weird_board)
# 另外一种错误方法
print('另外一种错误方法')
row = ['_'] * 3
board = []
for _ in range(3):
    board.append(row)
print(board)
board[1][2] = 2
print(board)
# 一种正确的方法
print('一种正确的方法')
board = []
for _ in range(3):
    row = ['_'] * 3
    board.append(row)
print(board)
board[1][2] = 0
print(board)

# --------------------------------------------------
# 序列的增量赋值
# 增量赋值运算符 += 和 *= 的表现取决于它们的第一个操作对象
l = [1, 2, 3]
print(id(l))
l *= 2
print(id(l))
t = (1, 2, 3)
print(id(t))
t *= 2
print(id(t))
# 对不可变序列进行重复拼接操作的话，效率会很低，因为每次都有一个新对象，
# 而解释器需要把原来对象中的元素先复制到新的对象里，然后再追加新的元素
t = (1, 2, [30, 40])
try:
    t[2] += [50, 60]
except TypeError as e:
    print(e)
print(t)
dis.dis('s[a] += b')
"""
· 不要把可变对象放在元组里面。
· 增量赋值不是一个原子操作。我们刚才也看到了，它虽然抛出了异常，但还是完成了操作。
· 查看 Python 的字节码并不难，而且它对我们了解代码背后的运行机制很有帮助。
"""

# --------------------------------------------------
# list.sort方法和内置函数sorted
fruits = ['grape', 'raspberry', 'apple', 'banana']
print(sorted(fruits))
print(fruits)
print(sorted(fruits, key=len))
print(sorted(fruits, key=len, reverse=True))
print(fruits)
fruits.sort()
print(fruits)

# --------------------------------------------------
# 用bisect来管理已排序的序列
HAYSTACK = [1, 4, 5, 6, 8, 12, 15, 20, 21, 23, 23, 26, 29, 30]
NEEDLES = [0, 1, 2, 5, 8, 10, 22, 23, 29, 30, 31]
ROW_FMT = '{0:2d} @ {1:2d}    {2}{0:<2d}'


def demo(bisect_fn) -> print:
    for needle in reversed(NEEDLES):
        position = bisect_fn(HAYSTACK, needle)
        offset = position * '  |'
        print(ROW_FMT.format(needle, position, offset))


if __name__ == '__main__':
    if sys.argv[-1] == 'left':
        bisect_fn = bisect.bisect_left
    else:
        bisect_fn = bisect.bisect
    print('DEMO:', bisect_fn.__name__)
    print('haystack ->', ' '.join('%2d' % n for n in HAYSTACK))
    demo(bisect_fn)


# bisect 函数其实是 bisect_right 函数的别名，后者还有个姊妹函数叫 bisect_left。
# 它们的区别在于，bisect_left 返回的插入位置是原序列中跟被插入元素相等的元素的位置，
# 新元素会被放置于它相等的元素的前面，而bisect_right返回的则是跟它相等的元素之后的位置


def grade(score, grades='FDCBA', breakpoints=None):
    if breakpoints is None:
        breakpoints = [60, 70, 80, 90]
    i = bisect.bisect(breakpoints, score)
    return grades[i]


print([grade(score) for score in [33, 99, 77, 70, 89, 90, 100]])


SIZE = 7
my_list = []
for i in range(SIZE):
    new_item = random.randrange(SIZE*2)
    bisect.insort(my_list, new_item)
    print('%2d ->' % new_item, my_list)


# --------------------------------------------------
# 当列表不是首选时
floats = array('d', (random.random() for i in range(10**4)))
print(floats[-1])
fp = open('floats.bin', 'wb')
floats.tofile(fp)
numpy.save('floats-10M', floats)
fp.close()
floats2 = array('d')
fp = open('floats.bin', 'rb')
floats2.fromfile(fp, 10**4)
fp.close()
floats3 = numpy.load('floats-10M.npy', 'r+')
floats3 *= 3
print(floats3[-1])
print(floats2[-1])
print(floats == floats2)


# 短整型有符号整数'h',无符号字符'B'
numbers = array('h', [-2, -1, 0, 1, 2])
memv = memoryview(numbers)
print(memv)
print(len(memv))
print(memv[0])
memv_oct = memv.cast('B')
print(memv_oct.tolist())
memv_oct[5] = 4
memv_oct[7] = 4
print(numbers)
print(bin(0))
print(bin(1024))


# NumPy 和 SciPy
a = numpy.arange(12)
print(a)
print(type(a))
print(a.shape)
a.shape = 3, 4
print(a)
print(a[2])
print(a[2, 1])
print(a[:, 1])
print(a.transpose())

t0 = perf_counter()
n = 100000
sum_n = 0
while n >= 0:
    sum_n += n
    n -= 1
print(perf_counter() - t0)

# 双向队列和其他形式的队列
dq = deque(range(10), maxlen=10)
print(dq)
dq.rotate(3)
print(dq)
dq.append(-1)
print(dq)
dq.extend([11, 22, 33])
print(dq)
dq.extendleft([10, 20, 30, 40, 50])
print(dq)
