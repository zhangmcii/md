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

二叉树节点定义：
```
typedef int ElemType；
typedef struct{
    ElemType data;
    struct BiNode *lchild, *rchild;
}BiNode, *BiTree;
```

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


## 给定一个二叉树，判断它是否是高度平衡的二叉树。

本题中，一棵高度平衡二叉树定义为：一个二叉树每个节点 的左右两个子树的高度差的绝对值不超过1。

示例 1:
给定二叉树 [3,9,20,null,null,15,7]
![题目9](https://file1.kamacoder.com/i/algo/2021020315542230.png)
返回 true 。

思路：先序遍历，判断每个节点的左右子树高度之差。会造成重复求,所以排除
    后序遍历可以

这里强调一波概念：

二叉树节点的深度：指从根节点到该节点的最长简单路径边的条数。
二叉树节点的高度：指从该节点到叶子节点的最长简单路径边的条数。
但leetcode中强调的深度和高度很明显是按照节点来计算的，如图：
![题目10](https://file1.kamacoder.com/i/algo/20210203155515650.png)

关于根节点的深度究竟是1 还是 0，不同的地方有不一样的标准，leetcode的题目中都是以节点为一度，即根节点深度是1。
但维基百科上定义用边为一度，即根节点的深度是0，我们暂时以leetcode为准（毕竟要在这上面刷题）。
因为求深度可以从上到下去查 所以需要前序遍历，而高度只能从下到上去查，所以只能后序遍历

后序遍历：
1.明确递归函数的参数和返回值
参数：当前传入节点。 返回值：以当前传入节点为根节点的树的高度。
如果当前传入节点为根节点的二叉树已经不是二叉平衡树了，还返回高度的话就没有意义了。
所以如果已经不是二叉平衡树了，可以返回-1 来标记已经不符合平衡树的规则了。
2.明确终止条件
递归的过程中依然是遇到空节点了为终止，返回0，表示当前节点为根节点的树高度为0
3.明确单层递归的逻辑
分别求出其左右子树的高度，然后如果差值小于等于1，则返回当前二叉树的高度，否则返回-1，表示已经不是二叉平衡树了。
```
int getDepth(BiTree root){
    if(root == NUll) return 0;
    lchildDepth = getDepth(root->lchild);
    if(lchildDepth == -1) return -1;
    rchildDepth = getDepth(root->rchild);
    if(rchildDepth == -1) return -1;
    if(abs(lchildDepth - rchildDepth) <= 1){
        return (lchildDepth > rchildDepth ? lchildDepth: rchildDepth) + 1;
    }
    return -1;
}

bool isBalanced(BiTree root){
    return getDepth(root) == -1 ? false: true;
}
```
> 总结
  通过本题可以了解求二叉树深度 和 二叉树高度的差异，求深度适合用前序遍历，而求高度适合用后序遍历。



## 给定一个二叉树，返回所有从根节点到叶子节点的路径。(比较难)

说明: 叶子节点是指没有子节点的节点。

示例:
![图片10](https://file1.kamacoder.com/i/algo/2021020415161576.png)
思路： 先序遍历

在这道题目中将第一次涉及到回溯，因为我们要把路径记录下来，需要回溯来回退一个路径再进入另一个路径。

``` python
# path用来记录路径
def traversal(self, cur, path, result):
    path.append(cur.val)
    if not cur.left and not cur.right:  # 到达叶子节点
        sPath = '->'.join(map(str, path))
        result.append(sPath)
        return
    if cur.left:  # 左
        self.traversal(cur.left, path, result)
        path.pop()  # 回溯
    if cur.right:  # 右
        self.traversal(cur.right, path, result)
        path.pop()  # 回溯

def binaryTreePaths(self, root):
    result = []
    path = []
    if not root:
        return result
    self.traversal(root, path, result)
    return result
```

标准写法：
```python
# 先序遍历
def binaryTreePaths_obvious(self, root):
        res = []
        path = []  # 共享的列表

        def backtrack(node):
            if not node:
                return
            
            # 1. 做选择：把当前节点加入路径
            path.append(str(node.val))
            
            # 如果是叶子节点，记录结果
            if not node.left and not node.right:
                res.append("->".join(path))
            else:
                # 2. 递归：去探索左边和右边
                if node.left: backtrack(node.left)
                if node.right: backtrack(node.right)
            
            # 3. 撤销选择：这就是【回溯】！
            path.pop() 

        backtrack(root)
        return res

```


## 计算给定二叉树的所有左叶子之和。
示例：
![题目11](https://file1.kamacoder.com/i/algo/20210204151927654.png)

思路：先序遍历。 找到所有左叶子，再累加
卡点： 怎么判断是左叶子

判断当前节点是不是左叶子是无法判断的，必须要通过节点的父节点来判断其左孩子是不是左叶子。
如果该节点的左节点不为空，该节点的左节点的左节点为空，该节点的左节点的右节点为空，则找到了一个左叶子，判断代码如下：
if (node->left != NULL && node->left->left == NULL && node->left->right == NULL) {
    左叶子节点处理逻辑
}


```
int sumOfLeftLeaves(TreeNode* root) {
    if (root == NULL) return 0;
    if (root->left == NULL && root->right== NULL) return 0;

    int leftValue = sumOfLeftLeaves(root->left);    // 左
    if (root->left && !root->left->left && !root->left->right) { // 左子树就是一个左叶子的情况
        leftValue = root->left->val;
    }
    int rightValue = sumOfLeftLeaves(root->right);  // 右

    int sum = leftValue + rightValue;               // 中
    return sum;
}
```

## 给定二叉搜索树（BST）的根节点和一个值。 你需要在BST中找到节点值等于给定值的节点。 返回以该节点为根的子树。 如果节点不存在，则返回 NULL。

例如，
![图片11](https://file1.kamacoder.com/i/algo/20210204155522476.png)
在上述示例中，如果要找的值是 5，但因为没有节点值为 5，我们应该返回 NULL。

递归:
```
TreeNode* searchBST(TreeNode* root, int val) {
    if (root == NULL || root->val == val) return root;
    TreeNode* result = NULL;
    if (root->val > val) result = searchBST(root->left, val);
    if (root->val < val) result = searchBST(root->right, val);
    return result;
}
```

优化：
```
TreeNode* searchBST(TreeNode* root, int val) {
    if (root == NULL || root->val == val) return root;
    if (root->val > val) return searchBST(root->left, val);
    if (root->val < val) return searchBST(root->right, val);
    return NULL;
}
```

迭代：
```
TreeNode* searchBST(TreeNode* root, int val) {
    while (root != NULL) {
        if (root->val > val) root = root->left;
        else if (root->val < val) root = root->right;
        else return root;
    }
    return NULL;
}
```


## 给定一个多叉树，每个节点存储两个属性：runtime，memory。现在计算每个节点到根节点的路径上的各属性之和

核心思路:
我们需要在遍历的过程中，把父节点传下来的“历史总和”加上“当前节点的值”，算出当前的总和，然后分别存起来，再传给子节点。


多叉树的深度遍历(先序遍历)
```python
from typing import List, Dict

# 1. 定义多叉树节点
class Node:
    def __init__(self, name: str, runtime: int, memory: int, children: List['Node'] = None):
        self.name = name        # 节点名称（用来标识）
        self.runtime = runtime  # 属性1
        self.memory = memory    # 属性2
        self.children = children if children else []

class Solution:
    def calcPathSums(self, root: 'Node') -> Dict[str, dict]:
        # 结果字典：Key是节点名, Value是该节点到根节点的累加属性
        results = {}
        
        if not root:
            return results

        # DFS 递归函数
        # node: 当前节点
        # acc_runtime: 从根节点到父节点的 runtime 之和
        # acc_memory: 从根节点到父节点的 memory 之和
        def dfs(node, acc_runtime, acc_memory):
            if not node:
                return
            
            # 1. 计算当前节点的路径总和 (父级累加 + 当前值)
            current_total_runtime = acc_runtime + node.runtime
            current_total_memory = acc_memory + node.memory
            
            # 2. 记录结果
            # 这里我们记录了每一个节点的路径和，不仅仅是叶子节点
            results[node.name] = {
                "total_runtime": current_total_runtime,
                "total_memory": current_total_memory
            }
            
            # 3. 递归遍历所有子节点
            # 将刚才计算好的 current_total 传给孩子
            for child in node.children:
                dfs(child, current_total_runtime, current_total_memory)
        
        # 初始调用：累加器从 0 开始
        dfs(root, 0, 0)
        
        return results

# --- 测试代码 ---
if __name__ == "__main__":
    # 构建多叉树结构
    #        Root (10, 100)
    #       /             \
    #    A (5, 50)       B (2, 20)
    #    /     \           |
    # A1(1,10) A2(3,30)  B1(4,40)

    # 创建节点
    root = Node("Root", 10, 100)
    node_a = Node("A", 5, 50)
    node_b = Node("B", 2, 20)
    node_a1 = Node("A1", 1, 10)
    node_a2 = Node("A2", 3, 30)
    node_b1 = Node("B1", 4, 40)

    # 建立连接关系
    root.children = [node_a, node_b]
    node_a.children = [node_a1, node_a2]
    node_b.children = [node_b1]

    # 计算
    sol = Solution()
    path_sums = sol.calcPathSums(root)

    # 打印结果
    for name, data in path_sums.items():
        print(f"节点 {name}: {data}")
```

关键点： 这里不需要像`二叉树返回所有从根节点到叶子节点的路径`那样维护一个 path 列表然后 pop() 回溯。因为我们传递的是数字（整数）。 在 Python 中，整数是不可变的。当我们把 current_sum + node.val 传给下一层递归时，下一层拿到了新的值，而当前层的变量并没有改变。当递归返回时，当前层的数值依然保持原样，自然就完成了“回溯”的效果。