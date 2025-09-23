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

深搜版：
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



广搜版 加上辅助队列：
注意： 只要 加入队列就代表 走过，就需要标记，而不是从队列拿出来的时候再去标记走过。否则会超时
如果从队列拿出节点，再去标记这个节点走过，就会发生下图所示的结果，会导致很多节点重复加入队列。
![解释1](https://file1.kamacoder.com/i/algo/20250124094043.png)
```
// 四个方向：上、右、下、左
int direction[4][2] = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};

// 静态二维数组存储网格和访问标记
int grid[MAX_ROWS][MAX_COLS];
int visited[MAX_ROWS][MAX_COLS];
int rows, cols;  // 实际网格的行数和列数

// 坐标点
typedef struct {
    int x;
    int y;
} Point;

// 简单队列
typedef struct {
    Point data[MAX_QUEUE_SIZE];
    int front, rear;
}*Queue;

void bfs(int grid[MAX_ROWS][MAX_COLS], Queue Q, int startX, int startY) {
    enQueue(Q, {startX, startY});
    visited[startX][startY] = true;

    while(!isEmpty(Q)) {
        Point cur = deQueue(Q); // Point = {int x, int y}
        int curX = cur.x;
        int curY = cur.y;

        for(int i = 0; i < 4; i++) {
            int newX = curX + direction[i][0];
            int newY = curY + direction[i][1];

            if(newX < 0 || newY < 0 || newX >= rows || newY >= cols) continue;

            if(grid[newX][newY] == 1 && !visited[newX][newY]) {
                enQueue(Q, {newX, newY});
                visited[newX][newY] = true;
            }
        }
    }
}

int main() {
    int result = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (!visited[i][j] && grid[i][j] == 1) {
                result++; // 遇到没访问过的陆地，+1
                bfs(grid, Q, i, j); // 将与其链接的陆地都标记上 true
            }
        }
    }
}
```

## 岛屿最大面积
思路： 深搜。加入计数的数组

dfs的返回值： 岛屿面积


```
int dfs(int x, int y) {

    // 终止条件：已访问或不是陆地
    if (visited[x][y] || grid[x][y] == 0) {
        return 0;
    }
    // 标记当前位置为已访问
    visited[x][y] = true;
    // 面积为1
    int square = 1;


    // 遍历四个方向
    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];

        // 检查下标是否越界
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) {
            continue;
        }

        // 递归访问相邻位置
        square += dfs(next_x, next_y);
    }
    return square;
}

int main() {
    int res = 0;
    int maxSquare = 0;
    // 遍历整个网格
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            // 找到未访问的陆地，计数并标记整个连通区域
            if (grid[i][j] == 1 && visited[i][j] == false) {
                res = dfs(i, j);
                maxSquare = res >= maxSquare ? res : maxSquare;
            }
        }
    }

    // 输出结果
    printf("%d\n", maxSquare);

    return 0;
}
```


## 孤岛总面积
岛屿指的是由水平或垂直方向上相邻的陆地单元格组成的区域，且完全被水域单元格包围。
孤岛是那些位于矩阵内部、所有单元格都不接触边缘的岛屿。

现在你需要计算所有孤岛的总面积，岛屿面积的计算方式为组成岛屿的陆地的总数。

思路：深搜不检测边缘
思路2: 将周边靠陆地且相邻的陆地都变成海洋，然乎重新遍历计算陆地数即可
如图，在遍历地图周围四个边，靠地图四边的陆地，都为绿色，
![思路1](https://file1.kamacoder.com/i/algo/20220830104632.png)
![思路2](https://file1.kamacoder.com/i/algo/20220830104651.png)


错误：
```
sole = false
int dfs(int x, int y) {

    // 终止条件：已访问或不是陆地
    if (visited[x][y] || grid[x][y] == 0) {
        return 0;
    }
    // 标记当前位置为已访问
    visited[x][y] = true;
    // 面积为1
    int square = 1;


    // 遍历四个方向
    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];

        // 检查下标是否越界
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) {
            continue;
        }
        if(next_x == 0 || next_x == rows - 1 || next_y == 0 || next_y == cols - 1){
            // 非孤岛
            sole = false;
            continue;
        }

        // 递归访问相邻位置
        square += dfs(next_x, next_y);
    }
    return sole == true ? square: 0;
}

int main() {

    int res = 0;
    int maxSquare = 0;
    // 遍历整个网格
    for (int i = 1; i < rows - 1; i++) {
        for (int j = 1; j < cols - 1; j++) {
            // 找到未访问的陆地，计数并标记整个连通区域
            if (grid[i][j] == 1 && visited[i][j] == false) {
                sole = true;
                res = dfs(i, j);
                maxSquare = res >= maxSquare ? res : maxSquare;
            }
        }
    }

    // 输出结果
    printf("%d\n", maxSquare);
    return 0;
}
```


改正：
更好的方式是：
1.先完整计算岛屿面积
2.DFS 只返回面积，不关心是否孤岛
3.外层 main 根据 sole 决定是否加到总和

```

bool sole; // 标记是否孤岛

int dfs(int x, int y) {
    if (visited[x][y] || grid[x][y] == 0) {
        return 0;
    }
    visited[x][y] = true;
    int square = 1;

    // 如果当前点在边界，说明不是孤岛
    if (x == 0 || x == rows - 1 || y == 0 || y == cols - 1) {
        sole = false;
    }

    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) continue;
        square += dfs(next_x, next_y);
    }
    return square;
}

int main() {
    int totalArea = 0;

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (grid[i][j] == 1 && visited[i][j] == false) {
                sole = true; // 每次新岛屿默认是孤岛
                int area = dfs(i, j);
                if (sole) {
                    totalArea += area;
                }
            }
        }
    }

    printf("%d\n", totalArea);
    return 0;
}

```

## 沉没孤岛
思路1： 找出孤岛， 对孤岛进行更新
思路2: 步骤一：深搜或者广搜将地图周边的 1 （陆地）全部改成 2 （特殊标记）
步骤二：将水域中间 1 （陆地）全部改成 水域（0）
步骤三：将之前标记的 2 改为 1 （陆地）


```
bool sole; // 标记是否孤岛

int dfs(int x, int y) {
    if (visited[x][y] || grid[x][y] == 0) {
        return 0;
    }
    visited[x][y] = true;
    int square = 1;

    // 如果当前点在边界，说明不是孤岛
    if (x == 0 || x == rows - 1 || y == 0 || y == cols - 1) {
        sole = false;
    }

    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) continue;
        square += dfs(next_x, next_y);
    }
    return square;
}


void updateInland(int grid[MAX_ROWS][MAX_COLS], int x, int y){
    if (grid[x][y] == 0) {
        return;
    }
    grid[x][y] = 0;

    for (int i = 0; i < 4; i++) {
        int next_x = x + direction[i][0];
        int next_y = y + direction[i][1];
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) continue;
        updateInland(grid, next_x, next_y);
    }
}

int main() {
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            if (grid[i][j] == 1 && visited[i][j] == 0) {
                sole = true; // 每次新岛屿默认是孤岛
                dfs(i, j);
                if (sole) {
                    updateInland(grid, i, j);
                }
            }
        }
    }
    return 0;
}

```

## 高山流水
现有一个 N × M 的矩阵，每个单元格包含一个数值，这个数值代表该位置的相对高度。矩阵的左边界和上边界被认为是第一组边界，而矩阵的右边界和下边界被视为第二组边界。

思路： 深搜，对上下左右方向进行搜索
终止条件： 当前坐标在第一或第二边界上
```
bool visited[10][10];
int direction[4][2] = {{1,0}, {-1, 0}, {0, 1}, {0, -1}}

void dfs(int x, int y){
    for(int i=0;i<4;i++){
        next_x = direction[i][0]
        next_y = direction[i][1]
        if (next_x < 0 || next_x >= rows || next_y < 0 || next_y >= cols) continue;
        if(grid[x][y] >= grid[next_x][next_y]){
            dfs(next_x, next_y)
        }
    }
}

```


## 拓扑排序

思路：实现拓扑排序的算法有两种：卡恩算法（BFS）和DFS
一般来说我们只需要掌握 BFS （广度优先搜索）就可以了，清晰易懂
拓扑排序的过程，其实就两步：
1.找到入度为0 的节点，加入结果集
2.将该节点从图中移除

邻接矩阵：
```
void topologicalSortKahn(int numVertices, int** graph) {
    int* inDegree = (int*)calloc(numVertices, sizeof(int));
    int* queue = (int*)malloc(numVertices * sizeof(int));
    int front = 0, rear = 0;
    int count = 0; // 已输出的顶点数

    // 计算入度
    for (int i = 0; i < numVertices; i++) {
        for (int j = 0; j < numVertices; j++) {
            if (graph[j][i] > 0) {
                inDegree[i]++;
            }
        }
    }

    // 入度为0的顶点入队
    for (int i = 0; i < numVertices; i++) {
        if (inDegree[i] == 0) {
            queue[rear++] = i;
        }
    }

    // 拓扑排序
    while (front < rear) {
        int u = queue[front++];
        printf("%d ", u);
        count++;

        for (int v = 0; v < numVertices; v++) {
            if (graph[u][v] > 0) {
                if (--inDegree[v] == 0) {
                    queue[rear++] = v;
                }
            }
        }
    }

    // 检查是否存在环
    if (count != numVertices) {
        printf("\n图中存在环路!\n");
    }

    free(inDegree);
    free(queue);
}
```


邻接表：
```
#include <stdio.h>
#include <stdlib.h>
#define MAX_VERTEX 100

// 邻接表节点结构
typedef struct ArcNode {
    int adjvex;
    struct ArcNode* nextarc;
} ArcNode;

// 顶点节点结构
typedef struct VNode {
    char data;
    ArcNode* firstarc;
    int inDegree; // 顶点入度
} VNode, AdjList[MAX_VERTEX];

// 图结构
typedef struct {
    AdjList vertices;
    int vexnum, arcnum;
} ALGraph;

// 创建邻接表
void CreateALGraph(ALGraph* G) {
    printf("输入顶点数和边数: ");
    scanf("%d %d", &G->vexnum, &G->arcnum);

    // 初始化顶点
    printf("输入%d个顶点数据: ", G->vexnum);
    for (int i = 0; i < G->vexnum; i++) {
        scanf(" %c", &G->vertices[i].data);
        G->vertices[i].firstarc = NULL;
        G->vertices[i].inDegree = 0;
    }

    // 构建边
    printf("输入%d条边(格式:起点下标 终点下标):\n", G->arcnum);
    for (int k = 0; k < G->arcnum; k++) {
        int i, j;
        scanf("%d %d", &i, &j);

        ArcNode* p = (ArcNode*)malloc(sizeof(ArcNode));
        p->adjvex = j;
        p->nextarc = G->vertices[i].firstarc;
        G->vertices[i].firstarc = p;
        G->vertices[j].inDegree++; // 终点入度增加
    }
}

// 拓扑排序
int TopologicalSort(ALGraph G) {
    int stack[MAX_VERTEX], top = -1;
    int count = 0; // 输出顶点计数
    int* result = (int*)malloc(G.vexnum * sizeof(int));

    // 将入度为0的顶点入栈
    for (int i = 0; i < G.vexnum; i++) {
        if (G.vertices[i].inDegree == 0) {
            stack[++top] = i;
        }
    }

    while (top != -1) {
        int v = stack[top--];
        result[count++] = v;

        // 遍历v的所有邻接点
        ArcNode* p = G.vertices[v].firstarc;
        while (p != NULL) {
            int k = p->adjvex;
            if (--G.vertices[k].inDegree == 0) {
                stack[++top] = k;
            }
            p = p->nextarc;
        }
    }

    // 输出拓扑序列
    if (count == G.vexnum) {
        printf("拓扑排序结果: ");
        for (int i = 0; i < count; i++) {
            printf("%c ", G.vertices[result[i]].data);
        }
        printf("\n");
        free(result);
        return 1;
    } else {
        printf("图中存在环，无法拓扑排序\n");
        free(result);
        return 0;
    }
}

int main() {
    ALGraph G;
    CreateALGraph(&G);
    TopologicalSort(G);
    return 0;
}
```


## 判断拓扑排序是否唯一
思路：初始化时将所有入度为0的顶点放入队列。每次从队列中取出一个顶点，并移除其所有出边。若队列中存在多个顶点，则拓扑排序不唯一；若仅有一个顶点，则排序唯一。

邻接矩阵：
```
void topologicalSortKahn(int numVertices, int** graph) {
    int* inDegree = (int*)calloc(numVertices, sizeof(int));
    int* queue = (int*)malloc(numVertices * sizeof(int));
    int front = 0, rear = 0;
    int count = 0; // 已输出的顶点数

    // 计算入度
    for (int i = 0; i < numVertices; i++) {
        for (int j = 0; j < numVertices; j++) {
            if (graph[j][i] > 0) {
                inDegree[i]++;
            }
        }
    }

    // 入度为0的顶点入队
    for (int i = 0; i < numVertices; i++) {
        if (inDegree[i] == 0) {
            queue[rear++] = i;
        }
    }

    // 标记拓扑序是否唯一
    int unique = 1;

    // 拓扑排序
    while (front < rear) {
        if (rear - front > 1) {
            unique = 0; // 队列里有多个候选，序列不唯一
        }
        int u = queue[front++];
        printf("%d ", u);
        count++;

        for (int v = 0; v < numVertices; v++) {
            if (graph[u][v] > 0) {
                if (--inDegree[v] == 0) {
                    queue[rear++] = v;
                }
            }
        }
    }

    if (count != numVertices) {
        printf("\n图中存在环路!\n");
    } else if (!unique) {
        printf("\n拓扑排序不唯一!\n");
    } else {
        printf("\n拓扑排序唯一!\n");
    }

    free(inDegree);
    free(queue);
}
```
