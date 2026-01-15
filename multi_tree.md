# 多叉树 记录各个节点到根节点的属性和


上一篇介绍的[一文看透“回溯”本质]中，是关于二叉树的回溯，这次是多叉树的题目。

## 题目：
给定一个多叉树，每个节点存在一个属性runtime，现在计算每个节点到根节点的路径上的各属性之和

## 思路：此题不是找出叶子节点到根节点的路径，而是每个节点到根节点的路径属性只和。其实原理是一样的，我们只需要载遍历时累计节点只和即可。

```python
class Node:
    def __init__(self, name, runtime=0, children=None):
        self.name = name
        self.runtime = runtime
        self.children = children if children else []

def multi_tree(root):
    result = {}

    def gu(root, sum):
        if not root:
            return
        sum += root.runtime
        result[root.name] = sum

        for child in root.children:
            gu(child, sum)
    gu(root, 0)
    return result


if __name__ == '__main__':
# 构建多叉树结构
#            root 
#       /             \
#      a                b
#    /    \    \        |   \   \  
#  a1     a2   a3       b1   b2   b3
    a1 = Node('a1', 2)
    a2 = Node('a2', 2)
    a3 = Node('a3', 2)
    a = Node('a',3, [a1,a2,a3])

    b1 = Node('b1', 1)
    b2 = Node('b2', 1)
    b3 = Node('b3', 5)
    b = Node('b', 3, [b1, b2, b3])

    root = Node('root', 3, [a, b])

    print(multi_tree(root))
```



路径问题，使用先序遍历来深度优先搜索，一般涉及回溯的过程。

而python的字符串是不可变对象，在递归函数内修改sum会创建新对象,而不会影响到原对象的值。
所以递归返回到上一级时，sum还是会保持传入前的值。  

主要是依据字符串是不可变对象，函数调用栈自动恢复状态的行为。我们称之为“隐式回溯”。




