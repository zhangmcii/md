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


队列如何用C语言来实现？

结构体中放一个数组，一个队头指针(队头数据的位置)，一个队尾指针(数据的下一位置)
入队就是放在队尾指针下一个位置
出队就是返回队尾指针的元素

指针要做到循环队列，避免浪费空间

判空： front == rear
判满： 保留一个位置不放数据， (rear + 1) % size == front

队头和队尾计算环形下标，保证不越界： front = (front + 1) % size       rear = (rear + 1) % size
元素个数：(rear - front + size) % size

# define MaxSize 100
# define QueueSize 200
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

## 翻转一棵二叉树。
![题目8](https://file1.kamacoder.com/i/algo/20210203192644329.png)
思路：只要把每一个节点的左右孩子翻转一下，就可以达到整体翻转的效果。
    使用前序遍历和后序，层序遍历都可以，唯独中序遍历不方便，因为中序遍历会把某些节点的左右孩子翻转了两次！
卡点：一层又很多的节点，怎么swap()

层序遍历：
```
int* levelOrder(BiTree *root) {
    if (root == NULL) return res;

    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);

    while (!isEmpty(Q)) {
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            // 节点处理
            swap(p->lchild, p->rchild)
            if (p->rchild) EnQueue(Q, p->rchild);
            if (p->lchild) EnQueue(Q, p->lchild);
        }
    }
}
```

先序遍历：
```
void pre(BiTree root){
    if(root == NULL) return;
    swap(root->lchild, root->rchild);
    pre(root->lchild);
    pre(root->rchild);
}

```

##
思路： 利用层序遍历，子树不存在时，加入为null。然后查看每一层是否对称


## 给定一个二叉树，找出其最大深度。
思路：先用后序遍历（左右中）来计算树的高度。
后序遍历：
```
// 先求它的左子树的深度，再求右子树的深度，
// 最后取左右深度最大的数值 再+1 （加1是因为算上当前中间节点）就是目前节点为根节点的树的深度。
int getdepth(TreeNode* node) {
    if (node == NULL) return 0;
    int leftdepth = getdepth(node->left);       // 左
    int rightdepth = getdepth(node->right);     // 右
    int depth = 1 + max(leftdepth, rightdepth); // 中
    return depth;
}
getdepth(root);
```

上述代码可以进一步简化为：
```
void post_depth(BiTree root){
    if(root == NULL) return 0;
    return 1 + max(post(root->lchild) ,post(root->rchild));
}
post(root);
```

或者精简为：(显然没上面精简的好)
```
void post_depth(BiTree root, int depth){
    if(root == NULL) return depth;
    return max(post(root->lchild, depth+1) ,post(root->rchild, depth+1));
}
post(root, 1);

```

> 精简之后的代码根本看不出是哪种遍历方式，也看不出递归三部曲的步骤，所以如果对二叉树的操作还不熟练，尽量不要直接照着精简代码来学。

先序遍历：
```
int pre(BiTree root){
    if(root == NULL) return 0;
    int depth = 1
    int l = depth + pre(root->lchild)
    int r = depth + pre(root->rchild)
    return max(l, r)
}
```

优化：
```
int pre(BiTree root){
    if(root == NULL) return 0;
    return max(1 + pre(root->lchild),1 + pre(root->rchild))；
}
```

进一步优化：
```
int pre(BiTree root) {
    if (root == NULL) return 0;

    int leftDepth = pre(root->lchild);
    int rightDepth = pre(root->rchild);
    return (leftDepth > rightDepth ? leftDepth : rightDepth) + 1;
}
```



## 给出一个完全二叉树，求出该树的节点个数。

示例 1：
输入：root = [1,2,3,4,5,6]
输出：6

示例 2：
输入：root = []
输出：0

思路： 通过前，后序，层序，计算节点数量。

后序遍历：
```
int pre_count(BiTree root){
    if(root == NULL) return 0;
    int leftCount = pre_count(root->lchild);
    int rightCount = pre_count(root->rchild);
    return leftCount + rightCount + 1;
}
```

层序遍历：
```
int level_count(BiTree root){
    if (root == NULL) return res;
    int sum = 0;
    Queue Q;
    InitQueue(Q);

    BiTree p;
    EnQueue(Q, root);

    while (!isEmpty(Q)) {
        int size = count(Q);
        for (int i = 0; i < size; i++) {
            DeQueue(Q, p);
            sum++;
            if (p->lchild) EnQueue(Q, p->lchild);
            if (p->rchild) EnQueue(Q, p->rchild);
        }
    }
    return sum;
}

```
以上两种方法的时间复杂度都是O(n)

因为题目给的是 完全二叉树，可以更快地计算：如果某棵子树是满二叉树，节点数可以直接用公式 2^h - 1, 否则递归计算。
这样平均复杂度能到 O(log² n)，比单纯的递归 O(n) 更快。

这里关键在于如何去判断一个左子树或者右子树是不是满二叉树呢？
在完全二叉树中，如果递归向左遍历的深度等于递归向右遍历的深度，那说明就是满二叉树

1.获取某节点高度的函数。getDepth()
2.根据高度计算满二叉树节点数。 getCountByDepth()
3.递归遍历某节点求节点数量

```
#include <stdlib.h>
int getDepthByLeft(BiTree root){
    if(root == NULL) return 0;
    int leftDepth = getDepthByLeft(root->lchild);
    return leftDepth + 1;
}

int getDepthByRight(BiTree root){
    if(root == NULL) return 0;
    int rightDepth = getDepthByRight(root->rchild);
    return rightDepth + 1;
}
int isFullBiTree(BiTree root){
    if(root == NULL) return -1;
    int leftDepth = getDepthByLeft(root->lchild);
    int rightDepth = getDepthByRight(root->rchild);
    return leftDepth == rightDepth ? leftDepth : -leftDepth;
}

int pre_count(BiTree root){
    if(root == NULL) return 0;
    int leftCount = pre_count(root->lchild);
    int rightCount = pre_count(root->rchild);
    return leftCount + rightCount + 1;
}

int fullBiTreeCount(BiTree root){
    if(root == NULL) return 0;
    int childDepth = isFullBiTree(root);
    int leftCount = 0, rightCount = 0;
    if(childDepth > 0){
         leftCount = (1 << childDepth) - 1;
         rightCount = (1 << childDepth) - 1;
    }else{
         leftCount = (1 << abs(childDepth)) - 1;
         rightCount = pre_count(root);
    }
    return leftCount + rightCount + 1;
}

fullBiTreeCount(root)
```

```
int countNodes(TreeNode root) {
    if (root == NULL) return 0;
    TreeNode left = root->left;
    TreeNode right = root->right;
    int leftDepth = 0, rightDepth = 0;
    while (left) {  // 求左子树深度
        left = left->left;
        leftDepth++;
    }
    while (right) { // 求右子树深度
        right = right->right;
        rightDepth++;
    }
    if (leftDepth == rightDepth) {
        return (2 << leftDepth) - 1; // 注意(2<<1) 相当于2^2，
    }
    return countNodes(root->left) + countNodes(root->right) + 1;
}
```
时间复杂度：O(log n × log n) = O(log² n)
空间复杂度：O(log n)
