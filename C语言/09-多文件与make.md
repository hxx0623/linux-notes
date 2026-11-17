# C 语言 第 8 课（下）：多文件与 Makefile

> 2026-11-17。**核心：`.h` 是菜单，`.c` 是厨房。**

---

## 一、为什么要多文件

```
单文件写到 2000 行 → 自己都找不到函数在哪
真实项目（Linux 内核）有 34667 个 .c
        ↓
必须拆：一个模块 = 一个 .h（声明）+ 一个 .c（实现）
```

---

## 二、项目结构

```
08-project/
├── calc.h         ← 声明（别人能用什么）
├── calc.c         ← 实现（函数体）
├── main.c         ← 主程序
└── Makefile       ← 一键编译
```

| 文件 | 放什么 | 谁 include |
| --- | --- | --- |
| **`.h`** | **只有声明**（函数原型、结构体、宏） | 谁要用谁 include |
| **`.c`** | **函数体** | **不 include，单独编译** |
| `main.c` | 主程序 | include `.h` |

### `calc.h`

```c
#ifndef CALC_H          /* 头文件保护 */
#define CALC_H

int calc_add(int a, int b);
int calc_sub(int a, int b);
int calc_mul(int a, int b);
int calc_div(int a, int b, int *out);   /* 成功返 0，结果写 *out */

#endif
```

### `calc.c`

```c
#include "calc.h"       /* ⚠️ 自己的头文件用【双引号】 */

int calc_add(int a, int b) { return a + b; }
int calc_sub(int a, int b) { return a - b; }
int calc_mul(int a, int b) { return a * b; }

int calc_div(int a, int b, int *out)    /* 复习第 5 课：指针出参 + 错误码 */
{
    if (b == 0) return -1;
    *out = a / b;
    return 0;
}
```

### `main.c`

```c
#include <stdio.h>
#include "calc.h"

int main(void)
{
    printf("3 + 5 = %d\n", calc_add(3, 5));
    printf("9 - 4 = %d\n", calc_sub(9, 4));
    printf("6 * 7 = %d\n", calc_mul(6, 7));

    int result;
    if (calc_div(10, 2, &result) == 0) printf("10 / 2 = %d\n", result);
    else                               printf("10 / 2 失败\n");

    if (calc_div(1, 0, &result) == 0)  printf("1 / 0 = %d\n", result);
    else                               printf("1 / 0 失败（除数为 0）\n");
    return 0;
}
```

**实测输出**：
```
3 + 5 = 8
9 - 4 = 5
6 * 7 = 42
10 / 2 = 5
1 / 0 失败（除数为 0）
```

---

## 三、`#include` 两种写法（必须分清）

```c
#include <stdio.h>     /* 尖括号 = 系统头文件，去 /usr/include 找 */
#include "calc.h"      /* 双引号 = 自己的，先去当前目录找 */
```
写成 `<calc.h>` → `fatal error: calc.h: No such file or directory`

---

## 四、⭐ 头文件保护

```c
#ifndef CALC_H          /* 没定义过 CALC_H？ */
#define CALC_H          /* 定义它 */

/* 内容 */

#endif
```

**没有它会怎样**：同一个头文件被包含两次 → `redefinition of 'int calc_add'`；
或者 a.h ↔ b.h 互相包含 → 无限递归。

**有了它**：第二次包含时 `#ifndef` 为假 → 整段跳过。

**现代写法** `#pragma once`（一行），但 `#ifndef` 是跨编译器标准，内核里全用它。

---

## 五、两种编译方式

```bash
# 方式 1：一条命令（简单）
gcc -Wall -Wextra main.c calc.c -o calc

# 方式 2：⭐ 分开编译再链接（真实项目）
gcc -Wall -Wextra -c main.c -o main.o
gcc -Wall -Wextra -c calc.c -o calc.o
gcc main.o calc.o -o calc
```

> ⭐ **方式 2 就是你在编内核时看到的流程**：`CC xxx.o` 然后 `LD vmlinux`。

---

## 六、Makefile

```makefile
CC      = gcc
CFLAGS  = -Wall -Wextra

calc: main.o calc.o
	$(CC) $(CFLAGS) -o calc main.o calc.o

main.o: main.c calc.h
	$(CC) $(CFLAGS) -c main.c

calc.o: calc.c calc.h
	$(CC) $(CFLAGS) -c calc.c

clean:
	rm -f calc *.o

.PHONY: clean
```

### 🔴 最经典的坑：命令行开头必须是 **TAB**

```
calc: main.o calc.o
<tab>$(CC) ...         ← ⭐ 用 TAB 键，不是空格
```

用空格 → `Makefile:6: *** missing separator.  Stop.`

**检查**：`cat -A Makefile | head -10` —— **TAB 显示为 `^I`**。

---

## 七、⭐ `make` 的灵魂：增量编译（实测）

```bash
$ make
make: "calc"已是最新。        ← 什么都没改，什么都不做

$ touch calc.c               ← 只改了 calc.c 的时间戳
$ make
gcc -Wall -Wextra -c calc.c              ← ⭐ 只重编 calc.o
gcc -Wall -Wextra -o calc main.o calc.o  ← 再链接
                                          （main.o 完全没动！）

$ make clean
rm -f calc *.o
$ ls
calc.c  calc.h  main.c  Makefile         ← 只剩源码
```

### 原理

```
calc: main.o calc.o        ← calc 依赖这两个 .o
        ↓
make 比较【目标的修改时间】和【每个依赖的修改时间】
        ↓
依赖比目标新 → 才执行那条规则
        ↓
所以：只改 calc.c → 只有 calc.o 过期 → 只重编它
```

> ⭐ **这就是为什么编内核改一个文件只要几十秒、全编要 16 分钟。**

---

## 八、验收清单

```bash
make                    # 编译通过
./calc                  # 五行输出全对
make                    # 第二次：已是最新
touch calc.c && make    # 只重编 calc.o（观察输出）
make clean              # 清理
ls                      # 只剩 .c .h Makefile
```

---

## 九、本课记住的 5 条

1. **`.h` 只放声明，`.c` 放实现**；自己的头文件用 `"双引号"`
2. **头文件必须加 `#ifndef` 保护**
3. **分开编译（`-c`）再链接** —— 这是大项目的基础
4. **Makefile 的命令行开头必须是 TAB**（`cat -A` 看 `^I`）
5. ⭐ **`make` 只看时间戳 → 增量编译**
