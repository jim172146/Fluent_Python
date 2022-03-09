__author__ = 'fmy'

import osconfeed
import explore0
import explore1
import schedule
import schedule2

import shelve

"使用特性验证属性"
# 数据的属性和处理数据的方法统称为属性,方法是可调用的属性


# --------------------------------------------------
# 19.1 使用动态属性转换数据
print('*' * 50)
# osconfeed.py:下载 osconfeed.json
feed = osconfeed.load()
# feed的值是一个字典,里面嵌套着字典和列表,存储着字符串和整数

# osconfeed.py示例
# 列出'Schedule'键中的记录集合
print(sorted(feed['Schedule'].keys()))

# 显示各个集合中的记录数
for key, value in sorted(feed['Schedule'].items()):
    print(f'{len(value):<5} {key}')

# 深入嵌套的字典和列表,获取最后一个演讲者的名字
print(feed['Schedule']['speakers'][-1]['name'])

# 获取那位演讲者的编号
print(feed['Schedule']['speakers'][-1]['serial'])

# 每个事件都有一个'speakers'字段,列出0个或多个演讲者的编号
print(feed['Schedule']['events'][40]['name'])
print(feed['Schedule']['events'][40]['speakers'])

# 1).使用动态属性访问JSON类数据
# explore0.py定义的FrozenJSON类能读取属性,如name,还能调用方法,如.keys()和.items()
raw_feed = osconfeed.load()
feed = explore0.FrozenJSON(raw_feed)

print(len(feed.Schedule.speakers))
print(sorted(feed.Schedule.keys()))
for key, value in sorted(feed.Schedule.items()):
    print(f'{len(value):<5}{key}')
print(feed.Schedule.speakers[-1].name)
talk = feed.Schedule.events[40]
print(type(talk))
print(talk.name)
print(talk.speakers)
# print(talk.flavor)  # 读取不存在的属性会抛出KeyError异常,而不是通常抛出的AttributeError异常

# 2).处理无效属性名
print('-' * 10)
grad = explore0.FrozenJSON({'name': 'Jim Bo', 'class': 1982})
# print(grad.class)  # SyntaxError: invalid syntax
# 无法读取grad.class的值,因为在Python中class是保留字
print(getattr(grad, 'class'))

grad = explore1.FrozenJSON({'name': 'Jim Bo', 'class': 1982})
print(grad.class_)

# 3).使用__new__方法以灵活的方式创建对象
# __init__方法是'初始化方法',真正的构造方法是__new__
# explore2.py

# 4).使用shelve模块调整OSCON数据源的结构
# schedule1.py:访问保存在shelve.Shelf对象里的OSCON日程数据
print('-' * 10)
db = shelve.open(schedule.DB_NAME)
if schedule.CONFERENCE not in db:
    schedule.load_db(db)

speaker = db['speaker.3471']
print(type(speaker))
print(speaker.name, '--', speaker.twitter)
db.close()


# 5).使用特性获取链接的记录
print('-' * 10)
db = shelve.open(schedule2.DB_NAME)
schedule2.DbRecord.set_db(db)
event = schedule2.DbRecord.fetch('event.33950')
