__author__ = 'fmy'

import inspect
from abc import ABC, abstractmethod
import collections
import promotions_else

"使用一等函数实现设计模式"
# --------------------------------------------------
# 6.1 案例分析:重构'策略'模式
print('*' * 50)
# 1). 经典的'策略'模式
# '策略'模式:定义一系列算法,把它们一一封装,并且使它们可以相互替代.本模式使得算法可以独立于使用它的客户而变化

# 电商领域的某个功能,使用'策略'模式:根据客户的属性或订单中的商品计算折扣
# ·有1000或以上积分的顾客，每个订单享5%折扣
# ·同一订单中,单个商品的数量达到20个或以上,享10%折扣
# ·订单中的不同商品达到10个或以上,享7%折扣
# 简单起见,我们假定一个订单只能享用一个折扣

# 根据UML类图,涉及到下列内容
# 上下文:把一些计算委托给实现不同算法的可互换组件,它提供服务
# 在这个电商示例中,上下文是Order,它会根据不同的算法计算促销折扣

# 策略:实现不同算法的组件共同的接口
# 在这个示例中,名为Promotion的抽象类扮演这个角色

# 具体策略:“策略”的具体子类。
# FidelityPromo、BulkPromo和LargeOrderPromo是这里实现的三个具体策略

# 实现Order类,支持插入式折扣策略
Customer = collections.namedtuple('Customer', 'name fidelity')


class LineItem:
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price

    def total(self):
        return self.price * self.quantity


class Order:  # 上下文
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion

    def total(self):
        if not hasattr(self, '__total'):
            self.__total = sum(item.total() for item in self.cart)
        return self.__total

    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion.discount(self)
        return self.total() - discount

    def __repr__(self):
        fmt = '<Order total:{:.2f} due:{:.2f}>'  # (:)是为了输出保留两位小数
        return fmt.format(self.total(), self.due())


class Promotion(ABC):  # 策略:抽象基类
    @abstractmethod
    def discount(self, order):
        """返回折扣金额(正值)"""


class FidelityPromotion(Promotion):  # 第一种具体策略
    """为积分超过1000的顾客提供5%折扣"""
    def discount(self, order):
        return order.total() * 0.05 if order.customer.fidelity >= 1000 else 0


class BulkItemPromotion(Promotion):  # 第二种具体策略
    """单个商品为20个及以上时提供10%折扣"""
    def discount(self, order):
        discount = 0
        for item in order.cart:
            if item.quantity >= 20:
                discount += item.total() * 0.1
        return discount


class LargeOrderPromotion(Promotion):  # 第三种具体策略
    """订单中的不同商品达到10个及以上时提供7%折扣"""
    def discount(self, order):
        distinct_items = {item.product for item in order.cart}
        if len(distinct_items) >= 10:
            return order.total() * 0.07
        return 0


# 在上面例子中,讲Promotion定义为抽象基类(abstract base class, ABC)
# 这么做视为了使用@abstractmethod,从而明确表明使用的模式

# 使用不同促销折扣的Order类示例
joe = Customer('John Doe', 0)
ann = Customer('Ann Smith', 1100)  # 两个顾客,Joe的积分为0,Ann的积分为1100
cart = [LineItem('banana', 4, 0.5),
        LineItem('apple', 10, 1.5),
        LineItem('watermelon', 5, 5.0)]  # 有三个商品的购物车
print(Order(joe, cart, FidelityPromotion()))  # FidelityPromotion没给Joe提供折扣
print(Order(ann, cart, FidelityPromotion()))  # Ann得到5%的折扣
banana_cart = [LineItem('banana', 30, 0.5),
               LineItem('apple', 10, 1.5)]
print(Order(joe, banana_cart, BulkItemPromotion()))  # BulkItemPromotion给Joe买的香蕉提供10%折扣
long_order = [LineItem(str(item_code), 1, 1.0)
              for item_code in range(10)]  # long_order中有10个不同的商品
print(Order(joe, long_order, LargeOrderPromotion()))  # LargeOrderPromotion为Joe的整个订单提供7%的折扣
print(Order(joe, cart, LargeOrderPromotion()))

# 2). 使用函数实现'策略'模式
# Order类和使用函数实现的折扣策略
Customer = collections.namedtuple('Customer', 'name fidelity')


class LineItem:
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price

    def total(self):
        return self.price * self.quantity


class Order:  # 上下文
    def __init__(self, customer, cart, promotion=None):
        self.customer = customer
        self.cart = list(cart)
        self.promotion = promotion

    def total(self):
        if not hasattr(self, '__total'):
            self.__total = sum(item.total() for item in self.cart)
        return self.__total

    def due(self):
        if self.promotion is None:
            discount = 0
        else:
            discount = self.promotion(self)  # 计算时只需调用self.promotion函数
        return self.total() - discount

    def __repr__(self):
        fmt = '<Order total:{:.2f} due:{:.2f}>'  # (:)是为了输出保留两位小数
        return fmt.format(self.total(), self.due())


# 没有抽象类,各个策略都是函数
def fidelity_promotion(order):  # 第一种具体策略
    """为积分超过1000的顾客提供5%折扣"""
    return order.total() * 0.05 if order.customer.fidelity >= 1000 else 0


def bulk_item_promotion(order):  # 第二种具体策略
    """单个商品为20个及以上时提供10%折扣"""
    discount = 0
    for item in order.cart:
        if item.quantity >= 20:
            discount += item.total() * 0.1
    return discount


def large_order_promotion(order):  # 第三种具体策略
    """订单中的不同商品达到10个及以上时提供7%折扣"""
    distinct_items = {item.product for item in order.cart}
    if len(distinct_items) >= 10:
        return order.total() * 0.07
    return 0


# 在上面例子中,讲Promotion定义为抽象基类(abstract base class, ABC)
# 这么做视为了使用@abstractmethod,从而明确表明使用的模式

# 使用不同促销折扣的Order类示例
print('-'*10)
joe = Customer('John Doe', 0)
ann = Customer('Ann Smith', 1100)
cart = [LineItem('banana', 4, 0.5),
        LineItem('apple', 10, 1.5),
        LineItem('watermelon', 5, 5.0)]
print(Order(joe, cart, fidelity_promotion))  # 折扣策略应用到Order实例,只需把促销参数作为参数传入
print(Order(ann, cart, fidelity_promotion))
banana_cart = [LineItem('banana', 30, 0.5),
               LineItem('apple', 10, 1.5)]
print(Order(joe, banana_cart, bulk_item_promotion))
long_order = [LineItem(str(item_code), 1, 1.0)
              for item_code in range(10)]
print(Order(joe, long_order, large_order_promotion))
print(Order(joe, cart, large_order_promotion))

# 3). 选择最佳策略:简单的方式
# best_promotion函数计算所以折扣,并返回额度最大的
# promotions列出所以策略,promotions是函数列表,习惯函数为一等对象后自然而然构建这种数据结构存储函数
promotions = [fidelity_promotion, bulk_item_promotion, large_order_promotion]


def best_promotion(order):  # 以其他函数一样,best_promotion函数的参数是一个Order实例
    """选择可用的最佳折扣"""
    # 使用生成器表达式把order传给promotions列表中的各个函数,返回折扣最大的那个函数
    return max(promotion(order) for promotion in promotions)


print('-'*10)
print(Order(joe, long_order, best_promotion))
print(Order(joe, banana_cart, best_promotion))
print(Order(ann, cart, best_promotion))
# best_promotion函数有一点不足在于新加促销函数时,不加修改函数将不起作用

# 4). 找出模块中的全部策略
# 在Python中,模块也是一等对象,而且标准库提供了几个处理模块的函数
# globals(),返回一个字典,表示当前的全局符号表,这个符号时中针对当前模块
# 对函数或方法来说,是指定义它们的模块,而不是调用它们的模块

# 内省模块的全局命名空间,构建promotions列表
promotions_1 = [globals()[name] for name in globals()   # 返回globals()字典中的各个name
                if name.endswith('_promotion')   # 只选择以'_promotion'结尾的名称
                and name != 'best_promotion']  # 过滤掉'best_promotion'自身


def best_promotion_1(order):
    """选择可用的最佳折扣"""
    return max(promotion(order) for promotion in promotions_1)
# 收集所有可用促销的另一种方法是,在一个单独的模块中保存所有策略函数,把best_promotion排除在外


print('-' * 10)
# globals()['key']() 的含义是:从全局环境中找到名为key的函数/类等callable的对象并执行
print(Order(joe, long_order, globals()['bulk_item_promotion']))

# 内省单独的promotions模块,构建promotions列表
promotions_2 = [func for name, func in
                inspect.getmembers(promotions_else, inspect.isfunction)]
print(promotions_2)
# inspect.getmembers函数用于获取对象(这里是promotions_else模块)的属性
# 第二个参数是可选的判断条件(一个布尔值函数),我们这里使用的是inspect.isfunction


def best_promotion_2(order):
    """选择可用的最佳折扣"""
    return max(promotion(order) for promotion in promotions_2)


# --------------------------------------------------
# 6.2 '命令'模式
print('*' * 50)
# '命令'模式的目的是解耦调用操作的对象(调用者)和提供实现的对象(接收者)


# MacroCommand的各个实例
class Macrocommand:
    """一个执行一组命令的命令"""
    def __init__(self, commands):
        self.commands = list(commands)

    def __call__(self):
        for command in self.commands:
            command()
