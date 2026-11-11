# 韩顺平《一周学会 Linux》学习计划（Ubuntu 24.04 版）

> 课程：[【小白入门 通俗易懂】韩顺平 一周学会Linux](https://www.bilibili.com/video/BV1Sv411r7vd)
> 规模：**153 集，总时长约 27 小时**（视频里用 CentOS 7.6，你用 Ubuntu 24.04.5 LTS）
> 约定：**以后你问课程里的任何操作，我默认直接给 Ubuntu 写法**，CentOS 原作法只在需要理解原理时说明。
> 资料库总索引：`Linux/README.md`
> 配套文件：命令级对照查 `../02-CentOS转Ubuntu/centos-to-ubuntu-guide.md`，分区练习查 `../03-命令速查/ubuntu-partition-guide.md`，日常命令速查 `../03-命令速查/linux-cli-cheatsheet.md`。

---

## 一、课程结构全景（按集数分段）

| 段落 | 集数 | 时长 | 内容 | 对你的必要性 |
| --- | --- | --- | --- | --- |
| A 环境准备 | 001–011 | 2.9 h | 课程介绍、VMware、CentOS 7.6 安装、三种网络、克隆、快照、迁移、vmtools | ✅ 已完成（换成 Ubuntu 装好的） |
| B 入门基础 | 012–020 | 1.8 h | 目录结构、远程登录、远程传文件、vim、关机重启、登录注销 | ⭐ 必学 |
| C 用户与权限 | 021–027 | 1.3 h | 用户管理、运行级别、找回 root 密码、帮助指令 | ⭐ 必学 |
| D 文件与实用指令 | 028–039 | 2.3 h | 文件目录指令、时间日期、查找、压缩解压 | ⭐⭐ 核心 |
| E 组与权限管理 | 040–051 | 2.2 h | 组、所有者、rwx 权限、chmod/chown、权限实例 | ⭐⭐ 核心 |
| F 任务调度 | 052–057 | 1.1 h | crond、at | ⭐ 必学 |
| G 磁盘 | 058–062 | 1.1 h | 分区机制、增加磁盘、挂载、df/du | ⭐ 必学 |
| H 网络 | 063–067 | 1.1 h | NAT 原理、网络配置、主机名/hosts | ⭐ 必学 |
| I 进程与服务 | 068–081 | 2.5 h | ps、父子进程、kill、pstree、服务管理、top、网络状态 | ⭐⭐ 核心 |
| J 软件包 | 082–090 | 1.2 h | rpm、yum、JDK8、Tomcat8、IDEA、MySQL5.7 | ⚠ 差异最大，有替代方案（见三） |
| K Shell 编程 | 091–107 | 2.4 h | 变量、运算符、判断、循环、函数、定时备份数据库 | ⭐⭐ 核心 |
| L Ubuntu 定制篇 | 108–115 | 1.1 h | Ubuntu 安装、中文支持、root、APT 原理与换源、远程登录集群 | 🔥 你正好用得上，务必看 |
| M 日志管理 | 116–125 | 1.3 h | CentOS8、日志服务、自定义日志、logrotate、内存日志 | ◯ 选学（运维向） |
| N 高级/内核 | 126–132 | 1.3 h | 定制自己的 Linux、读内核源码、内核升级 | △ 可跳过（纯兴趣） |
| O 备份与可视化 | 133–141 | 1.2 h | dump/restore、webmin、宝塔 | ◯ 选学 |
| P 面试题/系统优化 | 142–153 | 2.4 h | 统计访问量、找回 MySQL 密码、tcpdump、权限划分题、启动流程、io 监控、系统优化 | ◯ 选学（面试/调优再回来） |

**结论**：真正要跟的是 **B–K + L**，合计约 **17 小时**；M–P 按需回看。

---

## 二、21 天日程表（每天 1–1.5 h，含练习）

> 节奏：**看 1 集 → 立刻在你自己的 Ubuntu 里敲一遍 → 再下一集**。只看不敲等于没学。
> 每集结束后，把用到的命令记一行到你的速查表里。

| 天 | 看哪几集 | 时长 | 主题 | Ubuntu 差异要点 |
| --- | --- | --- | --- | --- |
| 已完成 | 001–011 | — | 装系统、快照、vmtools | 你已装好 Ubuntu + open-vm-tools-desktop，等价于 vmtools |
| 1 | 012–015 | 56 min | 目录结构、远程登录、远程传文件 | SSH 服务名 `ssh`；用 `scp`/`sftp`/`rsync` 同理 |
| 2 | 016–020 | 52 min | vim 三件套、关机重启 | 完全一样：`vim`、`shutdown`、`reboot`、`logout` |
| 3 | 021–023 | 40 min | 用户管理 1–3 | `useradd -m`；管理员组 `wheel` → **`sudo`** |
| 4 | 024–027 | 38 min | 用户管理 4、运行级别、找回密码、帮助 | 运行级别 → **systemd target**；root 密码 → 用 `sudo`，没有 root 登录 |
| 5 | 028–031 | 66 min | 文件目录指令 1–4 | 完全一样 |
| 6 | 032–035 | 55 min | 文件目录 5–6、时间日期、查找 1 | 完全一样（`find`/`locate`/`which`） |
| 7 | 036–039 | 35 min | 查找 2、压缩解压、小结 | 一样（`tar`/`gzip`/`zip`/`unzip`） |
| 8 | 040–043 | 25 min | 组、所有者、所在组 | 一样，只把 `wheel` 换 `sudo` |
| 9 | 044–047 | 41 min | rwx 权限、chmod、chown | 完全一样 |
| 10 | 048–051 | 64 min | 权限管理 4 个实例 | 完全一样（这集含金量最高，一定要跟着做） |
| 11 | 052–057 | 64 min | crond、at | 一样；`systemctl status cron`（CentOS 是 `crond`） |
| 12 | 058–062 | 65 min | 磁盘分区、加盘、挂载、df/du | 一样，但**需要第二块盘**（见四） |
| 13 | 063–067 | 65 min | NAT 原理、网络配置、hosts | 网卡配置 `/etc/sysconfig/network-scripts/` → **`/etc/netplan/*.yaml`** |
| 14 | 068–072 | 41 min | 进程、ps、父子进程、kill、pstree | 一样（`top` 可换 `htop`） |
| 15 | 073–077 | 56 min | 服务管理 1–5 | `systemctl` 通用；`chkconfig`/`service` → 一律 `systemctl` |
| 16 | 078–081 | 45 min | top 动态监控、ss 网络状态 | `netstat` → **`ss -tlnp`**（`netstat` 需装 `net-tools`） |
| 17 | 082–085 | 26 min | rpm、yum、包管理小结 | **重点看替代方案**：rpm→dpkg，yum→apt（见三） |
| 18 | 091–096 | 56 min | Shell 入门、变量、环境变量、位置/预定义变量、运算符 | 完全一样（`#!/bin/bash`） |
| 19 | 097–104 | 50 min | 条件判断、分支、case、for/while、read、函数 | 完全一样 |
| 20 | 105–107 | 37 min | 定时备份数据库实战、Shell 梳理 | 一样；备份对象换成 MariaDB/MySQL 同理 |
| 21 | 108–115 + 复习 | 65 min | **Ubuntu 定制篇（正对你）**、APT 原理与换源 | 这集讲的换源你已经做完了，跟着对一遍加深理解 |

**加速版**：时间紧就按「一天两天的量」合并，7 天冲完 B–K；把 058–062（磁盘）和 091–107（Shell）单独留出整天。

**加长版**：想走运维方向，21 天后再补 M（日志 116–125）→ O（备份/可视化 133–141）→ P（142–153 面试题）。

---

## 三、第 82–90 集怎么跟（课程里最"CentOS 味"的部分）

视频里：`rpm -ivh`、`yum install`、装 JDK8/Tomcat8/IDEA/MySQL5.7。
你 Ubuntu 上有两条路：

**路线 A（推荐，最省事）**：跳过 082–085 的实操，只看原理，把命令换成

```bash
sudo apt update                       # 相当于 yum makecache
sudo apt install -y 包名               # 相当于 yum install -y 包名
sudo apt remove 包名                   # 相当于 yum remove
dpkg -l                               # 相当于 rpm -qa
dpkg -S /usr/bin/vim                  # 相当于 rpm -qf
sudo dpkg -i xxx.deb                  # 相当于 rpm -ivh xxx.rpm
```

然后直接看 **108–115 集**——那几集韩顺平讲的就是 Ubuntu + APT，正好接上你现在的系统。

**路线 B（想亲眼看 yum）**：用 Docker 跑一个 CentOS 7 容器练手，不影响你的 Ubuntu：

```bash
sudo apt install -y docker.io
sudo docker run -it --rm centos:7 bash
# 容器里：sed -i 's|mirror.centos.org|vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo
# 然后 yum install -y httpd 随便玩，退出即销毁
```

JDK / Tomcat / MySQL 在 Ubuntu 上的对应装法（到时候我再帮你逐条对）：

| 视频 | Ubuntu 做法 |
| --- | --- |
| 装 JDK8 | `sudo apt install -y openjdk-8-jdk`（或 17/21） |
| 装 Tomcat8 | `sudo apt install -y tomcat10`（包名随版本，或官网下载 tar.gz 解压） |
| 装 IDEA | 官网下载 tar.gz 解压，`bin/idea.sh` 启动 |
| 装 MySQL5.7 | `sudo apt install -y mysql-server`（24.04 是 8.0；要 5.7 得用官方仓库或 Docker） |

---

## 四、两处"必须提前准备"的东西

1. **第 058–059 集要"增加一块硬盘"**
   你之前不想加第二块 20GB 练习盘，所以这两集只能看不能做。两种选择：
   - 想做：虚拟机**关机**后 → VMware 菜单「虚拟机 → 设置 → 添加 → 硬盘 → SCSI → 创建新虚拟磁盘 → 20GB」→ 开机，然后按 `../03-命令速查/ubuntu-partition-guide.md` 练 `fdisk`/`mkfs`/`mount`/`fstab`。
   - 不想做：先看视频理解原理，等学到 Shell 或需要练挂载时再加。

2. **第 065 集改静态 IP 有风险**
   你现在是 NAT + DHCP，改错会直接断网（连不上源、装不了软件）。建议：
   - 先用 `ip addr` 把当前 IP 记下来；
   - 真要改，改前 **拍一个 VMware 快照**（虚拟机 → 快照 → 拍摄快照），改坏了一键回滚。

---

## 五、每学完一段的自测清单（能不看笔记做出来才算过）

- [ ] 不看讲义，说出 `/etc`、`/var`、`/home`、`/usr`、`/tmp` 各放什么
- [ ] 用 `vim` 新建文件、插入、保存退出、查找替换、跳行
- [ ] 建一个用户 `tom`，加入 `sudo` 组，切换过去验证能 `sudo -i`
- [ ] 把某目录权限改成 750，属主改 `tom:tom`，解释 `rwxr-x---` 含义
- [ ] 写一个 crontab：每天 2:30 把 `/var/log/syslog` 备份到 `/backup`
- [ ] 用 `df -h`、`du -sh` 找出谁把磁盘吃满了
- [ ] 用 `ps aux | grep` 找到进程，用 `kill -9` 干掉
- [ ] 用 `systemctl` 启动/停止/开机自启 ssh
- [ ] 写 Shell 脚本：接收两个数字参数，判断大小并输出
- [ ] 写 Shell 脚本：`for` 循环把 `/etc` 下的 `.conf` 文件列表输出

---

## 六、我这边怎么配合你

- **默认 Ubuntu**：你问的任何操作，我直接给 Ubuntu 24.04 命令；只有理解原理需要时才提 CentOS 原写法。
- **报集数就行**：说"我在看第 45 集"或直接贴视频里的命令，我给你 Ubuntu 等价命令 + 差异解释。
- **报错就贴**：把终端里的报错整段复制给我（不要截图里的中文翻译），我帮你看。
- **练习环境**：想练"搞坏了再修"，喊我拍快照；练完一键回滚。
- **重要系统改动前**：我会先提醒你拍快照。

---

## 七、你现在的环境（起点）

| 项 | 值 |
| --- | --- |
| 虚拟机 | VMware Workstation 17.5.2，8 GB 内存 / 4 核 / 60 GB |
| 系统 | Ubuntu 24.04.5 LTS（Ubuntu 版 `cxh`，主机名 `cxh-VMware20-1`） |
| 分区 | `/dev/sda1` 1 GB vfat → `/boot/efi`；`/dev/sda2` 59 GB ext4 → `/`；swap 2 GB（`/swap.img`） |
| 软件源 | 已切清华 TUNA 镜像 |
| 网络 | NAT（VMnet8，网关 192.168.139.2） |
| 已装/待装 | `setup.sh` 里那批：vim、tmux、git、htop、tree、net-tools、openssh-server、open-vm-tools-desktop 等 |
