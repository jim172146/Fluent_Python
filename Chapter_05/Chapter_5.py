__author__ = 'fmy'

import collections
import functools
import inspect
import operator
import random
import unicodedata

"一等函数"
# 在Python中,函数是一等对象,编程语言理论家把'一等对象'定义为满足下述条件的程序实体
# · 在运行时创建
# · 能赋值给变量或者数据结构中的元素
# · 能作为参数传给函数
# · 能作为函数的返回结果
# 在Python中,整数、字符串和字典都是一等对象


# --------------------------------------------------
# 5.1 把函数视为对象
print('*' * 50)


# 创建并测试一个函数,然后读取它的__doc__属性,再检查其类型


def factorial(n):  # 控制台会话,再运行时创建一个函数
    """return n!"""
    return 1 if n < 2 else n * factorial(n - 1)


print(factorial(20))
print(factorial.__doc__)  # __doc__属性是众多属性中的一个
print(type(factorial))  # factorial 是 function 类的实例
print(help(factorial))  # 函数的帮助内容

# 通过别的名称使用函数,再把函数作为参数传递
fact = factorial
print(factorial)
print(fact)
print(fact(5))
print(map(fact, range(11)))
print(list(map(fact, range(11))))

# --------------------------------------------------
# 5.2 高阶函数
print('*' * 50)
# 接受函数作为参数,或者把函数作为结果返回的函数是高阶函数(high-order function)
# 再函数式编程中,最为人熟悉的高阶函数有map,filter和reduce
# map函数就是高阶函数,sorted也是:可选的key参数提供一个函数,应用到各个元素的排序
# 根据单词长度给一个列表排序
fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
print(sorted(fruits, key=len))


# 根据反向拼写给一个单词列表排序


def reverse(word):
    """返回一个单词的反向拼写"""
    return word[::-1]


print(reverse('testing'))
print(fruits)
print(sorted(fruits, key=reverse))

# 计算阶乘列表:map和filter与列表推导比较
print(list(map(fact, range(6))))  # 使用map函数
print([fact(n) for n in range(6)])  # 列表推导
print(list(map(fact, filter(lambda n: n % 2, range(6)))))  # 使用map和filter函数
print([fact(n) for n in range(6) if n % 2])  # 列表推导

# 使用reduce和sum计算0~99之和
print(functools.reduce(operator.add, range(100)))
print(sum(range(100)))
# sum和reduce的通用思想是把某个操作连续应用到序列的元素上,累计之前的结果归化成一个值
# all和any是内置的归约函数
# all(iterable),如果iterable的每个元素都是真值,返回True;all([])返回True
print(all([]))
print(all([0]))
# any(iterable),如果iterable有一元素都是真值,返回True;any([])返回False
print(any([]))
print(any([1]))

# --------------------------------------------------
# 5.3 匿名函数
print('*' * 50)
# lambda关键字再Python表达式内创建匿名函数
# 使用lambda表达式发转拼写,并排序
fruits = ['strawberry', 'fig', 'apple', 'cherry', 'raspberry', 'banana']
print(sorted(fruits, key=lambda word: word[::-1]))
# 除了作为参数传给高阶函数,很少使用匿名函数.因为复杂的lambda表达式难阅读、难写

# --------------------------------------------------
# 5.4 可调用对象
print('*' * 50)
# 除了用户定义的函数,调用运算符(即())还可以应用到其他对象上
# callable()函数可以判断对象能否调用
# 一些可调用对象
# ·用户定义函数---使用def语句或lambda表达式创建
# ·内置函数---使用C语言(CPython)实现的函数,如len或time.strftime
# ·内置方法---使用C语言实现的方法,如dict.get
# ·方法---在类的定义中定义的函数
# ·类---调用类时会运行类的__new__方法创建一个实例,然后运行__init__方法,初始化实例,最后把实例返回给调用方
# ·类的实例---如果定义了__call__方法,那么它的实例可以作为函数调用
# ·生成器函数---使用yield关键字的函数或方法,调用生成器函数返回的是生成器对象
print(abs, str, 13)
print([callable(obj) for obj in (abs, str, 13)])

# --------------------------------------------------
# 5.5 用户定义的可调用类型
print('*' * 50)


# 不仅Python函数是真正的对象,任何Python对象都可以表现得想函数,只需实现实例方法__call__
# 使用BingoCage实例,从打乱的列表中取出一个元素
class BingoCage:
    def __init__(self, items):
        self._item = list(items)  # __init__接受任何可迭代对象,在本地构建一个副本,防止列表参数的意外副作用
        random.shuffle(self._item)  # shuffle可以打乱列表的顺序

    def pick(self):  # 起主要作用的方法
        try:
            return self._item.pop()
        except IndexError:
            raise LookupError('pick from empty BingoCage')  # 如果self._item为空,抛出异常

    def __call__(self):  # bingo.pick() 的快捷方式 bingo()
        return self.pick()


bingo = BingoCage(range(222))
print(bingo.pick())
print(bingo())

# --------------------------------------------------
# 5.6 函数内省
# 把函数视为对象处理,运行时内省
print('*' * 50)
print(dir(factorial))


# 函数使用__dict__属性存储赋予它的用户属性

# 列出常规对象没有而函数有的属性
class C(object): pass


obj = C()


def func(): pass


print(sorted(set(dir(func)) - set(dir(obj))))
# 类实例没有而函数有的属性列表
# __annotations__ ---dict           ---参数和返回值的注解
# __call__        ---method-wrapper ---实现()运算符,即可调用对象协议
# __closure__     ---tuple          ---函数闭包,即自变量的绑定
# __code__        ---code           ---编译成字节码的函数元数据和函数定义体
# __defaults__    ---tuple          ---编译成字节码的函数元数据和函数定义体
# __get__         ---method-wrapper ---实现只读描述协议
# __globals__     ---dict           ---函数所在模块中的全局变量
# __kwdefaults__  ---dict           ---仅限关键字形式参数的默认值
# __name__        ---str            ---函数名称
# __qualname__    ---str            ---函数的限定名称

# --------------------------------------------------
# 5.7 从定位参数到仅限关键字参数
print('*' * 50)


# tag函数用于生成HTML标签;使用名为cls的关键字参数传入'class'属性,这时一种变通方法
def tag(name, *content, cls=None, **attrs):
    """生成一个或多个HTML标签"""
    if cls is not None:
        attrs['class'] = cls
    if attrs:
        attr_str = ''.join(' %s="%s"' % (attr, value)
                           for attr, value in sorted(attrs.items()))
    else:
        attr_str = ''
    if content:
        return '\n'.join('<%s%s>%s</%s>' %
                         (name, attr_str, c, name) for c in content)
    else:
        return '<%s%s />' % (name, attr_str)


print(tag('br'))  # 传入单个定位参数,生成一个指定名称的空标签
print(tag('p', 'hello'))  # 第一个参数后的任意个参数会被*content捕捉,存入一个元组
print(tag('p', 'hello', 'world'))
print(tag('p', 'hello', id=33))  # tag函数没有指定名称的关键字参数会被**attrs捕获,存入一个字典
print(tag('p', 'hello', 'world', cls='sidebar'))  # clc参数只能作为关键字参数传入
print(tag(content='testing', name='img'))  # 调用tag函数时,即便第一个定位参数也能作为关键字参数传入
my_tag = {'name': 'img', 'title': 'Sunset Boulevard',
          'src': 'sunset.jpg', 'cls': 'framed'}
print(tag(**my_tag))  # 在my_tag前面加上**,字典中的所有元素作为单个参数传入,同名键会绑定到对应的具名参数上,余下的被**attrs捕获


# 定义函数时若想指定仅限关键字参数,要把它们放在最前面有*的参数后面
# 若不想支持数量不定的定位参数,但想支持仅限关键字参数,在签名中放一个*，如下
def f(a, *, b):
    return a, b


print(f(1, b=2))

# --------------------------------------------------
# 5.8 获取关于参数的信息
print('*' * 50)


# 在指定长度附近截断字符串的函数
def clip(text, max_len=80):
    """在max_len前或后面的第一个空格处截断文字"""
    end = None
    if len(text) > max_len:
        space_before = text.rfind(' ', 0, max_len)
        if space_before >= 0:
            end = space_before
        else:
            space_before = text.rfind(' ', max_len)
        if space_before >= 0:
            end = space_before
    if end is None:  # 没找到空格
        end = len(text)
    return text[:end].rstrip()


print(clip.__defaults__)
print(clip.__code__)
print(clip.__code__.co_varnames)
print(clip.__code__.co_argcount)

# 提取函数的签名
sig = inspect.signature(clip)
print(sig)
print(str(sig))
for name, param in sig.parameters.items():
    print(param.kind, ':', name, '=', param.default)
# kind属性是_ParameterKind类中的5个值之一,如下
# POSITIONAL_OR_KEYWORD,可以通过定位参数和关键字参数传入的形参
# VAR_POSITIONAL,定位参数数组
# VAR_KEYWORD,关键字参数字典
# KEYWORD_ONLY,仅限关键字参数
# POSITIONAL_ONLY,仅限定位参数

# 把tag函数的签名绑定到一个参数字典上
sig = inspect.signature(tag)  # 获取tag函数的签名
my_tag = {'name': 'img', 'title': 'Sunset Boulevard',
          'src': 'sunset.jpg', 'cls': 'framed'}
bound_args = sig.bind(**my_tag)  # 把一个字典参数传给.bind()方法
print(bound_args)  # 打印inspect.BoundArguments对象
for name, value in bound_args.arguments.items():  # 迭代bound_args.arguments(OrderedDict对象)中的元素
    print(name, '=', value)
del my_tag['name']  # 把必须指定的参数name从my_tag中删除

# --------------------------------------------------
# 5.9 函数注解
print('*' * 50)


# 有注解的clip函数,type hints
def clip(text: str, max_len: int = 80) -> str:
    """在max_len前或后面的第一个空格处截断文字"""
    end = None
    if len(text) > max_len:
        space_before = text.rfind(' ', 0, max_len)
        if space_before >= 0:
            end = space_before
        else:
            space_before = text.rfind(' ', max_len)
        if space_before >= 0:
            end = space_before
    if end is None:  # 没找到空格
        end = len(text)
    return text[:end].rstrip()


# 函数声明中的各个参数可以在(:)之后增加注解表达式,若参数有默认值,注解放在参数名和=之间
# 注解返回值,在)和:之间添加->和一个表达式
# 注解不会做任何处理,指挥存储在__annotations__属性中
print('-' * 10)
for name, value in clip.__annotations__.items():
    print(name, '=', '%s' % value)
print(clip.__annotations__)
print(inspect.signature(clip))

# 从函数签名中提取注解
sig = inspect.signature(clip)
print(sig.return_annotation)
print('-' * 10)
for param in sig.parameters.values():
    note = repr(param.annotation).ljust(13)
    print(note, ':', param.name, '=', param.default)

# --------------------------------------------------
# 5.10 支持函数式编程的包
print('*' * 50)


# 1).operator模块
# 使用reduce函数和一个匿名函数计算阶乘
def fact(n):
    return functools.reduce(lambda a, b: a * b, range(1, n + 1))


# operator模块为算数运算符提供对应的函数,从而避免写lambda: a, b: a*b 这种平凡函数
# 使用reduce和operator.mul函数计算阶乘
def fact_1(n):
    return functools.reduce(operator.mul, range(1, n+1))


print(fact(4))
print(fact_1(4))

# operator模块中有一类函数,能替代从序列中取出元素或读取对象属性的lambda表达式
# 因此itemgetter和attrgetter其实会自动构建函数
# 演示使用itemgetter排序一个元组列表
metro_data = [
    ('Tokyo', 'JP', 36.933, (35.689722, 139.691667)),
    ('Delhi NCR', 'IN', 21.935, (28.613889, 77.208889)),
    ('Mexico City', 'MX', 20.142, (19.433333, -99.133333)),
    ('New York-Newark', 'US', 20.104, (40.808611, -74.020386)),
    ('Sao Paulo', 'BR', 19.649, (-23.547778, -46.635833)),
]
for city in sorted(metro_data, key=operator.itemgetter(1)):
    print(city)  # operator.itemgetter(1) 等价于 key=lambda fields: fields[1]

cc_name = operator.itemgetter(0, 1)
for city in metro_data:  # 多个参数传给itemgetter,它构建的函数会返回提取的值构建的元组
    print(cc_name(city))
# operator.itemgetter使用[]运算符,因此不仅支持序列,还支持映射和任意实现__getitem__方法的类

# attrgetter和itemgetter类似,它创建的函数根据名称提取对象的属性,传入多个对象同样返回元组
# dinginess一个namedtuple,名为metro_data,演示使用attrgetter处理它
print('-' * 10)
LatLong = collections.namedtuple('LatLong', 'lat long')  # 使用namedtuple定义LatLong
Metropolis = collections.namedtuple('Metropolis', 'name cc pop coord')  # 再定义Metropolis
# 使用Metropolis实例构建metro_areas列表,注意使用嵌套的元组拆包提取(lat, long)
# 然后使用他们构建LatLong,作为Metropolis的coord属性
metro_areas = [Metropolis(name, cc, pop, LatLong(lat, long))
               for name, cc, pop, (lat, long) in metro_data]
print(metro_areas[0])
print(metro_areas[0].coord.lat)  # 深入metro_areas[0],获取它的纬度
name_lat = operator.attrgetter('name', 'coord.lat')  # 定义一个attrgetter,获取name属性和嵌套的coord.lat属性
for city in sorted(metro_areas, key=operator.attrgetter('coord.lat')):  # 使用attrgetter,按照维度排序
    print(name_lat(city))  # 使用name_lat定义的attrgetter,只显示城市和维度

operator_list = [name for name in dir(operator) if not name.startswith('_')]
print(operator_list)
print(len(operator_list))
# ['abs', 'add', 'and_', 'attrgetter', 'concat', 'contains', 'countOf',
# 'delitem', 'eq', 'floordiv', 'ge', 'getitem', 'gt', 'iadd', 'iand',
# 'iconcat', 'ifloordiv', 'ilshift', 'imatmul', 'imod', 'imul', 'index',
# 'indexOf', 'inv', 'invert', 'ior', 'ipow', 'irshift', 'is_', 'is_not',
# 'isub', 'itemgetter', 'itruediv', 'ixor', 'le', 'length_hint', 'lshift',
# 'lt', 'matmul', 'methodcaller', 'mod', 'mul', 'ne', 'neg', 'not_', 'or_',
# 'pos', 'pow', 'rshift', 'setitem', 'sub', 'truediv', 'truth', 'xor']
# 以i开头、后面是另一个运算符的那些名称,如iadd,对应的是增量赋值运算符,如+=等
# 如果第一个参数是可变的,那么这些运算符函数会就地修改它;否则作用与不带i的函数一样,直接返回运算结果

# operator.methodcaller使用实例
s = 'The time has come'
upcase = operator.methodcaller('upper')
print(upcase(s))
hiphenate = operator.methodcaller('replace', ' ', '-')
print(hiphenate(s))

print(str.upper(s))  # 如果想把 str.upper 作为函数使用

# 2).使用functools.partial冻结参数
# functools模块提供了一系列高阶函数,其中最为人熟知的或许是reduce
# 余下的函数中,最有用的是partial及其变体partialmethod
# functools.partial 这个高阶函数用于部分应用一个函数
# 部分应用是指:基于一个函数创建一个新的可调用对象,把原函数的某些参数固定

# 使用partial把一个两参数函数改编成需要单参数的可调用对象
triple = functools.partial(operator.mul, 3)  # 使用mul创建triple函数,第一个参数固定为3
print(triple(7))
print(list(map(triple, range(1, 10))))

# 使用partial构建一个便利的Unicode规范化函数
nfc = functools.partial(unicodedata.normalize, 'NFC')
s1 = 'café'
s2 = 'cafe\u0301'
print(s1, s2)
print(s1 == s2)
print(nfc(s1) == nfc(s2))

# partial应用到上文的tag函数上
print(tag)
picture = functools.partial(tag, 'img', cls='pic-frame')
print(picture(src='wumpus.jepg'))
print(picture)  # picture 返回一个functools.partial对象
print('-' * 10)
print(f'{picture.func}\n'
      f'{picture.args}\n'
      f'{picture.keywords}')  # 提供访问原函数和固定参数的属性
