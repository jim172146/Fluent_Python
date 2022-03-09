# explore0.py:把一个JSON数据集转换成一个嵌套着
# FrozenJSON对象、列表和简单类型的FrozenJSON对象

from collections import abc


class FrozenJSON:
    """一个只读接口,使用属性表示法访问JSON类对象"""

    def __init__(self, mapping):
        self.__data = dict(mapping)

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            return FrozenJSON.build(self.__data[name])

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            # 如果obj是映射,那就构建一个FrozenJSON对象
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            # 如果是MutableSequence对象,必然是列表
            # 因此把obj中每个元素递归地传给.build()方法,构建一个列表。
            return [cls.build(item) for item in obj]
        else:
            return obj



