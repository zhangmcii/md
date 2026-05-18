
队列存储二叉树节点：
```
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MaxSize 100

typedef int ElemType;

/*
    二叉树节点
*/
typedef struct BiNode{
    ElemType data;
    struct BiNode *lchild, *rchild;
}BiNode, *BiTree;


/*
    循环队列
    队列里存的是 BiTree（树节点指针）
*/
typedef struct{
    BiTree data[MaxSize];
    int front;
    int rear;
}Queue;


/*
    初始化队列
*/
void InitQueue(Queue *Q){
    Q->front = 0;
    Q->rear = 0;
}


/*
    判空
*/
bool IsEmpty(Queue *Q){
    return Q->front == Q->rear;
}


/*
    判满

    牺牲一个存储单元：
    MaxSize=100
    实际最多存99个元素
*/
bool IsFull(Queue *Q){
    return (Q->rear + 1) % MaxSize == Q->front;
}


/*
    当前元素个数
*/
int Count(Queue *Q){
    return (Q->rear - Q->front + MaxSize) % MaxSize;
}


/*
    入队
*/
bool EnQueue(Queue *Q, BiTree x){

    if(IsFull(Q)){
        return false;
    }

    Q->data[Q->rear] = x;

    Q->rear = (Q->rear + 1) % MaxSize;

    return true;
}


/*
    出队
*/
bool DeQueue(Queue *Q, BiTree *x){

    if(IsEmpty(Q)){
        return false;
    }

    *x = Q->data[Q->front];

    Q->front = (Q->front + 1) % MaxSize;

    return true;
}


/*
    创建一个树节点
*/
BiTree CreateNode(int val){

    BiTree node = (BiTree)malloc(sizeof(BiNode));

    node->data = val;
    node->lchild = NULL;
    node->rchild = NULL;

    return node;
}


/*
    测试
*/
int main(){

    Queue Q;

    InitQueue(&Q);

    BiTree n1 = CreateNode(1);
    BiTree n2 = CreateNode(2);
    BiTree n3 = CreateNode(3);

    EnQueue(&Q, n1);
    EnQueue(&Q, n2);
    EnQueue(&Q, n3);

    printf("count = %d\n", Count(&Q));

    BiTree x;

    while(!IsEmpty(&Q)){

        DeQueue(&Q, &x);

        printf("%d\n", x->data);
    }

    return 0;
}
```


# 求深度适合用前序遍历，而求高度适合用后序遍历。

1. 深度和高度的区别
1.1 节点深度： 从根节点到当前节点所经过的边数 或者 当前节点在第几层
    特点： 从上往下计算。 （因为必须先知道父节点深度。）
1.2 节点高度： 从当前节点到最远叶子节点的最长路径
    特点： 从下往上计算。  （因为必须先知道左右子树高度。）

2.核心区别
2.1 深度 依赖父节点
```
depth(child)
=
depth(parent) + 1
```
所以天然适合 top-down（前序）

2.2 高度 依赖子节点
```
height(node)
=
1 + max(height(left), height(right))
```
所以天然适合 bottom-up（后序）

2.树的最大深度
实际上求 树的最大层数， 也就是 根节点的高度。
所以 “树的最大深度” ≠ “节点深度”
所以看到使用**后序遍历**求 树的最大深度 完全合理。
