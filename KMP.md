# KMP模式匹配

实现 strStr() 函数。
给定一个 haystack 字符串和一个 needle 字符串，在 haystack 字符串中找出 needle 字符串出现的第一个位置 (从0开始)。如果不存在，则返回  -1。
示例 1: 输入: haystack = "hello", needle = "llo" 输出: 2
示例 2: 输入: haystack = "aaaaa", needle = "bba" 输出: -1
说明: 当 needle 是空字符串时，我们应当返回什么值呢？这是一个在面试中很好的问题。 对于本题而言，当 needle 是空字符串时我们应当返回 0 。这与C语言的 strstr() 以及 Java的 indexOf() 定义相符。


思路1: 暴力匹配。
i指向haystack第一个字符位置，j指向needle第一个字符位置。
遍历haystack。
若haystack[i] != needle[j], 则j=j+1, i=i+1
若所指的值相等，同步移动i,j。否则，i退回i-j+1的位置，j回到needle第一个字符位置

n为文本串长度，m为模式串长度，
时间: O(n*m)
空间: O(1)
~~~
#include <stdio.h>
#include <string.h>

int match(const char* haystack, const char* needle) {
    int i = 0, j = 0;
    int lenSource = strlen(haystack);
    int lenTarget = strlen(needle);

    if (lenTarget == 0) return 0; // 空字符串返回0

    while (i < lenSource && j < lenTarget) {
        if (haystack[i] == needle[j]) {
            i++;
            j++;
            if (j == lenTarget) {
                return i - j;
            }
        } else {
            i = i - j + 1;  // 回退到上次匹配的下一个位置
            j = 0;
        }
    }

    return -1;
}
~~~

| 写法                                  | 是否正确    | 优点          | 缺点               |
| ----------------------------------- | ------- | ----------- | ---------------- |
| ✅ `if (j == lenTarget)` 在 while 里面  | ✅ 推荐写法  | 立即返回结果，逻辑直观 | 无明显缺点            |
| ❇️ `if (j == lenTarget)` 在 while 外面 | ✅ 逻辑也正确 | 循环逻辑更“纯粹”   | 稍微多判断一次循环边界，不够直接 |


思路2: KMP算法
思想：当出现字符串不匹配时，可以知道一部分之前已经匹配的文本内容，可以利用这些信息避免从头再去做匹配了。
时间: O(n+m)
空间: O(m)

解释几个名词概念：

前缀表：
    定义：记录下标i之前（包括i）的字符串中，有多大长度的相同前缀后缀。
    作用：是用来回退的，它记录了模式串与主串不匹配的时候，模式串应该从哪里开始重新匹配。
next数组就是一个前缀表

## 最长公共前后缀
文章中字符串的前缀是指不包含最后一个字符的所有以第一个字符开头的连续子串。
后缀是指不包含第一个字符的所有以最后一个字符结尾的连续子串。
**正确理解什么是前缀什么是后缀很重要!**

因为前缀表要求的就是相同前后缀的长度， 用“最长相等前后缀” 更准确一些。
所以字符串a的最长相等前后缀为0。 字符串aa的最长相等前后缀为1。 字符串aaa的最长相等前后缀为2。 等等.

## 为什么一定要用前缀表


为了清楚地了解前缀表的来历，我们来举一个例子：
要在文本串：aabaabaafa 中查找是否出现过一个模式串：aabaaf。

刚刚匹配的过程在下标5的地方遇到不匹配，模式串是指向f，如图：
![示例1](https://file1.kamacoder.com/i/algo/KMP%E7%B2%BE%E8%AE%B21.png)
然后就找到了下标2，指向b，继续匹配：如图:
![示例2](https://file1.kamacoder.com/i/algo/KMP%E7%B2%BE%E8%AE%B22.png)

以下这句话，对于理解为什么使用前缀表可以告诉我们匹配失败之后跳到哪里重新匹配 非常重要！

下标5之前这部分的字符串（也就是字符串aabaa）的最长相等的前缀 和 后缀字符串是 子字符串aa ，
因为找到了最长相等的前缀和后缀，匹配失败的位置是后缀子串的后面，那么我们找到与其相同的前缀的后面重新匹配就可以了。

所以前缀表具有告诉我们当前位置匹配失败，跳到之前已经匹配过的地方的能力


## 如何计算前缀表
长度为前1个字符的子串a，最长相同前后缀的长度为0。
长度为前4个字符的子串aaba，最长相同前后缀的长度为1。 长度为前5个字符的子串aabaa，最长相同前后缀的长度为2。 长度为前6个字符的子串aabaaf，最长相同前后缀的长度为0。
![示例3](https://file1.kamacoder.com/i/algo/KMP%E7%B2%BE%E8%AE%B28.png)

可以看出模式串与前缀表对应位置的数字表示的就是：下标i之前（包括i）的字符串中，有多大长度的相同前缀后缀。

再来看一下如何利用 前缀表找到 当字符不匹配的时候应该指针应该移动的位置。如动画所示：
![示例4](https://file1.kamacoder.com/i/algo/KMP%E7%B2%BE%E8%AE%B22.gif)
- 找到的不匹配的位置， 那么此时我们要看它的前一个字符的前缀表的数值是多少。(为什么要前一个字符的前缀表的数值呢，因为要找前面字符串的最长相同的前缀和后缀。)
- 前一个字符的前缀表的数值是2， 所以把下标移动到下标2的位置继续比配。
- 最后就在文本串中找到了和模式串匹配的子串了。


## 前缀表与next数组
next数组就可以是前缀表，但是很多实现都是把前缀表统一减一（右移一位，初始位置为-1）之后作为next数组。
为什么这么做呢?
其实这并不涉及到KMP的原理，而是具体实现，next数组既可以就是前缀表，也可以是前缀表统一减一（右移一位，初始位置为-1）。


## 构造next数组
1.初始化：
定义两个指针i和j，j指向前缀末尾位置，i指向后缀末尾位置。
然后还要对next数组进行初始化赋值，如下：
~~~
int j = -1;
next[0] = j;
~~~

2.处理前后缀不相同的情况
~~~
while (j >= 0 && s[i] != s[j + 1]) { // 前后缀不相同了
    j = next[j]; // 向前回退
}
~~~


问题： 为什么失配时，j = next[j] ？
通俗理解一句话总结：“next[j]” 就是告诉你，当 s[i] 与 s[j+1] 失配时，j 应该退回到哪个位置继续尝试。
上面说的是主串和模式串的比较，当失配时，之后跳到哪里重新匹配。
这里是模式串（相当于主串）和子模式串（相当于模式串）的比较，当失配时，之后跳到哪里重新匹配。 说白了，就是 模式串自己当主串，用它的前缀和后缀做匹配实验。


3.处理前后缀相同的情况
如果 s[i] 与 s[j + 1] 相同，那么就同时向后移动i 和j 说明找到了相同的前后缀，同时还要将j（前缀的长度）赋给next[i], 因为next[i]要记录相同前后缀的长度。
~~~
if (s[i] == s[j + 1]) { // 找到相同的前后缀
    j++;
}
next[i] = j;
~~~


问题： 为什么在匹配成功时用 if (s[i] == s[j + 1]) j++;  ？
背后体现了整个 KMP 的「前后缀最长匹配长度递推思想」。
总结成一句话： if (s[i] == s[j + 1]) j++;  表示前一个前后缀又延长了 1 个字符。
             next[i] = j;  记录下目前为止的最长相等前后缀长度（或末尾下标）。



完整代码：
~~~
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// 构造 next 数组
void buildNext(const char *pattern, int *next) {
    int n = strlen(pattern);
    int j = -1;         // j 表示前缀末尾
    next[0] = j;

    for (int i = 1; i < n; i++) {
        // 如果当前字符不匹配，就回退 j
        while (j >= 0 && pattern[i] != pattern[j + 1]) {
            j = next[j];
        }
        // 如果匹配，扩展 j
        if (pattern[i] == pattern[j + 1]) {
            j++;
        }
        next[i] = j; // 记录前缀末尾位置
    }
}

// KMP 主函数
int KMP(const char *haystack, const char *needle) {
    int n = strlen(haystack);
    int m = strlen(needle);
    if (m == 0) return 0;  // 空模式串返回 0

    int *next = (int *)malloc(sizeof(int) * m);
    buildNext(needle, next);

    int j = -1; // 当前已匹配的模式串末尾位置
    for (int i = 0; i < n; i++) {
        // 如果当前字符不匹配，就回退 j
        while (j >= 0 && haystack[i] != needle[j + 1]) {
            j = next[j];
        }
        // 如果匹配，j 向后移动
        if (haystack[i] == needle[j + 1]) {
            j++;
        }
        // 若 j 到达模式串末尾，说明找到一个匹配
        if (j == m - 1) {
            free(next);
            return i - m + 1; // 返回匹配起始下标
        }
    }

    free(next);
    return -1; // 没有找到匹配
}
~~~






















默写：
~~~
int KMP(char* s, char* t){
    int lenSource = strlen(s);
    int lenTarget = strlen(t);
    if(lenTarget == 0) return 0;

    // 构造next前缀数组
    int* next = (int*)malloc(sizeof(int)*lenTarget);
    buildNext(t, next);

    int j = -1;
    for(int i = 0;i < lenSource;i++){
        // j+1处失配
        while(j>=0 && s[i] != t[j+1]){
            // 查找前一个字符的前缀表
            j = next[j];
        }
        // 当前处匹配，j向后移动
        if(s[i] == t[j+1]){
            j++;
        }

        if(j == lenTarget - 1){
            // 重要。别忘了释放空间‼️
            free(next);
            // 因为前缀表统一减1了，即j是从-1开始
            return i - j + 1;
        }
    }
    // 重要。别忘了释放空间‼️
    free(next);
    return -1;
}

出错的地方：申请了空间，在函数结束时需要释放：  free(next);
~~~


~~~
void buildNext(char* t, int* next){
    int lenTarget = strlen(t);
    int j = -1;
    next[0] = j;
    for(int i = 1; i < lenTarget; i++){
        // 失配
        while(j >= 0 && t[i] != t[j+1]){
            // j回退到前一个字符的前缀表
            j = next[j];
        }
        
        // 匹配，j向后移动
        if(t[i] == t[j+1]){
            j++;
        }
        next[i] = j;
    }
}

出错的地方：函数无返回值即可： void buildNext
~~~


