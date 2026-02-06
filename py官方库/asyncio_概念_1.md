


## 异步函数和协程
async def 使它成为一个异步函数（或“协程函数”）。调用它会创建并返回一个 协程 对象。
```
async def loudmouth_penguin(magic_number: int):
    print(
     "I am a super special talking penguin. Far cooler than that printer. "
     f"By the way, my lucky number is: {magic_number}."
    )
```
调用异步函数 loudmouth_penguin 不会执行打印语句 ；相反，它会创建一个协程对象：
```
>>> loudmouth_penguin(magic_number=3)
<coroutine object loudmouth_penguin at 0x104ed2740>
```
“协程函数”和“协程对象”这两个术语经常被统称为协程。这可能会引起混淆注意！ 在本文中，协程特指 协程对象

## 任务
任务 是绑定到事件循环的协程（而非协程函数）
`任务还维护一个回调函数列表，这些回调函数的重要性在稍后讨论 await 时会更加清晰`。推荐使用 asyncio.create_task() 创建任务。

asyncio 会为你自动将任务与事件循环进行关联。 这种自动关联是出于简便的考虑有意设计在 asyncio 中的。
```
coroutine = loudmouth_penguin(magic_number=5)

# 这将创建一个 Task 对象并通过事件循环安排其执行。
task = asyncio.create_task(coroutine)
```

之前，我们手动创建了事件循环并将其设置为永久运行。实际上，推荐（且常见）的做法是使用 asyncio.run()，它负责管理事件循环并确保提供的协程在继续执行之前结束。例如，许多异步程序都遵循以下设置：
```
import asyncio

async def main():
    # 执行各种稀奇古怪、天马行空的异步操作……
    ...

if __name__ == "__main__":
    asyncio.run(main())
    # 直到协程 main() 结束，程序才会到达下面的打印语句。
    print("coroutine main() is done!")
```

## await
await 是一个 Python 关键字，通常以两种不同的方式使用：
- await task
- await coroutine
从关键方面来说，await 的行为取决于所等待对象的类型。

### await task
等待任务完成会将控制权从当前任务或协程移交给事件循环。在交还控制权的过程中，会发生一些重要的事情。我们将使用以下代码示例来说明：
```
async def plant_a_tree():
    dig_the_hole_task = asyncio.create_task(dig_the_hole())
    await dig_the_hole_task

    # 与植树相关的其他指令。
    ...
```
await dig_the_hole_task 这条指令会将一个回调函数（用于恢复 plant_a_tree() 的执行）添加到 dig_the_hole_task 对象的回调函数列表中。随后，这条指令将控制权交还给事件循环。过一段时间后，事件循环会将控制权传递给 dig_the_hole_task，该任务会完成它需要做的工作。`一旦任务结束，它会将它的各种回调函数添加到事件循环中，在这里是恢复 plant_a_tree() 的执行`。

一般来说，当等待的任务完成时 (dig_the_hole_task)，`原先的任务或协程` (plant_a_tree()) 将被添加回事件循环的待办列表以便恢复运行。

这是一个基础但可靠的思维模型。实际操作中，控制权交接会稍微复杂一些，但不会复杂太多。在第 2 部分中，我们将逐步讲解实现这一目标的细节。

### await coroutine
与任务不同，等待协程不会将控制权交给事件循环！ 先将协程包装在任务中，然后再等待该任务，才会将控制权交给事件循环。其行为await coroutine实际上与调用常规的同步 Python 函数相同


## 事件循环回调
一个常见的陷阱是，事件循环不会将任务对象（即asyncio.Task实例）存储在它的队列（或“作业集合”）中。相反，它存储的是可调用对象（或“回调函数”），这些对象通常会调用任务，尽管它们也可以执行其他更通用的操作!

如果你不保留对任务的引用，就不会有任何对该对象的引用，垃圾回收器（即内存清理器）可能会销毁该对象并回收这些字节。如果事件循环稍后尝试调用这个现在已不存在的对象，那就麻烦了！

在下面的简短示例中，一个任务在没有引用的情况下被创建，并且没有立即等待，因此它随时可能被垃圾回收。另一个任务在创建时带有对其的引用（即task = ...），但在main()函数的作用域内也没有等待。如果main()函数在事件循环恰好重新获得控制并调用task之前完成，则作用域将退出，包括任务对象在内的局部变量都有可能被释放。
```
async def main():
    # The task is created, but no reference is made to it.
    asyncio.create_task(coro_fn())
    # A reference is made, but the task is never awaited in the scope of main().
    task = asyncio.create_task(coro_fn())
    ...
```


人们最常在 for 循环中意外触发此错误。在下面的示例中，看起来我们似乎保留了对每个任务的引用，但 for 循环结束后，我们实际上只保留了对最后一个任务的引用。
```
async def main():
    for idx in range(5):
        t = asyncio.create_task(coro_fn())
```

相反，请保留对每个已创建任务的引用：
```
async def main():
    # 使用任务列表
    tasks = []
    for idx in range(5):
        t = asyncio.create_task(coro_fn())
        tasks.append(t)
    
    # Ensure each task finishes before exiting main().
    for task in tasks:
        await task
```

## 总结
到目前为止，我们已经讲了很多内容！让我们回顾一下，看看这些概念是如何协同工作的。

事件循环负责统筹全局。你基本上可以把它想象成一个队列，按照提供的顺序一次运行一个任务。这些任务是对调用/恢复任务的调用。任务基本上是与事件循环绑定的协程，它们还可以存储一个回调列表。而协程就像普通的Python函数，可以在其主体（在await处）暂停和恢复。

还有两个常见的陷阱。`await`协程并不会将控制权交给事件循环。在等待任务对象之前，保持对它们的引用非常重要。