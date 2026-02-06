


1. 控制始于program.py
    * 第 9 行创建事件循环，第 10 行创建main_task并将其添加到事件循环中，第 11 行调用事件循环。
2. 现在控制权掌握在手中。event-loop
    * 事件循环main_task从队列中弹出，然后通过调用来调用它main_task.step()。
3. 现在控制权在main_task.step
    * 我们在第 4 行进入 try 代码块，然后main在第 5 行开始协程。
4. 现在控制权在program.main
    * Tasktriple_task在第 5 行创建，并被添加到事件循环的队列中。第 6 行使用 await triple_task。请记住，该 awaitTask.__await__会调用并处理所有 yield。
5. 现在控制权在triple_task.__await__
    * triple_task由于它刚刚创建，所以还没有完成，因此我们在第 5 行进入第一个 if 块，并让出我们将要等待的东西——triple_task。
6. 现在控制权在program.main
    * await渗透收益率和收益率值—— triple_task。
7. 现在控制权在main_task.step
    * 变量awaited_task为triple_task。由于没有触发 StopIteration 事件，因此第 8 行 try 代码块中的 else 语句执行。main_task.step添加了一个 done 回调函数triple_task。该step方法结束并返回到事件循环。
8. 现在控制权掌握在手中。event-loop
    * 事件循环会遍历其队列中的下一个任务。事件循环triple_task从其队列中弹出任务并通过调用来调用它triple_task.step()。
9. 现在控制权在triple_task.step
    * 我们在第 4 行进入 try 代码块，然后triple在第 5 行开始协程。
10. 现在控制权在program.triple
    * 控制权转移到triple第 2 行的协程。它计算 3 乘以 5，然后结束并引发 StopIteration 异常。
11. 现在控制权在triple_task.step
    * StopIteration 异常被捕获，因此我们跳转到第 7 行。协程的返回值triple嵌入到value该异常的属性中。Future.set_result() 保存结果，将任务标记为已完成，并将完成回调添加triple_task到事件循环的队列中。该step方法结束，并将控制权返回给事件循环。
12. 现在控制权掌握在event-loop手中。
    * 事件循环会依次处理队列中的下一个任务。事件循环弹出main_task并通过调用main_task.step()来调用它.

> 注意，因为main_task并未被Future.set_result() 设置为已完成，所以它还在事件循环队列中。相反，triple_task已经被设置为完成，所以不在事件循环队列中了。

不是。main_task还在事件循环中，是因为当初triple_task添加了回调函数main_task.step。triple_task任务结束，它会将它的各种回调函数添加到事件循环中，在这里是恢复 main_task 的执行


13. 现在控制权在main_task.step
    * 我们在第 4 行进入 try 代码块，然后恢复协程main，协程会从上次 yield 的地方继续执行。请注意，yield 不是在协程内部，而是在triple_task.__await__第 6 行。
14. 现在控制权在triple_task.__await__
    * 我们评估第 8 行的 if 语句，以确保操作triple_task已完成。然后，它返回之前保存的值。最后，将该值result返回 给调用者（即）。triple_taskresult... = await triple_task
15. 现在控制权在program.main
    * tripled_val现在为 15。协程结束并引发 StopIteration 异常，返回值为 17。
16. 现在控制权在main-task.step
    * StopIteration 异常被捕获并main_task标记为已完成，其结果被保存。step方法结束，控制权返回给事件循环。
17. 现在控制权掌握在手中。event-loop
    * 队列中没有任何内容。事件循环漫无目的地继续进行。
