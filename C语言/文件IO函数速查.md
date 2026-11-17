# 文件 IO 函数速查（背不下来就看这张）

> **记忆锚点**：**`f` 开头 = file（文件版）**。
> `printf`/`scanf`/`gets`/`putc` 的**文件版**就是 `fprintf`/`fscanf`/`fgets`/`fputc`。

---

## 零、核心概念：`FILE *` 是什么

```c
FILE *fp = fopen("a.txt", "r");   /* 打开文件 → 得到一个"遥控器" */
        ↓
用 fp 操作这个文件（读/写）
        ↓
fclose(fp);                        /* 关掉 */
```

**`FILE *` 就是"文件的句柄"** —— 你看不见文件内部，只能拿着这个句柄让它干活。

### 三个"天生就有"的文件

| 句柄 | 是什么 |
| --- | --- |
| `stdin` | 键盘输入 |
| `stdout` | 屏幕（正常输出） |
| `stderr` | 屏幕（错误输出，可单独重定向） |

⭐ **关键等价关系**：
```c
printf("hi\n");              ≡   fprintf(stdout, "hi\n");
scanf("%d", &x);             ≡   fscanf(stdin, "%d", &x);
```

---

## 一、总表（按用途）

| 用途 | 函数 | 一句话 |
| --- | --- | --- |
| **打开** | `fopen(路径, 模式)` | 返回 `FILE*`，失败返回 `NULL` |
| **关闭** | `fclose(fp)` | **必须调用**，否则数据可能没写盘 |
| **写文本** | `fprintf(fp, fmt, ...)` | = `printf` + 目的地 |
| **写字符串** | `fputs(s, fp)` | 写一个字符串（不加换行） |
| **写字符** | `fputc(c, fp)` | 写一个字符 |
| **读一行** | `fgets(buf, size, fp)` | ⭐ 最常用、最安全 |
| **读字符** | `fgetc(fp)` | 返回 `int`（要能装 EOF） |
| **读格式化** | `fscanf(fp, fmt, ...)` | = `scanf` + 来源（**少用**，易卡住） |
| **读二进制块** | `fread(buf, 每块, 块数, fp)` | 返回实际读到几块 |
| **写二进制块** | `fwrite(buf, 每块, 块数, fp)` | 返回实际写了几块 |
| **报错** | `perror(前缀)` | 打印 `前缀: 系统错误原因` |
| **判断结尾** | `feof(fp)` | 读到末尾后为真 |

---

## 二、参数顺序（⭐ 最容易记混的地方）

| 规律 | 函数 |
| --- | --- |
| **`fp` 在最前面**（= printf/scanf 前面加 fp） | `fprintf(fp, fmt, ...)`、`fscanf(fp, fmt, ...)` |
| **`fp` 在最后面** | `fputs(s, fp)`、`fputc(c, fp)`、`fgets(buf, n, fp)`、`fread(...)`、`fwrite(...)` |
| **只有一个参数** | `fclose(fp)`、`fgetc(fp)`、`feof(fp)` |

> 🔑 **口诀**：**`fprintf`/`fscanf` 是"前面加"，其余是"后面加"。**

---

## 三、逐个详解

### `fopen` —— 打开

```c
FILE *fopen(const char *路径, const char *模式);
```

| 模式 | 含义 |
| --- | --- |
| `"r"` | 读（**文件必须存在**） |
| `"w"` | 写（**存在则清空**！不存在则创建） |
| `"a"` | 追加（写在末尾） |
| `"rb"` / `"wb"` | 二进制读/写（不转换换行） |

**必须检查**：
```c
FILE *fp = fopen("a.txt", "r");
if (fp == NULL) {
    perror("fopen");        /* → "fopen: No such file or directory" */
    return 1;
}
```

### `fprintf` —— 写格式化文本

```c
int fprintf(FILE *fp, const char *格式, ...);
```

```c
fprintf(fp, "line %d\n", 1);      /* 和 printf 用法完全一样，只是多了 fp */
```

### `fgets` —— 读一行（⭐ 主力）

```c
char *fgets(char *buf, int size, FILE *fp);
```

| 行为 | 说明 |
| --- | --- |
| 最多读 `size - 1` 个字符 | 留 1 个位置给 `'\0'` |
| 遇到 `'\n'` 就停 | **而且把 `'\n'` 也存进去** |
| 返回 | 成功 → `buf`；到末尾/出错 → **`NULL`** |

**标准循环**：
```c
char buf[256];
while (fgets(buf, sizeof(buf), fp) != NULL) {
    printf("%s", buf);      /* buf 里已含换行，不用再 printf("\n") */
}
```

### `fgetc` —— 逐字符读

```c
int fgetc(FILE *fp);        /* ⚠️ 返回 int，不是 char！ */
```

```c
int c;
while ((c = fgetc(fp)) != EOF) {     /* EOF = -1 */
    /* 处理字节 c */
}
```

> ⚠️ **为什么返回 `int`**：要能同时表示 0~255 的字节和 `-1`（EOF）。用 `char` 会装不下。

### `fread` / `fwrite` —— 二进制块

```c
size_t fread (void *buf, size_t 每块大小, size_t 块数, FILE *fp);
size_t fwrite(const void *buf, size_t 每块大小, size_t 块数, FILE *fp);
```

| 写法 | 含义 |
| --- | --- |
| `fread(buf, 1, 1024, fp)` | 读 **1024 个字节**（每块 1 字节 × 1024） |
| `fread(buf, sizeof(int), 10, fp)` | 读 **10 个 int** |
| 返回值 | **实际读到的块数**（到末尾会小于请求数） |

**标准拷贝循环**：
```c
unsigned char buf[4096];
size_t n;
while ((n = fread(buf, 1, sizeof(buf), fp_in)) > 0) {
    fwrite(buf, 1, n, fp_out);
}
```

### `perror` —— 打印错误

```c
void perror(const char *前缀);
```

```c
fopen("不存在.txt", "r");
perror("fopen");       /* 输出：fopen: No such file or directory */
```

**原理**：它读全局变量 `errno`（系统调用的错误码），翻译成文字。

### `EOF` 和 `feof`

| | 说明 |
| --- | --- |
| `EOF` | 常量 **-1**，`fgetc` 读完时返回它 |
| `feof(fp)` | 判断"是否已到达末尾" |

> ⚠️ **经典错误**：`while (!feof(fp)) { fgets(...); }` —— **会多循环一次**。
> **正确做法**：直接判断函数返回值（`while (fgets(...) != NULL)`）。

---

## 四、最小完整示例（写 + 读）

```c
#include <stdio.h>

int main(void)
{
    /* 写 */
    FILE *fp = fopen("a.txt", "w");
    if (!fp) { perror("fopen"); return 1; }
    fprintf(fp, "hello\n");
    fputs("world\n", fp);
    fclose(fp);

    /* 读 */
    fp = fopen("a.txt", "r");
    if (!fp) { perror("fopen"); return 1; }

    char buf[128];
    while (fgets(buf, sizeof(buf), fp) != NULL) {
        printf("读到: %s", buf);
    }
    fclose(fp);

    return 0;
}
```

---

## 五、五条铁律

1. **`fopen` 之后必须检查 `NULL`**
2. **用完必须 `fclose`**（否则缓冲数据可能丢失）
3. **`fgetc`/`fread` 的返回值要按 `int`/`size_t` 接**，别用 `char`
4. **错误信息走 `stderr`，正常结果走 `stdout`**
5. **`"w"` 会清空文件** —— 想追加用 `"a"`
