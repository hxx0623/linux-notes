# Git 基础与配置（从零开始）

> 记录于 2026-11-11。所有命令都在 **Windows PowerShell 5.1 + Git 2.56.0.windows.4** 上实测过。

---

## 一、核心心智模型：三个区域

```
   工作区                暂存区                 仓库
（你看到的文件）      （staging / index）    （.git 里的历史）
      │                    │                     │
      │─── git add ───────▶│                     │
      │                    │─── git commit ─────▶│
      │                                          │
      └── 你在这里改文件                          └── 每张快照永久保存
```

**拍照比喻**（能吃透大半 Git）：

| 比喻 | Git |
| --- | --- |
| 房间里的东西 | **工作区** —— 你看到的文件 |
| 把要拍的人叫到镜头前 | **`git add`** —— 挑选"这次记录哪些改动" |
| 按下快门 | **`git commit`** —— 生成一张**不可变**的快照 |
| 相册 | **仓库**（`.git` 目录） |

**为什么要有暂存区**：让你能**只提交一部分改动**（改了两个文件、只提交一个）。没有它做不到。

### `.git` 目录 = 仓库本体

- 装着所有历史（`objects/`）、当前位置（`HEAD`）、配置（`config`）
- **删了它 → 文件还在，但历史全没了，这文件夹不再是仓库**
- 备份/移动仓库时 **`.git` 必须一起带走**

---

## 二、核心命令表

### 起步

| 命令 | 作用 |
| --- | --- |
| `git init` | 把当前目录变成仓库 |
| `git clone <URL>` | 把远程仓库**完整复制**到本地（含历史） |

### 日常三件套

| 命令 | 作用 |
| --- | --- |
| `git status` | **看现状**（最重要，每次先敲它） |
| `git add <文件>` / `git add .` | 放进暂存区（`.` = 当前目录全部改动） |
| `git commit -m "说明"` | 拍快照 |

### 看

| 命令 | 作用 |
| --- | --- |
| `git log --oneline` | 一行一条历史 |
| `git log --stat` | 加"改了哪些文件、几行" |
| `git log --oneline --graph` | 画线（有分支时才看得出价值） |
| **`git show <编号>`** | **看某一次提交改了什么**（编号省略 = `HEAD`） |
| `git show --shortstat HEAD` | 只输出"N files changed, M insertions" |
| `git diff` | 工作区 **vs** 暂存区 |
| **`git diff HEAD`** | 工作区 **vs** 最新提交（不管有没有 add） |

### 远程

| 命令 | 作用 |
| --- | --- |
| `git remote add origin <URL>` | 添加远程，命名为 `origin` |
| `git remote -v` | 看远程地址（fetch/push 各一行，正常） |
| `git remote set-url origin <新URL>` | **改**远程地址 |
| **`git push -u origin main`** | 第一次推；`-u` 绑定上游，**以后只需 `git push`** |
| `git pull` | 把远程的新提交拉下来 |

### `git status` 的三句关键话

| 输出 | 含义 | 该做什么 |
| --- | --- | --- |
| `Your branch is up to date with 'origin/main'` | 本地=远程 | 无事 |
| `ahead of 'origin/main' by N commits` | 本地有提交没推 | `git push` |
| `behind 'origin/main' by N commits` | 远程有新的没拉 | `git pull` |

---

## 三、撤销四场景（**最容易搞混，必须记**）

| 你想撤回什么 | 命令 | 会丢东西吗 |
| --- | --- | --- |
| **工作区的改动**（改了还没 add） | `git restore <文件>` | 🔴 **会丢**（改动消失） |
| **暂存状态**（add 了还没 commit） | `git restore --staged <文件>` | ✅ 不丢（内容不变，只是退出候选名单） |
| 最近一次提交（保留改动） | `git reset --soft HEAD~1` | ✅ 保留 |
| 彻底回到某次提交 | `git reset --hard <编号>` | 🔴🔴 **会丢，危险** |

**记法**：`--staged` 说的是"**我只动暂存区**"。

> 旧教程里的 `git checkout -- <文件>` = 现在的 `git restore <文件>`。

**`HEAD` 的用法**：`HEAD` = 最新提交；`HEAD~1` = 往前 1 次；`HEAD~2` = 往前 2 次。

---

## 四、日常流程（养成肌肉记忆）

```powershell
# ① 开工先看现状
git status

# ② 改文件……然后
git diff                    # 看改了什么（确认没改坏）

# ③ 挑要提交的
git add <文件>              # 或 git add .

# ④ 提交
git commit -m "说明这次做了什么"

# ⑤ 推上去
git push

# ⑥ 再确认
git status
```

**关键认知**：**`git commit` 只提交"暂存区里的东西"**。没 `add` 的文件不会进去。

---

## 五、这台电脑的实际配置（2026-11-11 配好）

### 5.1 身份

```powershell
git config --global user.name  "HXX0623"
git config --global user.email "211278675+hxx0623@users.noreply.github.com"
```

> ⚠️ **邮箱必须用 GitHub 给的 noreply 地址**（不是真实邮箱）。
> 原因：① 公开仓库里每次提交都会写进邮箱，真实 QQ 邮箱会被爬 ② noreply 照样能把提交归属到你账号（绿格子会亮），前提是 GitHub 设置里勾了 **"Keep my email addresses private"**。

### 5.2 其他设置

| 配置 | 值 | 为什么 |
| --- | --- | --- |
| `init.defaultBranch` | `main` | GitHub 默认叫 main，统一省事 |
| **`core.quotepath`** | **`false`** | ⭐ **中文文件名不再显示成 `\345\255\246` 这种八进制转义** |
| `core.autocrlf` | `true`（Git for Windows 默认） | 仓库里存 LF，检出到 Windows 变 CRLF |

### 5.3 ⭐ SSH：走 443 端口（22 被网络挡住）

**问题**：`ssh -T git@github.com` 报 `Connection closed by 20.205.243.166 port 22` 或 `Connection timed out during banner exchange` —— 22 端口被挡。

**解法**：`C:\Users\cxh\.ssh\config` 里写

```
Host github.com
    HostName ssh.github.com
    Port 443
    User git
```

**作用**：连 `github.com` 时**实际走 `ssh.github.com` 的 443 端口**（和网页同端口）。**命令照旧写 `github.com`，不用改习惯**；也不影响连虚拟机的 SSH。

**验证**：`ssh -T git@github.com` → `Hi hxx0623! You've successfully authenticated`（后面那句"不提供 shell 访问"是正常的）

**首次连接会问指纹**，回答 `yes`。GitHub 的 ED25519 指纹：`SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`

### 5.4 环境事实（实测）

| 项 | 值 |
| --- | --- |
| Git 版本 | `2.56.0.windows.4` |
| OpenSSH | `OpenSSH_for_Windows_9.5p1` |
| 密钥 | `~/.ssh/id_ed25519`（**和连虚拟机共用同一把**，公钥已加到 GitHub） |
| 到 github.com HTTPS | HTTP 200，但**耗时约 10.7 秒**（慢） |
| **上传速度** | **约 26 KiB/s**（7.7 MB 传了 4–5 分钟）⚠️ 大仓库要有耐心 |

> **建议**：以后**别往仓库塞大文件**（视频、大图片、数据集），26 KiB/s 会让人崩溃。GitHub 建议仓库 < 1 GB、单文件 < 100 MB。

---

## 六、中文与编码（PowerShell 5.1 的坑）

| 场景 | 结论 |
| --- | --- |
| **提交说明**（`-m "中文"`） | ✅ **完全可以写中文**，GitHub 显示正常（已实测） |
| **文件内容**里的中文 | ⚠️ PowerShell 5.1 的 `-Encoding utf8` 会**加 BOM**（一个隐藏标记），推上去可能显示乱码 |
| 安全写法 | 中文内容用 `[IO.File]::WriteAllText($路径, $内容, (New-Object System.Text.UTF8Encoding($false)))`（**无 BOM**） |
| 纯 ASCII 内容 | `Set-Content -Encoding ascii` 最安全 |
| **CRLF 警告** | `warning: LF will be replaced by CRLF` —— **正常**，是 `autocrlf` 在干活，不用处理 |

> 📌 **`.gitignore` 文件本身要小心 BOM**：如果第一行带 BOM，Git 可能认不出那条规则。

---

## 七、密钥安全（血的教训级）

| 东西 | 能不能上传/粘贴 |
| --- | --- |
| `id_ed25519.pub`（**公钥**） | ✅ 可以，就是要贴到 GitHub |
| **`id_ed25519`（私钥，没有 `.pub`）** | 🔴 **绝对不能**给任何人、任何网站 |
| 密码 / token / API key | 🔴 绝不能进仓库 |

**规则**：**只推你愿意贴在公告栏上的东西。**

> GitHub 会自动扫描并吊销泄露到公开仓库的密钥 —— 但那是在**已经泄露之后**，别指望它兜底。
