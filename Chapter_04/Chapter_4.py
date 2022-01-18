__author__ = 'fmy'

import array
import os
import re
import string
import struct
import chardet
import urllib.request
import sys
import locale
import pyuca
import unicodedata

"文本和字节序列"

# 本章节讨论一下话题
# • 字符、码位和字节表述
# • bytes、bytearray 和 memoryview 等二进制序列的独特特性
# • 全部 Unicode 和陈旧字符集的编解码器
# • 避免和处理编码错误
# • 处理文本文件的最佳实践
# • 默认编码的陷阱和标准 I/O 的问题
# • 规范化 Unicode 文本，进行安全的比较
# • 规范化、大小写折叠和暴力移除音调符号的实用函数
# • 使用 locale 模块和 PyUCA 库正确地排序 Unicode 文本
# • Unicode 数据库中的字符元数据
# • 能处理字符串和字节序列的双模式 API


# --------------------------------------------------
# 4.1 字节问题
# 字符的标识，即码位；字符的具体表述取决于所用的编码，即在码位和字节序列间转换时使用的算法
# 编码：码位转换成字节序列；解码：字节序列转换为码位
# Unicode包含1,114,112个码位，范围是0到10FFFF(16进制)

# 编码和码位
s = 'café'
print(len(s))  # 4个Unicode字符
b = s.encode('utf-8')  # 使用UTF-8把str对象编码位bytes对象
print(b)
print(len(b))  # 字节序列b有五个字节（UTF-8中，é的码位编码成两个字节）
b = b.decode('utf-8')
print(b)  # 使用UTF-8把bytes对象解码位str对象
print(len(b))
# 帮助记忆.decode()和.encode(),字节序列想成晦涩难懂的，Unicode想成'人类可读',
# 将不懂的转换成可理解的是解码，将可理解的转换成不可理解的就是编码


# --------------------------------------------------
# 4.2 字节概要
print('*' * 50)
# 包含5个字节的bytes和bytearray对象
cafe = bytes('café', encoding='utf-8')  # bytes对象可以从str对象使用给定的编码构建
print(cafe)
print(cafe[0])  # 各个元素是range(256)内的整数
print(cafe[:1])  # bytes对象的切片还是bytes对象,即使是一个字节的切片
print(cafe[0] == cafe[:1])
# cafe[0]获取的是一个整数,而cafe[:1]返回的是一个长度为 1 的bytes对象,这一点应该不会让人意外.
# s[0] == s[:1]只对str这个序列类型成,str类型的这个行为十分罕见.
# 对其他各个序列类型来说,s[i]返回一个元素,而 s[i:i+1] 返回一个相同类型的序列,里面是 s[i] 元素.
cafe_arr = bytearray(cafe)
print(cafe_arr)  # bytearray对象没有字面量句法，而是以bytearray()和子序列字面量参数的形式显示
print(cafe_arr[-1:])  # bytearray对象的切片还是bytearray对象

# 二进制序列其实是整数序,其字面量表示法表示其中有ASCII文本，各个字节的值涉及下列三种显示方式：
# (1).可打印的ASCII范围内的字节(空格至~),使用ASCII本身
# (2).使用转义序列:制表符(\t)、换行符(\n)、回车符(\r)和\(\\)
# (3).其他字节的值,使用十六进制的转义序列(eg.\x00是空格)

# 除了格式化方法(format和format_map),和几个处理Unicode数据的方法(eg.casefold, isdecimal, isidentified,
# isnumeric, isprintable 和 encode)外,str类型的其他方法都可以用于处理bytes和bytearray类型
# 若正则表达式编译自二进制序列而不是字符串,re模块中的正则表达式函数也能处理二进制序列
# 二进制的fromhex方法,str没有,作用是解析十六进制数字构建二进制序列
eg_fromhex = bytes.fromhex('31 4B CE A9')
print(eg_fromhex)
# 构建bytes和bytearray实例还可以调用各自的构建方法，传入下述参数:
# (1).一个str对象和一个encoding关键字参数
# (2).一个可迭代对象,提供0~255之间的数值
# (3).一个整数,使用空字节创建对应长度的二进制序列(Outdated,已删除)
# (4).一个实现了缓冲协议的对象(eg.bytes,bytearray,memoryview,array.array)
# 使用数组中的原始数据初始化bytes对象
numbers = array.array('h', [-2, -1, 0, 1, 2])  # 指定类型代码h,创建一个短整数(16位)数组
octets = bytes(numbers)  # octets保存组成numbers的字节序列的副本
print(octets)  # 打印5个短整数的10个字节,10*8=80位
# 使用缓冲类对象创建bytes或bytearray对象时，始终复制源对象中的字节序列
# memoryview对象允许在二进制数据结构之间共享内存
# 想从二进制序列中提取结构化信息，struct模块是重要的工具

# 结构体和内存试图
# struct模块提供了一些函数,将打包的字节序列转换成不同类型字段组成的元组,同时还有一些函数
# 用于执行反向转换,将元组转换成打包的字节序列.struct模块能处理bytes,bytearray和memoryview对象
# 使用memoryview和struct查看一个GIF图像的首部
fmt = '<3s3sHH'  # 结构体的格式:<是小字节序。3s3s是两个3字节序列,HH是两个16位二进制整数
with open('example.gif', 'rb') as fp:
    img = memoryview(fp.read())  # 使用内存中的文件内容创建一个memoryview对象
header = img[:10]  # 使用切片再创建一个memoryview对象，这里不会复制字节序列
print(bytes(header))  # 转换成字节序列，然后打印
header_unpack = struct.unpack(fmt, header)
print(header_unpack)  # 拆包memoryview对象,得到一个元组,包含类型、版本、宽度和高度
del header  # 删除引用,释放memoryview实例占用的内存
del img


# --------------------------------------------------
# 4.3 基本的编解码器
print('*' * 50)
# Python自带超过100中编解码器,用于再文本和字节之间相互转换,每个编解码器都有一个名称
# 如'utf-8','utf8','U8',这些名字都可以传给open(),str.encode(),bytes.decode()等函数
# 使用3个编解码器编码字符串‘El Niño’,得到的字节序列差异很大
for codec in ['latin-1', 'utf-8', 'utf-16']:
    print(codec, 'El Niño'.encode(codec), sep='\t\t')
# 一些典型编码介绍
# latin1(即iso8859-1)-->其他编码的基础,如cp1252和Unicode
# cp1252-->Microsoft指定的latin超集,添加了有用的符号，如€,有些Windows应用把它称为'ANSI',但它并不时'ANSI'标准
# cp437-->IBM PC最初的字符集,包含狂徒符号
# gb2312-->用于编码简体中文的陈旧标准;是亚洲语言中使用最广泛的多字节编码
# utf-8-->目前Web中最常见的8位编码,于ASCII兼容，纯ASCII文本是有效的UTF-8文本
# utf-16le-->UTF-16的16位编码方案的一种形式,所有UTF-16支持通过转义序列(代理对,surrogate pair)表示超过U+FFFF的码位


# --------------------------------------------------
# 4.4 了解编解码问题
print('*' * 50)
# 1).处理UnicodeEncodeError
# 多数非UTF编解码器只能处理Unicode字符的一小部分子集,文本转字节序列时，目标编码中没有定义某个字符，
# 就会抛出UnicodeEncodeError错误,除非把errors参数传给编码方法或函数,对错误进行特殊处理
# 编码成字节序列:成功和错误之处
city = 'São Paulo'
city_utf8 = city.encode('utf-8')  # utf-? 编码能处理任何字符
city_utf16 = city.encode('utf-16')
city_iso8859_1 = city.encode('iso8859-1')  # iso8859-1 编码能处理
# city_cp437 = city.encode('cp437')        # cp437 无法编码’ã‘
city_cp437_ignore = city.encode('cp437', errors='ignore')  # 跳过无法编码的字符
city_cp437_replace = city.encode('cp437', errors='replace')  # 把无法编码的换成'?'
city_cp437_other = city.encode('cp437', errors='xmlcharrefreplace')  # 把无法编码的换成XML实体
print(city)
print(city_utf8)
print(city_utf16)
print(city_iso8859_1)
# print(city_cp437)
print(city_cp437_ignore)
print(city_cp437_replace)
print(city_cp437_other)

# 2).处理UnicodeDecodeError
# 不是每一个字节都包含有效的ASCII,也不是每一个字节序列都是有效的UTF-8或UTF-16.
# 因此把二进制序列转换成文本时，遇到无法转化的字节序列会抛出UnicodeDecodeError
# 陈旧的8位编码，能解码任何字节序列而不报错,解码过程悄无声息，但得到的是无用输出
# 乱码字符称为鬼符(gremlin)或(mojibake)
# 把字节序列解码成字符串:成功和错误处理
octets = b'Montr\xe9al'  # '\xe'是latin1编码的'é'
print(octets.decode('cp1252'))  # cp1252 是 latin1 的超集
print(octets.decode('iso8859-7'))  # 用于编码希腊文
print(octets.decode('koi8-r'))  # 用于编码俄文
# print(octets.decode('utf-8'))     # utf-8 编解码器检测到不是有效的UTF-8字符，抛出错误
print(octets.decode('utf-8', errors='replace'))  # 采用replace错误处理方式

# 3).使用与其之外的编码加载模块是抛出的SyntaxError
# Python3 默认使用UTF-8编码,若加载的.py模块中包含UTF-8之外的数据而没有申明编码，会抛出SyntaxError
# GNU/Linux 和 OS X 系统大都使用UTF-8,因此打开再Windows系统中使用的cp1252编码的.py文件时可能发生这种状况
# 为修正这个错误,可以再文件顶部加一个神奇的coding注释：
# coding:cp1252

# 4).如何找出字节序列的编码
# 如果b'\x00'经常出现,那么可能是16位或32位编码,而不是8位编码
# 如果字节序列b'\x20\x00'经常出现,那么可能是UTF-16LE编码
# 统一字符编码侦测包 chardet 就是这样工作的,他能识别30种编码
web_read = urllib.request.urlopen('https://www.youdao.com').read()
print(chardet.detect(web_read))

# 5).BOM:有用的鬼符
u16 = 'El Niño'.encode('utf_16')
print(u16)
# 输出中b'\xff\xfe',是字节序标记(byte-order mark)(BOM),知名编码时使用Intel CPU 的小字节序
# 再小字节序列设备中，各个码位的最低有效字节在前面:字母'E'的码位是U+0045(十进制:69)
print(list(u16))  # 在字节偏移中'E'的编码为69和0;大字节序CPU中,编码顺序相反,'E'的编码为0和69
# 为避免混淆,UTF-16编码在要编码的文本前面加上特殊的不可见字符ZERO WIDTH NO-BREAK SPACE (U+FFFE)
# 在小字节序系统中,这个字符编码为b'\xff\xfe'
# UTF-16有两个变种:UTF-16LE,显式指明使用小字节序;UTF-16BE,显式指明使用大字节序
# 使用这两个变种,不会生成BOM
u16le = 'El Niño'.encode('utf-16le')
u16be = 'El Niño'.encode('utf-16be')
print(f"{list(u16le)}\n{list(u16be)}")
print("%s\n%s" % (list(u16le), list(u16be)))


# --------------------------------------------------
# 4.5 处理文本文件
print('*' * 50)
# 对输入:尽早把输入的字节序列解码为字符串
# 对输出:尽晚把输出的字符串编码为字节序列
open('cafe.txt', 'w', encoding='utf8').write('café')
print(open('cafe.txt').read())  # 写入时指定UTF-8编码,读取文件未指定编码
# 因此多台设备或多种场合下运行的代码,一定不能依赖默认编码
with open('cafe.txt', 'w', encoding='utf8') as fp:
    print(fp)  # 默认情况下,open函数采用文本模式,返回一个TextIOWrapper对象
    print(fp.write('café'))  # 在TextINWrapper对象上write()方法返回写入的Unicode字符数
print(os.stat('cafe.txt').st_size)  # os.stat报告文件中有5个字节
with open('cafe.txt') as fp:  # 打开文本文件时没有显式指定编码,采用默认编码cp936
    print(fp)
    print(fp.read())
with open('cafe.txt', encoding='utf-8') as fp:
    print(fp)
    print(fp.read())
with open('cafe.txt', 'rb') as fp:  # 以二进制模式读取文件
    print(fp)  # 返回BufferedReader对象
    print(fp.read())

# 探索编码默认值
expressions = """
locale.getpreferredencoding()
type(my_file)
my_file.encoding
sys.stdout.isatty()
sys.stdout.encoding
sys.stdin.isatty()
sys.stdin.encoding
sys.stderr.isatty()
sys.stderr.encoding
sys.getdefaultencoding()
sys.getfilesystemencoding()
"""
my_file = open('dummy', 'w')
for expression in expressions.split():
    value = eval(expression)
    print(expression.rjust(30), '-->', repr(value))


# --------------------------------------------------
# 4.6 为了正确比较而规范化Unicode字符串
print('*'*50)
# 因为Unicode有组合字符,因此字符串比较起来很复杂
print('*' * 50)
s1 = 'café'
s2 = 'cafe\u0301'  # \u0301 是 COMBINING ACUTE ACCENT 加在e后面得到'é'
print(s1, s2)  # Unicode标准中,é和'e\u0301'这样的序列称为标准等价物
print(len(s1), len(s2))  # Python看到是不同的码位序列,因此两者长度不等
print(s1 == s2)  # Python看到是不同的码位序列,因此判断两者不相等
# 该问题的解决方案是使用unicode.normalize函数提供的Unicode规范化,该函数第一个参数是四个字符串的一个:'NFC','NFD','NFKC','NFKD'
# NFC(Normalization Form C) 使用最少的码位构成等价的字符串
# NFD把组合字符分解成基字符和单独的组合字符
s1 = 'café'  # 把e和重音字符组合在一起
s2 = 'cafe\u0301'  # 分解成e和重音符
print(len(unicodedata.normalize('NFC', s1)), len(unicodedata.normalize('NFC', s2)))
print(len(unicodedata.normalize('NFD', s1)), len(unicodedata.normalize('NFD', s2)))
print(len(unicodedata.normalize('NFC', s1)) == len(unicodedata.normalize('NFC', s2)))
print(len(unicodedata.normalize('NFD', s1)) == len(unicodedata.normalize('NFD', s2)))
# 西方键盘通常能输出组合字符,因此用户输入的文本默认是NFC形式,为安全起见,保存前最好使用normalize('NFC', user_text)洗清字符串
# 使用NFC时,有些单字符会规范成另一个单子符.如Ω会被规范为希腊字符大写的欧米加,视觉上一样,但并不相等
ohm = '\u2126'
print(unicodedata.name(ohm))
ohm_c = unicodedata.normalize('NFC', ohm)
print(unicodedata.name(ohm_c))
print(ohm == ohm_c)
print(unicodedata.normalize('NFC', ohm) == unicodedata.normalize('NFC', ohm_c))
# NFKC的具体应用,使用NFKC和NFKD规范化形式时要小心,因为只能在特殊情况中使用,例如搜索和索引,而不能用于永久存储
half = '½'
print(unicodedata.normalize('NFKC', half))
four_squared = '4²'
print(unicodedata.normalize('NFKC', four_squared))
micro = 'µ'
print(unicodedata.normalize('NFKC', micro))
print(micro, unicodedata.normalize('NFKC', micro))
print(ord(micro), ord(unicodedata.normalize('NFKC', micro)))
print(list((unicodedata.name(micro),
            unicodedata.name(unicodedata.normalize('NFKC', micro)))))

# 1).大小写折叠
# 大小写折叠-->把文本变成小写,再做其他转换,该功能由str.casefold()方法实现
# 对于只包含latin1字符的字符串,casefold()得到的结果与lower()得到的一致,除一下两个例外
micro = 'µ'
print(unicodedata.name(micro))
micro_cf = micro.casefold()
print(unicodedata.name(micro_cf))
eszett = 'ß'
print(unicodedata.name(eszett))
eszett_cf = eszett.casefold()
print(eszett_cf)


# 2).规范化文本匹配实用函数
def nfc_equal(str1, str2):
    return unicodedata.normalize('NFC', str1) == unicodedata.normalize('NFC', str2)


def fold_equal(str1, str2):
    return unicodedata.normalize('NFC', str1).casefold() == \
           unicodedata.normalize('NFC', str2).casefold()


s1 = 'café'
s2 = 'cafe\u0301'
s3 = 'Straße'
s4 = 'strasse'
print(nfc_equal(s1, s2), fold_equal(s1, s2))
print(nfc_equal('A', 'a'), fold_equal('A', 'a'))
print(nfc_equal(s3, s4), fold_equal(s3, s4))
print(unicodedata.normalize('NFC', 'ß'), unicodedata.normalize('NFC', 'ss'))
print(unicodedata.normalize('NFC', 'ß').casefold(),
      unicodedata.normalize('NFC', 'ss').casefold())


# 3).极端"规范化":去掉变音符号


# 去掉全部组合记号的函数
def shave_marks(txt):
    norm_txt = unicodedata.normalize('NFD', txt)  # 把所有字符分解成基字符和组合记号
    shaved = ''.join(c for c in norm_txt
                     if not unicodedata.combining(c))  # 过滤掉组合记号
    return unicodedata.normalize('NFC', shaved)  # 重组所有字符


order = '“Herr Voß: • ½ cup of Œtker™ caffè latte • bowl of açaí.”'
Greek = 'Zέφupoς, Zéfiro'
print(shave_marks(order))  # 只替换了'è','ç','í'
print(shave_marks(Greek))  # 只替换了'έ','é'


# 删除拉丁字母中组合记号的函数
def shave_marks_latin(txt):
    norm_txt = unicodedata.normalize('NFD', txt)  # 把所有字符分解成基字符和组合记号
    latin_base = False
    keepers = []
    for c in norm_txt:
        if unicodedata.combining(c) and latin_base:  # 基符号为拉丁字母时,跳过组合记号
            continue
        keepers.append(c)  # 否则,保存当前字符
        if not unicodedata.combining(c):  # 检测新的基字符,判断不是拉丁字母
            latin_base = c in string.ascii_letters
    shaved = ''.join(keepers)
    return unicodedata.normalize('NFC', shaved)  # 重组字符


order = '“Herr Voß: • ½ cup of Œtker™ caffè latte • bowl of açaí.”'
Greek = 'Zέφupoς, Zéfiro'
print(shave_marks_latin(order))  # 只替换了'è','ç','í'
print(shave_marks_latin(Greek))  # 只替换了'έ','é'

# 把一些西文印刷字符转换成ASCII字符
single_map = str.maketrans(""",ƒ,†ˆ‹‘’“”•––˜›""",
                           """'f'*^<''""---~>""")    # 构建字符替换字符的映射表
multi_map = str.maketrans({
    '€': '<euro>',
    '…': '...',
    'Œ': 'OE',
    '™': '(TM)',
    'œ': 'oe',
    '‰': '<per mille>',
    '‡': '**',
})                                       # 构建字符替换字符的映射表
multi_map.update(single_map)             # 合并两个映射表


# dewinze不影响ASCII和latin1文本,只替换Microsoft在cp963为latin1额外添加的字符
def dewinize(txt):
    return txt.translate(multi_map)


def asciize(txt):
    no_marks = shave_marks_latin(dewinize(txt))     # 去掉变音符号
    no_marks = no_marks.replace('ß', 'ss')          # 'ß'转换成'ss'
    return unicodedata.normalize('NFKC', no_marks)  # 使用NFKC规范化形式把字符与之兼容的码位组合卡里


order = '“Herr Voß: • ½ cup of Œtker™ caffè latte • bowl of açaí.”'
print(dewinize(order))
print(asciize(order))


# --------------------------------------------------
# 4.7 Unicode文本排序
print('*'*50)
# Python 比较任何类型的序列时,会一一比较序列里各个元素,对于字符串比较的是码位,但比较非ASCII字符时得到的结果不尽人意
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
print(sorted(fruits))
# Python非ASCII1文本的排序方式使用的是locate.strxfrm函数
# 使用locate.strxlm函数做排序键
print(locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8'))
fruits_sorted = sorted(fruits, key=locale.strxfrm)
print(fruits_sorted)
# 使用locale.strxfrm函数做排序键之前,要调用setlocale(LC_COLLATE, <<your_locale>>),要注意以下几点
# · 区域设置是全局的,不推荐在库中调用setlocale函数,应用或框架应该在进程启动时设定区域设置,并且之后不再改动
# · 操作系统必须支持区域设置
# · 必须知道如何拼写区域名称 Windows是:语言名称,语言变体,去域名,代码页
# · 操作系统的制作者必须正确实现所设的区域

# 使用Unicode排序算法排序
coll = pyuca.Collator()
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
sorted_fruits1 = sorted(fruits, key=coll.sort_key)
print(sorted_fruits1)


# --------------------------------------------------
# 4.8 Unicode数据库
print('*'*50)
# Unicode标准提供了一个完整的数据库,不仅包括码位和字符名称之间的映射,还有各个字符的元数据即字符之间的映射
# Unicode数据库中数值字符的元数据示例
re_digit = re.compile(r'\d')
sample = '1\xbc\xb2\u0969\u136b\u216b\u2466\u2480\u3285'
for char in sample:
    print('U+%04x' % ord(char),
          char.center(6),
          're_dig'.ljust(6) if re_digit.match(char) else '-'.ljust(6),
          'isdig'.ljust(6) if char.isdigit() else '-'.ljust(6),
          'isnum'.ljust(6) if char.isnumeric() else '-'.ljust(6),
          format(unicodedata.numeric(char), '6.2f'),
          unicodedata.name(char),
          sep='\t')
# 正则表达式r'\d'能匹配'1'和梵文数字3,但不能匹配其他形式的数字,re模块对Unicode支持并不充分


# --------------------------------------------------
# 4.9 支持字符串和字节序列的双模式API
print('*'*50)
# 标准库中的一些函数能接受字符串或字节序列为参数,根据类型展现不同的行为,re模块和os模块中有这样的函数
# 1).正则表达式中的字符串和字节序列
# 使用字节序列构建正则表达式,\d和\w只能匹配ASCII字符
# 使用字符串模式,可以匹配ASCII之外的Unicode数字和字母
re_numbers_str = re.compile(r'\d+')
re_words_str = re.compile(r'\w+')
re_numbers_bytes = re.compile(rb'\d+')
re_words_bytes = re.compile(rb'\w+')
text_str = ("Ramanujan saw \u0be7\u0bed\u0be8\u0bef"
            " as 1729 = 1³ + 12³ = 9³ + 10³.")
text_bytes = text_str.encode('utf8')
print('Text', repr(text_str), sep='\n    ')
print('Numbers')
print('  str  :', re_numbers_str.findall(text_str))
print('  bytes:', re_numbers_bytes.findall(text_bytes))
print('Word')
print('  byr  :', re_words_str.findall(text_str))
print('  bytes:', re_words_bytes.findall(text_bytes))
# 2).os函数中的字符串和字节序列
# 把字符串和字节序列参数传给listdir函数得到的结果
print(os.listdir('.'))
print(os.listdir(b'.'))
# 为了便于手动处理字符串和字节序列形式的文件名和路径名,os模块提供了特殊的编码和解码函数
# · fsencode(filename)
# 若filename是str类型,使用sys.getfilesystemencoding()返回的编解码器把filename编码为字符串,否则返回未经修改的filename字符串
# · fsdecode(filename)
# 若filename是bytes类型,使用sys.getfilesystemencoding()返回的编解码器把filename解码为字符串,否则,返回未经修改的filename字符串
# 使用surrogateescape错误处理方式
print(os.listdir('.'))
print(os.listdir(b'.'))
pi_name_bytes = os.listdir(b'.')[2]
pi_name_str = pi_name_bytes.decode('ascii', 'surrogateescape')
pi_name_str.encode('ascii', 'surrogateescape')
print(pi_name_bytes)


# --------------------------------------------------
# 4.10 本章总结
print('*'*50)
# 首先澄清了人们对一个字符等于一个字节的误解
# 在没有元数据的情况下检测编码:理论做不到,实际上Chardet包能够正确处理一些流行的编码

