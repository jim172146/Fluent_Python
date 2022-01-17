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