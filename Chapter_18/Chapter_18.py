__author__ = 'fmy'

import spinner_thread


"使用asyncio包处理并发"
# 本章讨论一下话题:
# 1).对比一个简单的多线程程序和对应的asyncio版,说明多线程和异步任务之间的关系
# 2).asyncio.Future类和concurrent.futures.Future类之间的区别
# 3).17章中下载国旗示例的异步版
# 4).在异步编程中,与回调相比,协程显著提升性能的方式
# 5).如何把阻塞的操作交给线程池处理,从而避免阻塞事件循环
# 6).使用asyncio编写服务器,重新审视Web应用对高并发的处理方式
# 7).为什么asyncio已经准备好对Python生态系统产生重大影响


# --------------------------------------------------
# 18.1 线程与协程对比
print('*' * 50)
# spinner_thread:通过线程以动画形式显示文本式旋转指针
spinner_thread.main()  # 在终端可以看到效果

# spinner_asyncio:通过协程以动画形式显示文本式旋转指针
# 这里没给出

"""
如果使用线程做过重要的编程,你就知道写出程序有多么困难,因为调度程序任何时候都能中断线程
必须记住保留锁,去保护程序中的重要部分,防止多步操作在执行的过程中中断,防止数据处于无效状态

而协程默认会做好全方位保护以防止中断.我们必须显式产出才能让程序的余下部分运行
对协程来说无需保留锁,在多个线程之间同步操作,协程自身就会同步,因为在任意时刻只有一个协程运行
想交出控制权时,可以使用yield或yield from把控制权交还调度程序,这就是能够安全地取消协程的原因
按照定义,协程只能在暂停的yield处取消,因此可以处理CancelledError异常,执行清理操作
"""

# 1).asyncio.Future:故意不阻塞
"""
期物只是调度执行某物的结果
在asyncio包中,BaseEventLoop.create_task(...)方法接收一个协程,排定它的运行时间
然后返回一个asyncio.Task实例——也是asyncio.Future类的实例,因为Task是Future的子类,用于包装协程
这与调用Executor.submit(...)方法创建concurrent.futures.Future实例是一个道理

与concurrent.futures.Future类似,asyncio.Future类也提供了.done()、.add_done_callback(...)和.result()等方法
asyncio.Future类的.result()方法没有参数，因此不能指定超时时间
此外，如果调用.result()方法时期物还没运行完毕，那么.result()方法不会阻塞去等待结果，而是抛出asyncio.InvalidStateError异常
然而获取asyncio.Future对象的结果通常使用yield from
使用yield from处理期物,等待期物运行完毕这一步无需我们关心,而且不会阻塞事件循环,因为在asyncio包中,yield from的作用是把控制权还给事件循环

注意,使用yield from处理期物与使用add_done_callback方法处理协程的作用一样
延迟的操作结束后,事件循环不会触发回调对象,而是设置期物的返回值;而yield from表达式则在暂停的协程中生成返回值,恢复执行协程
总之,因为asyncio.Future类的目的是与yield from一起使用,所以通常不需要使用以下方法

• 无需调用my_future.add_done_callback(...),因为可以直接把想在期物运行结束后执行的操作放在协程中yield from my_future表达式的后面
  这是协程的一大优势:协程是可以暂停和恢复的函数
• 无需调用my_future.result(),因为yield from从期物中产出的值就是结果(如result = yield from my_future)

当然有时也需要使用.done() .add_done_callback(...)和.result()方法
但一般情况下asyncio.Future对象由yield from驱动,而不是靠调用这些方法驱动
"""
# 2).从期物、任务和协程中产出

