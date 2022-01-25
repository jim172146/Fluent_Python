class LookingGlass:
    def __enter__(self):  # 除了self之外,Python调用__enter__方法时不传入其他参数
        import sys
        self.original_write = sys.stdout.write  # 把sys.stdout.write方法保存在实例属性中
        sys.stdout.write = self.reverse_write  # 为sys.stdout.write打猴子补丁
        return 'YKCOWREBBAJ'  # 返回'JABBERWOCKY'字符串,这样才有内容存入目标变量what

    # 这是用于取代sys.stdout.write的方法,把text参数的内容反转,然后调用原来的实现
    def reverse_write(self, text):
        self.original_write(text[::-1])

    # 如果一切正常,Python调用 __exit__方法时传入的参数是None,None,None
    # 如果抛出了异常,这三个参数是异常数据
    def __exit__(self, exc_type, exc_val, exc_tb):
        import sys  # 重复导入模块不会消耗很多资源,因为 Python会缓存导入的模块
        sys.stdout.write = self.original_write  # 还原成原来的sys.stdout.write方法
        # 如果有异常,而且是ZeroDivisionError类型,打印一个消息
        if exc_type is ZeroDivisionError:
            print('Please DO NOT divide by zero!')
            return True  # 然后返回True,告诉解释器异常已经处理了
# 如果__exit__方法返回None或者True之外的值,with块中的任何异常都会向上冒泡
