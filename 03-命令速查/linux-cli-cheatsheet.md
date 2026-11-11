# Linux 命令行入门小抄（配合这台 Ubuntu 24.04 虚拟机）

## 一、先记住 6 个命令，能覆盖大半日常

| 命令 | 作用 | 例子 |
| --- | --- | --- |
| `pwd` | 我现在在哪个目录 | `pwd` |
| `ls` | 看目录里有什么 | `ls -lh`（带大小）、`ls -a`（含隐藏文件） |
| `cd` | 切换目录 | `cd /etc`、`cd ..`（上一层）、`cd ~`（回家目录） |
| `cat` | 看文件内容 | `cat /etc/hostname` |
| `mkdir` / `rmdir` | 建目录 / 删空目录 | `mkdir -p ~/lab/a/b` |
| `rm` | 删文件（不可恢复！先想清楚） | `rm 文件`、`rm -r 目录` |

## 二、新手最容易踩的坑

- Linux 区分大小写：`File` 和 `file` 是两个东西。
- 路径 `/` 是根，`~` 是你的家目录（`/home/你的用户名`），`.` 是当前目录，`..` 是上一层。
- 命令前加 `sudo` 才有管理员权限；会要你输密码（输入时不显示，正常）。
- `rm -rf` 是危险命令，别手抖。
- 任何命令卡住了：`Ctrl + C` 中断。
- 输出太长刷屏：`命令 | less`（按 `q` 退出）。

## 三、学文件与权限

```bash
ls -l            # 看权限：-rw-r--r-- 用户/组/其他人
chmod +x 脚本.sh  # 加可执行权限
chown 用户 文件    # 改属主（要 sudo）
df -h            # 看磁盘
du -sh 目录       # 看目录占用
free -h          # 看内存
```

## 四、学文本处理（命令行最有用的部分）

```bash
cat 文件 | grep 关键词     # 过滤含关键词的行
grep -rn "关键词" 目录      # 递归搜索
head -n 20 文件            # 前 20 行
tail -f 日志               # 实时跟日志（Ctrl+C 退出）
awk '{print $1}' 文件      # 取第 1 列
sed 's/旧/新/g' 文件       # 替换
```

## 五、学进程与服务

```bash
ps aux | grep 进程名   # 找进程
top / htop            # 看资源占用（htop 里按 q 退出）
kill -9 PID           # 强杀进程
systemctl status ssh  # 看服务状态
sudo systemctl restart ssh
```

## 六、学软件安装与网络

```bash
sudo apt update          # 更新软件列表
sudo apt install 包名    # 装软件
apt search 关键词        # 搜软件
ip -4 addr               # 看 IP
ping -c 4 baidu.com      # 测网络
curl -I https://www.baidu.com
```

## 七、学 shell 小技巧

```bash
命令1 && 命令2      # 前一个成功才执行后一个
命令 > 文件         # 输出写进文件（覆盖）
命令 >> 文件        # 追加
命令 2>&1 | less    # 错误和正常输出一起看
Ctrl+R             # 搜索历史命令
!!                 # 重复上一条命令
Tab                # 自动补全（多用！）
```

## 八、建议练习路径

1. 家目录建 `~/lab`，在里面练 `ls/cd/mkdir/touch/rm`。
2. 用 `cat`、`echo`、`grep`、`awk`、`sed` 对文本文件做增删改查。
3. 用 `chmod` 写一个 `hello.sh` 脚本，`./hello.sh` 跑起来。
4. 用 `apt` 装 `tmux`，在 tmux 里练多窗口。
5. 每天记 3 个命令，一周就有手感了。

## 九、Windows 上更舒服的练法（可选）

安装完成后在 Windows PowerShell 里：

```powershell
ssh 你的用户名@虚拟机IP地址
```

就能用 Windows 终端直接练 Linux 命令，复制粘贴都方便（IP 用虚拟机里 `ip -4 addr` 查）。
