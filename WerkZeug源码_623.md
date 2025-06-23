# local类

    class Local(object):
        __slots__ = ('__storage__', '__lock__', '__ident_func__')
    
        def __init__(self):
            object.__setattr__(self, '__storage__', {})
            object.__setattr__(self, '__lock__', allocate_lock())
            object.__setattr__(self, '__ident_func__', get_ident)
    
        def __iter__(self):
            return self.__storage__.iteritems()
    
        def __call__(self, proxy):
            """Create a proxy for a name."""
            return LocalProxy(self, proxy)
    
        def __release_local__(self):
            self.__storage__.pop(self.__ident_func__(), None)
    
        def __getattr__(self, name):
            try:
                return self.__storage__[self.__ident_func__()][name]
            except KeyError:
                raise AttributeError(name)
    
        def __setattr__(self, name, value):
            ident = self.__ident_func__()
            self.__lock__.acquire()
            try:
                storage = self.__storage__
                if ident in storage:
                    storage[ident][name] = value
                else:
                    storage[ident] = {name: value}
            finally:
                self.__lock__.release()
    
        def __delattr__(self, name):
            try:
                del self.__storage__[self.__ident_func__()][name]
            except KeyError:
                raise AttributeError(name)

解释：
**`__slots__` 属性**：限制类实例可以拥有三个属性

- `__storage__`：用于存储每个线程的数据的字典,是个嵌套的字典：比如{'线程1号':{}, '线程2号':{},}
                最外面字典 key 是线程或者协程的 identity，value 是另外一个字典，这个内部字典就是用户自定义的 key-value 键值对。
                用户访问实例的属性，就变成了访问内部的字典，外面字典的 key 是自动关联的
- `__lock__`：用于线程安全的锁对象
- `__ident_func__`：获取当前线程标识符的函数


**疑问1** ： `object.__setattr__` 的作用

属性是设置在 **当前实例** 上，而不是父类或类本身

`object.__setattr__` 是 Python 中最底层的属性设置方法，它会：

- **直接修改实例**：将属性存入实例的 `__dict__` 或 `__slots__` 对应的存储中。
- **绕过自定义逻辑**：不会触发实例的 `__setattr__` 或 `__setattribute__` 方法，避免循环调用



def **release_local**(self):   从__storage___字典中移除key等于当前线程号的数据

def **getattr**(self, name):  从__storage___字典中获取key等于当前线程号的值，该值又是字典类型，最后再获取key等于name的数据





def **setattr**(self, name, value):

设置属性前先加锁。如果__storage___字典中已有key等于当前线程号的，比如对应数据为A字典，直接A[name] = value。

如果__storage___字典中没有key等于当前线程号的，在__storage___字典中添加key等于当前线程号的，值为字典{name: value}

最后释放锁



def **delattr**(self, name):  

从__storage___字典中选择key等于当前线程号的数据B，删除B字典中key等于name的数据







# LocalStack类

    class LocalStack(object):
        def __init__(self):
            self._local = Local()
            self._lock = allocate_lock()
    
        def __release_local__(self):
            self._local.__release_local__()
    
        def _get__ident_func__(self):
            return self._local.__ident_func__
    
        def _set__ident_func__(self, value):
            object.__setattr__(self._local, '__ident_func__', value)
    
        __ident_func__ = property(_get__ident_func__, _set__ident_func__)
        del _get__ident_func__, _set__ident_func__
    
        def __call__(self):
            def _lookup():
                rv = self.top
                if rv is None:
                    raise RuntimeError('object unbound')
                return rv
            return LocalProxy(_lookup)
    
        def push(self, obj):
            self._lock.acquire()
            try:
                rv = getattr(self._local, 'stack', None)
                if rv is None:
                    self._local.stack = rv = []
                rv.append(obj)
                return rv
            finally:
                self._lock.release()
    
        def pop(self):
            self._lock.acquire()
            try:
                stack = getattr(self._local, 'stack', None)
                if stack is None:
                    return None
                elif len(stack) == 1:
                    release_local(self._local)
                    return stack[-1]
                else:
                    return stack.pop()
            finally:
                self._lock.release()
    
        @property
        def top(self):
            try:
                return self._local.stack[-1]
            except (AttributeError, IndexError):
                return None

初始化：

1. 实例化Local类

2. 实例化锁对象



def **release_local**(self): 调用Loca实例的release_local()函数



**疑问1**：下面最后两行的作用

    线程标识函数的属性管理
    def _get__ident_func__(self):
        # 获得当前线程号
        return self._local.__ident_func__
    
    def _set__ident_func__(self, value):
        # 设置Local实例的ident_func变量的值为value
        object.__setattr__(self._local, '__ident_func__', value)
    
    __ident_func__ = property(_get__ident_func__, _set__ident_func__)
    del _get__ident_func__, _set__ident_func__
    
    
    通过 property 装饰器封装了 getter 和 setter 方法，并删除了原始方法引用避免混淆：
    getter 方法：_get__ident_func__用于获取线程本地对象的__ident_func__属性
    setter 方法：_set__ident_func__用于设置线程本地对象的标识函数
    
    当外部代码读取instance.__ident_func__时，会自动调用_get__ident_func__方法；
    当外部代码设置instance.__ident_func__ = value时，会自动调用_set__ident_func__方法。
    
    del 的作用： 强制用户只能通过属性（__ident_func__）访问和修改值，而不是直接调用方法



def push(self, obj): 先加锁。在线程专属字典中key等于stack的列表数据，把obj追加到列表数据中。最后释放锁。

**疑问2**：self._local使用了__slots__ = ('__storage__', '__lock__', '__ident_func__')，为什么这里self._local.stack = rv = []还能新增变量stack?

解答：1. `Local` 类通常通过 **自定义属性访问逻辑** 绕过 `__slots__` 的限制。它的核心机制是通过重载 `__getattr__` 和 `__setattr__` 拦截所有属性访问。

2.这个过程**没有违反 `__slots__` 的限制**，因为 `stack` 不是实例属性，而是存储在线程专属字典中的键值对。





def pop(self):先加锁。从线程专属字典中key等于stack获取列表数据，如果列表为空，返回为空；如果列表长队为1，释放当前local实例，返回该元素；否则，返回列表弹出的末尾数据。最后释放锁。



def top(self):返回线程专属字典中key等于stack的列表数据的最后一个元素






