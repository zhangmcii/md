图：

dfs(深度优先遍历)的代码框架：
```
void dfs(参数) {
    if (终止条件) {
        存放结果;
        return;
    }

    for (选择：本节点所连接的其他节点) {
        处理节点;
        dfs(图，选择的节点); // 递归
        回溯，撤销处理结果
    }
}
```


深搜三部曲:
1.确认递归函数，参数
void dfs(参数)

2.确认终止条件
终止条件很重要，很多同学写dfs的时候，之所以容易死循环，栈溢出等等这些问题，都是因为终止条件没有想清楚。
```
if (终止条件) {
    存放结果;
    return;
}
```
终止添加不仅是结束本层递归，同时也是我们收获结果的时候。

3.处理目前搜索节点出发的路径
一般这里就是一个for循环的操作，去遍历 目前搜索节点 所能到的所有节点。
```
for (选择：本节点所连接的其他节点) {
    处理节点;
    dfs(图，选择的节点); // 递归
    回溯，撤销处理结果
}
```

邻接矩阵定义：
```
//顶点类型
typedef char VertexType;

//边上权类型
typedef int EdgeType;

//最大顶点数
#define MaxVEX 100

//邻接矩阵
typedef struct MGraph {
    //顶点表
    VertexType vex[MaxVEX];
    //邻接矩阵，边表
    EdgeType arc[MaxVEX][MaxVEX];

    //图中当前的顶点数和边数
    int numVertexes, numEdges;
} MGraph;
```


邻接表定义：
```
#define EdgeType int       // 边的权值类型
#define VertexType int     // 顶点数据类型（存储节点编号）
//边表结点
typedef struct EdgeNode {
    //邻接点域，存储改顶点对应的下标
    int adjvex;
    //链域，指向下一个邻接点
    struct EdgeNode *next;
    //用于存储权值，对于非网图可以不需要
    // EdgeType weight;
} EdgeNode;

//顶点表结点
typedef struct VertxNode {
    //顶点域，存储顶点信息
    VertexType data;
    //边表头指针
    EdgeNode *firstEdge;
} VertexNode, AdjList[MaxVEX];

typedef struct {
    AdjList adjList;
    //图中当前顶点数和边数
    int numVertexes, numEdges;
} GraphAdjList;
```


## 给定一个有 n 个节点的有向无环图，节点编号从 1 到 n。请编写一个程序，找出并返回所有从节点 1 到节点 n 的路径。每条路径应以节点编号的列表形式表示。

邻接矩阵：
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PATH_LEN 100  // 最大路径长度（可根据需求调整）
#define MAX_RESULT_NUM 100  // 最大路径数量（可根据需求调整）

int result[MAX_RESULT_NUM][MAX_PATH_LEN];  // 存储所有路径
int path[MAX_PATH_LEN];                    // 存储当前路径
int resultSize = 0;                        // 实际路径数量
int pathSize = 0;                          // 当前路径长度

// 深度优先搜索函数
// graph: 邻接矩阵（graph[x][i] = 1表示x到i有边）
// x: 当前节点
// n: 目标终点
void dfs(const int graph[][MAX_PATH_LEN], int x, int n) {
    // 到达终点，保存当前路径
    if (x == n) {
        // 将当前路径path复制到结果数组
        memcpy(result[resultSize], path, sizeof(int) * pathSize);
        resultSize++;  // 路径数量+1
        return;
    }

    // 遍历所有可能的下一个节点
    for (int i = 1; i <= n; i++) {
        // 若x到i有边，继续搜索
        if (graph[x][i] == 1) {
            path[pathSize++] = i;  // 当前节点加入路径
            dfs(graph, i, n);      // 递归搜索
            pathSize--;            // 回溯：移除当前节点
        }
    }
}

```


邻接表：
```
#define MaxVEX 100         // 最大顶点数
#define MaxPathLen 50      // 最大路径长度
#define MaxResultNum 100   // 最大路径数量

int result[MaxResultNum][MaxPathLen];  // 存储所有路径
int path[MaxPathLen];                  // 当前路径
int resultSize = 0;                    // 路径总数
int pathSize = 0;                      // 当前路径长度

void dfs(GraphAdjList *graph, int curVex, VertexType targetData) {
    // 找到目标节点，保存路径
    if (graph->adjList[curVex].data == targetData) {
        // 复制当前路径到结果数组
        memcpy(result[resultSize], path, sizeof(int) * pathSize);
        resultSize++;
        return;
    }

    // 遍历所有邻接节点
    EdgeNode *edge = graph->adjList[curVex].firstEdge;
    while (edge != NULL) {
        int nextVex = edge->adjvex;
        VertexType nextData = graph->adjList[nextVex].data;

        // 加入路径（检查数组边界）
        if (pathSize < MaxPathLen) {
            path[pathSize++] = nextData;
            dfs(graph, nextVex, targetData);
            pathSize--;  // 回溯
        }

        edge = edge->next;
    }
}

```


## 岛屿数量
给定一个由 1（陆地）和 0（水）组成的矩阵，你需要计算岛屿的数量。岛屿由水平方向或垂直方向上相邻的陆地连接而成，并且四周都是水域。你可以假设矩阵外均被水包围。

输入描述：

第一行包含两个整数 N, M，表示矩阵的行数和列数。

后续 N 行，每行包含 M 个数字，数字为 1 或者 0。

输出描述：

输出一个整数，表示岛屿的数量。如果不存在岛屿，则输出 0。

输入示例：
```
4 5
1 1 0 0 0
1 1 0 0 0
0 0 1 0 0
0 0 0 1 1
```
输出示例：

3

提示信息
![题目12](https://file1.kamacoder.com/i/algo/20240516111613.png)
根据测试案例中所展示，岛屿数量共有 3 个，所以输出 3。

数据范围：

1 <= N, M <= 50

思路： 广度+深度
只要陆地的前后左右有其他陆地，则属于同一个岛屿。斜方向不算。

选择邻接矩阵存储更合适：
```
bool visited[100];

int findIland(MGraph m, int start){
    VertexType curVex = m->vex[start]
    if()
}
返回值： 岛屿数量

终止条件是什么？
序号超过矩阵实际大小
```

```
#include <stdio.h>
#include <string.h>

// 定义网格最大尺寸（可根据实际需求调整）
#define MAX_ROWS 100
#define MAX_COLS 100

// 四个方向：上、右、下、左
int direction[4][2] = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};

// 静态二维数组存储网格和访问标记
int grid[MAX_ROWS][MAX_COLS];
int visited[MAX_ROWS][MAX_COLS];
int rows, cols;  // 实际网格的行数和列数

/**
 * 深度优先搜索标记连通的陆地
 */
void dfs(int x, int y) {
    // 终止条件：已访问或不是陆地
    if (visited[x][y] || grid[x][y] == 0) {
        return;
    }

    // 标记当前位置为已访问
    visited[x][y] = 1;

    // 遍历四个方向
    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];

        // 检查下标是否越界
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) {
            continue;
        }

        // 递归访问相邻位置
        dfs(next_x, next_y);
    }
}

int main() {
    // 读取网格行数和列数
    scanf("%d %d", &rows, &cols);

    // 读取网格数据（使用静态二维数组）
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            scanf("%d", &grid[i][j]);
        }
    }

    // 初始化访问标记数组为0（未访问）
    memset(visited, 0, sizeof(visited));

    int res = 0;
    // 遍历整个网格
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            // 找到未访问的陆地，计数并标记整个连通区域
            if (grid[i][j] == 1 && visited[i][j] == 0) {
                res++;
                dfs(i, j);
            }
        }
    }

    // 输出结果
    printf("%d\n", res);

    return 0;
}
```

python:
```
direction = [[0, 1], [1, 0], [0, -1], [-1, 0]]  # 四个方向：上、右、下、左


def dfs(grid, visited, x, y):
    """
    对一块陆地进行深度优先遍历并标记
    """
    # 与版本一的差别，在调用前增加判断终止条件
    if visited[x][y] or grid[x][y] == 0:
        return
    visited[x][y] = True

    for i, j in direction:
        next_x = x + i
        next_y = y + j
        # 下标越界，跳过
        if next_x < 0 or next_x >= len(grid) or next_y < 0 or next_y >= len(grid[0]):
            continue
        # 由于判断条件放在了方法首部，此处直接调用dfs方法
        dfs(grid, visited, next_x, next_y)


if __name__ == '__main__':
    # 版本二
    n, m = map(int, input().split())

    # 邻接矩阵
    grid = []
    for i in range(n):
        grid.append(list(map(int, input().split())))

    # 访问表
    visited = [[False] * m for _ in range(n)]

    res = 0
    for i in range(n):
        for j in range(m):
            # 判断：如果当前节点是陆地，res+1并标记访问该节点，使用深度搜索标记相邻陆地。
            if grid[i][j] == 1 and not visited[i][j]:
                res += 1
                dfs(grid, visited, i, j)

    print(res)
```