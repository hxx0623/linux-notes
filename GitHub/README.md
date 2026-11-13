# GitHub 学习资料库

> 建立于 **2026-11-11**（从零开始学 GitHub 的当天）。**以后所有与 Git/GitHub 相关的新文件都放这里，并登记到本文索引。**

---

## 零、上下文丢了先看这里

如果对话被压缩、或换会话，读这 5 条就能接着干：

1. **账号**：GitHub 用户名 **`HXX0623`**（URL 规范写法小写 `hxx0623`）
2. **两个已建仓库**：`gitlearn`（练习用）、`linux-notes`（Linux 学习资料库，真东西）
3. **本地路径**：练习库 `C:\Users\cxh\gitlearn`；笔记库 `C:\Users\cxh\deepseek harness\Linux`
4. **认证**：SSH 密钥 `~/.ssh/id_ed25519`（**和连虚拟机共用同一把**）；**22 端口被网络挡，走 `ssh.github.com:443`**，配置在 `~/.ssh/config`
5. **讲解约定**：学习者英文较弱，**Git 输出保持英文，但每条都要用中文逐句标注**（见 `Git基础与配置.md`）

---

## 一、目录结构

```
GitHub/
├── README.md              ← 本文件（索引）
├── Git基础与配置.md        三个区域模型、核心命令、撤销场景、全部配置记录
└── 问题速查.md            现象 → 原因 → 解决（遇到报错先查这里）
```

---

## 二、文件索引（按"我要干什么"查）

| 我想…… | 打开 |
| --- | --- |
| 忘了 Git 的"三个区域"是什么意思 | [Git基础与配置.md](Git基础与配置.md) §一 |
| 忘了某条命令怎么用（add/commit/push…） | [Git基础与配置.md](Git基础与配置.md) §二 |
| **改坏了想撤回，该用哪条命令** | [Git基础与配置.md](Git基础与配置.md) §三（撤销四场景表） |
| 每天的正常操作流程是什么 | [Git基础与配置.md](Git基础与配置.md) §四 |
| 这台电脑上 Git/SSH 到底怎么配的 | [Git基础与配置.md](Git基础与配置.md) §五 |
| **报错了，看不懂英文** | [问题速查.md](问题速查.md) |

---

## 三、两个仓库的实际地址

| 仓库 | URL（SSH） | 本地路径 | 用途 |
| --- | --- | --- | --- |
| `gitlearn` | `git@github.com:hxx0623/gitlearn.git` | `C:\Users\cxh\gitlearn` | 第一个练习仓库（3+ 次提交，内容无意义） |
| **`linux-notes`** | `git@github.com:hxx0623/linux-notes.git` | `C:\Users\cxh\deepseek harness\Linux` | ⭐ **韩顺平 Linux 全部学习资料**（217 文件 / 13743 行 / 7.7 MB） |

> ⚠️ **`linux-notes` 是公开仓库**。所以：
> - 笔记里**绝不能出现明文密码、私钥、token**（截至 2026-11-11 已扫描确认干净）
> - 提交作者邮箱用的是 **noreply 地址**，QQ 号不会泄露

---

## 四、约定

1. **新文件建完立刻登记到本文第二节索引表。**
2. **Git 命令的输出保持英文**（便于搜索报错），但**助教必须逐句中文标注**。
3. **文件内容写中文要小心编码**（PowerShell 5.1 默认带 BOM）—— 详见 `Git基础与配置.md` §六。
4. **提交说明可以写中文**（已验证显示正常）。

---

## 五、学习记录（时间线）

### 2026-11-11：从零到把 217 个文件推上 GitHub（约 2.5 小时）

| 阶段 | 做成的事 |
| --- | --- |
| 体检 | 发现 Windows 没装 Git；**22 端口被挡**、HTTPS 能通但慢（10.7s） |
| 装环境 | `winget` 装 Git for Windows **2.56.0**；注册 GitHub 账号 **HXX0623** |
| 认证 | 复用 `~/.ssh/id_ed25519`；配 **noreply 邮箱**；**SSH 走 443 绕开 22 端口封锁** |
| 本地 Git | 练习库 `gitlearn`：3 次提交，跑通 init/add/commit/log/show/diff/restore |
| 真实项目 | **`linux-notes`**：217 文件 / 13743 行 / 7.7 MB，一次推送成功 |

**踩到并解决的坑**（详见 `问题速查.md`）：22 端口被挡 · 仓库大小写（`This repository moved`）· 中文路径转义（`core.quotepath`）· `git status` 折叠目录（`-u`）· `Measure-Object -Line` 含表头 · PowerShell BOM。

**下一步计划（学习者定的顺序）**：
- **A. 日常练习**：以后更新笔记都走 `add → commit → push`，练成肌肉记忆
- **B. 美化 README**：给 `linux-notes` 加开源项目式的开头介绍 + 目录跳转
- **C. GitHub Pages**：把这套笔记变成一个能访问的网站（需先做 B）
