__author__ = 'fmy'

import copy
import weakref

"对象引用、可变性和垃圾回收"
# 对象与对象名称之间的区别.名称不是对象,而是单独的东西

# --------------------------------------------------
# 8.1 变量不是盒子
print('*' * 50)
# 变量a,b引用同一个列表,而不是那个列表的副本
a = [1, 2, 3]
b = a
a.append(4)
print(b)
# 若把变量视为盒子,上面的结果无法解释,正确的是把变量视为便利贴
# 而且,对引用式变量来说,把变量分配给对象更合理:如把变量s分配给seesaw


# 创建对象之后才把变量分配给对象
class Gizmo:
    def __init__(self):
        print(f'Gizmo id:{id(self)}')


x = Gizmo()
# y = Gizmo() * 10  # 这里说明在尝试求积之前会创建一个新的实例.Traceback:TypeError
print(dir())  # 说明不会创建y变量,因为在赋值前右边求值抛出错误


# --------------------------------------------------
# 8.2 表示、相等性和别名
print('*' * 50)
# charles和lewis指代同一个对象
charles = {'name': 'Chrles L. Dodgson', 'born': 1983}
lewis = charles  # lewis是charles的别名
print(lewis is charles)
print(id(charles), id(lewis))
lewis['balance'] = 950
print(charles)

# alex与charles比较的结果是相等的,但alex不是charles
alex = {'name': 'Chrles L. Dodgson', 'born': 1983, 'balance': 950}
print(alex == charles)
print(alex is charles)
print(alex is not charles)
# 每个变量都有标识、类型和值.对象一旦创建,它的标识绝不会变;可以把标识理解为对象在内存中的地址
# is运算符比较两个对象的标识,id()函数返回对象标识的整数表示。

# 1).在==和is之间选择
# ==运算符比较对象的值,is运算符比较对象的标识
# 变量与单例值比较时,应该使用is,最常使用is检查变量绑定的值是不是None
print('-' * 10)
print(x is None)
print(x is not None)
# is运算符比==运算符速度快,因为它不能重载,不用寻找并调用特殊方法
# 而a == b是语法糖,等同于a.__eq__(b)

# 2).元组的相对不可变性
# 元组保存的是对象的引用,如果引用元素可变,则元组本身不可变但其元素可变

# 一开始,t1和t2相等,但是修改t1中的一个可变元素后,两者不相等了
print('-' * 10)
t1 = (1, 2, [30, 40])
t2 = (1, 2, [30, 40])
print(t1 == t2)
print(id(t1[-1]))
print(id(t2[-1]))
t1[-1].append(99)
print(id(t1[-1]))
print(t1 == t2)


# --------------------------------------------------
# 8.3 默认做浅复制
print('*' * 50)
l1 = [3, [55, 44], (7, 8, 9)]
l2 = list(l1)  # list(l1)创建l1的副本
print(l2, l1)
print(l2 == l1)
print(l2 is l1)
l2.append(99)
print(l2, l1)
# 对于列表和其他可变序列来说,还能使用简洁的l2 = l1[:]语句创建副本
# 构造方法和[:]做的是浅复制

# 在一个包含一个列表的列表中做浅复制
print('-' * 10)
l1 = [3, [66, 55, 44], (7, 8, 9)]
l2 = list(l1)  # l2是l1的浅复制副本
l1.append(100)
l1[1].remove(55)
print('l1:', l1)
print('l2:', l2)
print(f'id(l1):{id(l1)}\n'
      f'id(l1):{id(l1[:])}\n'
      f'id(l2):{id(l2)}\n'
      f'id(l2):{id(l2[:])}')
l2[1] += [33, 22]  # 对可变对象,+=运算符就地修改
l2[2] += (10, 11)  # 对元组来说,+=运算符创建一个新的元组,然后绑定给l2[2]
print('l1:', l1)
print('l2:', l2)
print(f'id(l1[1]):{id(l1[1])}\n'
      f'id(l2[1]):{id(l2[1])}\n'
      f'{id(l1[1]) == id(l2[1])}\n'
      f'id(l1[2]):{id(l1[2])}\n'
      f'id(l2[2]):{id(l2[2])}\n'
      f'{id(l1[2]) == id(l2[2])}')


# 为任意对象做深复制和浅复制
# 小车乘客在途中上车和下车
class Bus:
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []
        else:
            self.passengers = list(passengers)

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)


print('-' * 10)
bus1 = Bus(['Alice', 'Bill', 'Claire', 'David'])
bus2 = copy.copy(bus1)
bus3 = copy.deepcopy(bus1)
print(f'id(bus1)->{id(bus1)}\n'
      f'id(bus2)->{id(bus2)}\n'
      f'id(bus3)->{id(bus3)}')
print(f'bus1.passengers->{bus1.passengers}')
bus1.drop('Bill')
print(f'bus2.passengers->{bus2.passengers}')  # bus1中的'Bill'下车,bus2中也没有它了
print(f'bus3.passengers->{bus3.passengers}')  # bus3时深层复制副本,它的passengers属性只想另一个列表
print(f'id(bus1.passengers)->{id(bus1.passengers)}\n'
      f'id(bus2.passengers)->{id(bus2.passengers)}')

# 循环引用,b引用a,然后追加到a中;deepcopy会想办法复制a
print('-' * 10)
a = [1, 20]
b = [a, 30]
a.append(b)
print(f'a->{a}')
c = copy.deepcopy(a)
print(f'c->{c}')
print(f'id(a[2])->{id(a[2])}\n'
      f'id(c[2])->{id(c[2])}')


# --------------------------------------------------
# 8.4 函数的参数作为引用时
print('*' * 50)
# 可选参数可以有默认值,要避免使用可变的对象最为u函数的默认参数


# 1).不要使用可变类型作为参数的默认值
class HuntedBus:
    """备受幽灵乘客折磨的校车"""
    def __init__(self, passengers=[]):  # 若没传入passengers参数,使用默认绑定的列表对象,一开始是空列表
        self.passengers = passengers  # 这self.passengers是passengers的别名
        print(f'id(self.passengers):{id(self.passengers)}\n'
              f'id(passengers):\t\t{id(passengers)}')

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        self.passengers.remove(name)


bus1 = HuntedBus(['Alice', 'Bill'])
print(f'bus1.passengers->{bus1.passengers}')
bus1.pick('Claire')
bus1.drop('Alice')
print(f'bus1.passengers->{bus1.passengers}')
bus2 = HuntedBus()  # bus2是空的,因此把默认的空列表赋值给self.passengers
bus2.pick('Carrie')
print(f'bus2.passengers->{bus2.passengers}')
bus3 = HuntedBus()
print(f'bus3.passengers->{bus3.passengers}')   # 默认列表不为空！
bus3.pick('Dave')
print(f'bus2.passengers->{bus2.passengers}\n'
      f'bus3.passengers->{bus3.passengers}')
print(f'bus2.passengers is bus3.passengers: '
      f'{bus2.passengers is bus3.passengers}')
print(f'bus1.passengers->{bus1.passengers}')
print(dir(HuntedBus.__init__))
print(HuntedBus.__init__.__defaults__)
print(HuntedBus.__init__.__defaults__[0] is bus2.passengers)


# 2).防御可变参数
# 一个简单的类,说明接受可变参数的风险
class TwilightBus:
    """让乘客销声匿迹的校车"""
    def __init__(self, passengers=None):
        if passengers is None:
            self.passengers = []
        else:
            # 把self.passengers变成passengers的别名,而后者是传给 __init__方法的实参的别名
            self.passengers = passengers

    def pick(self, name):
        self.passengers.append(name)

    def drop(self, name):
        # 在self.passengers上调用remove()和append()方法其实会修改传给构造方法的那个列表
        self.passengers.remove(name)


print('-' * 10)
basketball_team = ['Sue', 'Tina', 'Maya', 'Diana', 'Part']  # 有五个学生的名字
bus = TwilightBus(basketball_team)  # 使用这队学生实例化TwilightBus
bus.drop('Tina')
bus.drop('Part')
print(basketball_team)  # 下车的学生从篮球队中消失了
print(f'id(basketball_team):{id(basketball_team)}\n'
      f'id(bus.passengers):\t{id(bus.passengers)}')
# 这里的问题在于校车为传给构造方法的列表创造了别名
# 正确的做法,校车自己维护乘客列表,把参数值的副本赋值给self.passengers
"""
正确做法
def __init__(self, passengers=None):
    if passengers is None:
        self.passengers = []
    else:
        self.passengers = list(passengers)
"""


# --------------------------------------------------
# 8.5 del和垃圾回收
print('*' * 50)
# del语句删除名称,而不是对象;del命令可能导致对象被当作垃圾回收


# 没有指向对象的引用时,监控对象生命结束时的情形
def bye():  # 这个函数一定不能是要销毁的对象的绑定方法,否则会有一个指向对象的引用
    print('Gone with the wind....')


s1 = {1, 2, 3}
s2 = s1  # s1和s2是别名,指向同一个集合
ender = weakref.finalize(s1, bye)  # 在s1引用的对象上注册bye回调
print(ender.alive)
del s1
print(ender.alive)
print(s2)
s2 = 'spam'
print(ender.alive)


# --------------------------------------------------
# 8.6 弱引用
print('*' * 50)
# 弱引用不会增加对象的引用数量,引用的目标对象称为所指对象(referent)
# 因此弱引用不会妨碍所指对象被当作垃圾回收
# 弱引用在缓存应用中很有用,因为我们不想仅因为被缓存引用着而始终保存缓存对象

# 弱引用是可调用的对象,返回的是被引用的对象;如果所指对象不存在了,返回None
a_set = {0, 1}
wref = weakref.ref(a_set)  # 创建弱引用对象wref
print(wref)  # 调用wref()返回的是被引的对象
print(wref())
a_set = {2, 3, 4}
print(wref())  # 这里已经没有对象引用{1, 2}


# 1).WeakValueDictionary简介
# WeakValueDictionary类实现的是一种可变映射,里面的值是对象的弱引用
# 被引用的对象在程序中的其他地方被当作垃圾回收后,对应的键会自动从WeakValueDictionary中删除
class Cheese:
    def __init__(self, kind):
        self.kind = kind

    def __repr__(self):
        return f'Cheese{self.kind}'


stock = weakref.WeakValueDictionary()  # stock是WeakValueDictionary的实例
catalog = [Cheese('Red Leicester'), Cheese('Tilsit'),
           Cheese('Brie'), Cheese('Parmesan')]
for cheese in catalog:
    stock[cheese.kind] = cheese  # stock把奶酪的名称映射到catlog中Cheese实例的弱引用上
print(sorted(stock.keys()))
del catalog
# 删除catalog后stock的多数奶酪都不见了,这是WeakValueDictionary的预期行为
print(sorted(stock.keys()))
del cheese
print(sorted(stock.keys()))


# 2).弱引用的局限
# 不是每个Python对象都可以作为弱引用的目标(或称所指对象),基本的list和dict实例不能作为所指对象
class MyList(list):
    """list的子类,实例可以作为弱引用的目标"""


a_list = MyList(range(10))
wref_to_a_list = weakref.ref(a_list)


# --------------------------------------------------
# 8.7 Python对不可变类型施加的把戏
print('*' * 50)
# 对元组t来说,t[:]不创建副本,而是返回同一个对象的引用
# 此外tuple(t)获得的也是同一个元组的引用
# str、bytes和frozenset实例也有这种行为
# frozenset实例不是序列,因此不能使用 fs[:](fs是一个frozenset实例)
# 但是,fs.copy()具有相同的效果:它会欺骗你,返回同一个对象的引用,而不是创建一个副本
# 共享字符串字面量是一种优化措施,称为驻留(interning)


# --------------------------------------------------
# 8.8 本章小小结
print('*' * 50)
# 每个Python对象都有标识,类型和值,只有对象的值会不时变化
# 变量保存的是引用,这一点对Python编程有很多实际的影响
# · 简单的复制不创建副本
# · 对+=或*=所作的增量赋值而言,若左边的变量绑定的是不可变对象,会创建新对象,若可变则就地更改
# · 为现有的变量赋予新值,不会修改之前绑定的变量;重新绑定:现在变量绑定了其他的对象
# · 若变量是对象的最后一个引用,变量删除后对象会被当做垃圾回收
# · 函数的参数以别名的形式传递,意味着哈桑农户可能会修改通过参数传入的可变对象
# · 使用可变类型作为函数参数的默认值很危险先,因为若就地修改了参数,函数默认值也就变看,这会影响之后默认值的使用
