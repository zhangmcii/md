//#include <stdio.h>
//
//int main(){
//    printf("111");
//
//}
//
//int travel(BiTree T){
//    // 初始化队列Q
//    // 根结点入队
//    while(!IsEmpty(Q)){
//        BiTree q = pop(Q)
//        printf(q.value)
//        if(q.left){
//            push(q.left)
//        }
//        if(q.right){
//            push(q.right)
//        }
//
//    }
//}

模版1:
int LevelOrder(BiTree T){
    InitQueue(Q);
    BiTree p;
    EnQueue(Q, T);
    // 根结点入队
    while(!IsEmpty(Q)){
        DeQueue(Q, p);
        Visit(p);
        if(p->lchild != NULL){
            EnQueue(Q, p->lchild);
        }
        if(p->rchild != NULL){
            EnQueue(Q, p->rchild);
        }
    }
}

模版2:
int* levelOrder(BiTree *root, int *returnSize) {
    static int res[1000];
    int j = 0;
    //告诉调用者数组的实际长度
    *returnSize = 0;
    if (root == NULL) return res;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);

    while (!isEmpty(Q)) {
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            res[j++] = p->value;
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
    }
    *returnSize = j;
    return res;
}

> 模版1，单纯while循环。while循环一次， 队列增加某个节点的孩子节点
  模版2，在while循环中加入对队列遍历的for循环。while循环一次，队列中就保存着下一层的所有结点

---
队列如何用C语言来实现？

结构体中放一个数组，一个队头指针(队头数据的位置)，一个队尾指针(数据的下一位置)
入队就是放在队尾指针下一个位置
出队就是返回队尾指针的元素

指针要做到循环队列，避免浪费空间

判空： front == rear
判满： 保留一个位置不放数据， (rear + 1) % size == front

队头和队尾计算环形下标，保证不越界： front = (front + 1) % size       rear = (rear + 1) % size
元素个数：(rear - front + size) % size

\# define MaxSize 100
\# define QueueSize 200
typedef struct {
    int data[MaxSize];
    int front;
    int rear;
}*Queue;

void InitQueue(Queue Q){
    Q->data = (BiTree*)malloc(sizeof(BiTree) * QueueSize);
    Q.front = 0;
    Q.rear = 0;
}

bool IsEmpty(Queue Q){
    if(Q.rear == Q.front){
        return true;
    }
    return false;
}

bool IsFull(Queue Q){
    if((Q.rear + 1) % size = Q.front){
        return true;
    }
    return false;
}

int count(Queue Q){
    return (Q.rear - Q.front + size) % size
}

bool EnQueue(Queue Q, BiTree q){
    if(IsFull()){
        return false;
    }
    Q.data[Q.rear] = q;
    Q.rear = (Q.rear + 1) % size
    return true;
}

bool DeQueue(Queue Q, BiTree &q){
     if(IsEmpty()){
        return false;
     }
     q = Q.data[Q.front];
     Q.front = (Q.front + 1) % size;
     return true;
}

---

## 给定一个二叉树，返回其节点值自底向上的层次遍历。 （即按从叶子节点所在层到根节点所在的层，逐层从左向右遍历）
思路: 相对于二叉树的层序遍历，就是最后把result数组反转一下就可以了。



## 给定一棵二叉树，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看到的节点值。
![题目2](https://file1.kamacoder.com/i/algo/20210203151307377.png)
思路：层序遍历的时候，判断是否遍历到单层的最后面的元素，如果是，就放进result数组中，随后返回result就可以了。
```
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rightSideView(self, root: TreeNode) -> List[int]:
        if not root:
            return []

        queue = collections.deque([root])
        right_view = []

        while queue:
            level_size = len(queue)

            for i in range(level_size):
                node = queue.popleft()

                if i == level_size - 1:
                    right_view.append(node.val)

                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return right_view
```


## 给定一个非空二叉树, 返回一个由每层节点平均值组成的数组。
![题目3](https://file1.kamacoder.com/i/algo/20210203151350500.png)
思路： 对在队列中的元素取评论值即可
卡点： 一层的结束
```
def average(Queue Q, BiTree T)(){
    InitQueue(Q);
    BiTree p, q;
    EnQueue(Q, T);
    int sum = 0;
    int average_ = []
    int j = 0;
    while(!IsEmpty(Q)){
        int len = count(Q)
        for(int i = 0;i < len;i++){
            DeQueue(Q, p);
            sum += p.value;
            if(p->lchild != NULL){
                EnQueue(Q, p->lchild);
            }
            if(p->rchild != NULL){
                EnQueue(Q, p->rchild);
            }
        }
        average_[j++] = sum / len;
    }
}

```

## 您需要在二叉树的每一行中找到最大的值。
![题目4](https://file1.kamacoder.com/i/algo/20210203151532153.png)
思路： 对在队列中的元素取最大值即可
```
int* levelMax(BiTree *root, int *returnSize) {
    static int res[1000];
    int j = 0;
    //告诉调用者数组的实际长度
    *returnSize = 0;
    if (root == NULL) return res;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);

    while (!isEmpty(Q)) {
        int size = count(Q);
        int maxValue = Q.data[Q.front]->value;
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            if(p->value > maxValue){
                maxValue = p->value;
            }
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
        res[j++] = maxValue;
    }

    *returnSize = j;
    return res;
}
```

## 给定一个二叉树，其所有叶子节点都在同一层，每个父节点都有两个子节点。二叉树定义如下：
struct Node {
  int val;
  Node *left;
  Node *right;
  Node *next;
}
填充它的每个 next 指针，让这个指针指向其下一个右侧节点。如果找不到下一个右侧节点，则将 next 指针设置为 NULL。
初始状态下，所有 next 指针都被设置为 NULL。
![题目5](https://file1.kamacoder.com/i/algo/20210203152044855.jpg)
思路：对每层的节点进行便利，设置前后指针进行赋值
```
void levelOrder(BiTree *root) {
    if (root == NULL) return;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);

    while (!isEmpty(Q)) {
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            if(i < size -1){
                p->next = Q.data[Q.front];
            }
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
    }
}
```

## 给定一个二叉树，找出其最大深度。

二叉树的深度为根节点到最远叶子节点的最长路径上的节点数。

说明: 叶子节点是指没有子节点的节点。

示例：
给定二叉树 [3,9,20,null,null,15,7]，
![题目6](https://file1.kamacoder.com/i/algo/20210203153031914-20230310134849764.png)
返回它的最大深度 3 。
思路： 计算有多少层即可
```
int levelOrder(BiTree *root) {
    if (root == NULL) return res;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);
    int depth = 0;
    while (!isEmpty(Q)) {
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
        depth++;
    }
    return depth;
}
```

## 给定一个二叉树，找出其最小深度。
最小深度是从根节点到最近叶子节点的最短路径上的节点数量。
![题目7](https://assets.leetcode.com/uploads/2020/10/12/ex_depth.jpg)

思路：第i层是满节点的数量为2^(i-1)，第一个小于这个数量的层， 就是最小深度
易错点： 只有当左右孩子都为空的时候，才说明遍历的最低点了。如果其中一个孩子为空则不是最低点
```
#include <math.h>
int levelOrder(BiTree *root, int *returnSize) {

    if (root == NULL) return res;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);
    int depth = 0;
    while (!isEmpty(Q)) {
        depth++;
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            // 当左右孩子都为空的时候，说明是最低点的一层了，退出
            if(p->lchild == NULL && p->rchild == NULL){
                return depth;
            }
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
    }
    return depth;
}
```