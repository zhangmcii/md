
# 协程的内部工作原理

coroutine.send(arg) 是用于启动或恢复协程的方法。 如果协程已暂停并正在被恢复，则参数 arg 将作为原先暂停它的 yield 语句的返回值被发送。 如果协程是首次被使用（而不是被恢复），则 arg 必须为 None。

```python
class Rock:
    def __await__(self):
        value_sent_in = yield 7
        print(f"Rock.__await__ resuming with value: {value_sent_in}.")
        return value_sent_in

async def main():
    print("Beginning coroutine main().")
    rock = Rock()
    print("Awaiting rock...")
    value_from_rock = await rock
    print(f"Coroutine received value: {value_from_rock} from rock.")
    return 23

coroutine = main()
intermediate_result = coroutine.send(None)
print(f"Coroutine paused and returned intermediate value: {intermediate_result}.")

print(f"Resuming coroutine and sending in value: 42.")
try:
    coroutine.send(42)
except StopIteration as e:
    returned_value = e.value
print(f"Coroutine main() finished and provided value: {returned_value}.")
```

yield 像往常一样暂停执行并将控制权返回给调用者。 在上面的例子中，第 3 行的 yield 被第 11 行的 ... = await rock 调用。 

更宽泛地说，await 会调用给定对象的 __await__() 方法。 await 还会做一件非常特别的事情：它会将接收到的任何 yield 沿着调用链向上传播（或称“传递”）。 在本例中，这将回到第 16 行的 ... = coroutine.send(None)。

协程通过第 21 行的 coroutine.send(42) 调用恢复。协程从第 3 行 yield (或暂停) 的位置继续执行，并执行其主体中的剩余语句。协程完成后，它会引发一个 StopIteration 异常，并将返回值附加在 value 属性中。

该代码片段产生以下输出：
```
Beginning coroutine main().
Awaiting rock...
Coroutine paused and returned intermediate value: 7.
Resuming coroutine and sending in value: 42.
Rock.__await__ resuming with value: 42.
Coroutine received value: 42 from rock.
Coroutine main() finished and provided value: 23.
```


## Future 
Future 是一个用来表示计算状态和结果的对象。

Future 对象有几个重要的属性。 其一是它的状态，可以是“待处理”、“已取消”或“已完成”。 其二是它的结果，当状态转换为已完成时它就会被设定。
