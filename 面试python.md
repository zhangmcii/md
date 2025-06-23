1.**Python中哪些是可变对象，不可变对象？**

可变对象：列表，集合，字典

不可变对象： 元组，整数，字符串，浮点数，布尔值



2.**字典不是线程安全的。**

在多线程环境下，多个线程同时对同一个字典进行读写操作可能会导致数据竞争和数据不一致的问题。

> 扩展：
> 
> 同样不是线程安全的对象有： 列表(list), 字典(dict),  集合(set)
> 
> 线程安全的是： 元祖(tuple)， 字符串(str)， 字节或字符串(bytes)。因为它们都是不可变对象





3.**现在有一个数字和布尔类型，你怎么去区分它们？**

1.使用type()函数

2.直接检查布尔值，比如 y is True



> nizhenshi: 
> 
> 使用isinstance()函数
> 
> x = 5
> 
> y = True
> 
> isinstance(x, (ini,float)
> 
> isinstance(y, bool)



4.**Flask框架的Request对象底层怎么实现的？**

对于 flask app 来说，请求就是一个对象，当需要某些信息的时候，只需要读取该对象的属性或者方法就行了。
Request() # 未实现,借用自 Werkzeug

这个类的定义很简单，它继承了 `werkzeug.wrappers:Request`，然后添加了一些属性，这些属性和 flask 的逻辑有关，比如 view_args、blueprint、json 处理等



总之，Flask的Request对象是通过Werkzeug库实现的，它封装了当前HTTP请求的所有数据，并且提供了许多属性和方法来访问这些数据。



5.**flask怎么区分不同的请求到对应的视图函数？**

flask 的做法是把这些信息作为**类似全局变量的东西**，这些对象和全局变量不同的是——它们必须是动态的，因为在多线程或者多协程的情况下，每个线程或者协程获取的都是自己独特的对象，不会互相干扰。

如何实现这种互不干扰的效果呢？多线程中有个非常类似的概念 [`threading.local`](http://stackoverflow.com/questions/104983/what-is-thread-local-storage-in-python-and-why-do-i-need-it#)。内部的原理就是，这个对象有一个字典，保存了线程 id 对应的数据，读取该对象的时候，它动态地查询当前线程 id 对应的数据。这样就会使多线程或者多协程情况下全局变量的隔离效果。



在并发程序中每个视图函数都会看到属于自己的上下文，而不会出现混乱。



 gunicorn 怎么念？

为了省事：

- 绿色的独角兽

- g-unicorn

- gun-i-corn


