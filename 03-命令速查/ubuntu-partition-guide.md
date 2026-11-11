# Ubuntu 24.04 里怎么练「分区」（对照 CentOS 7.6 课程）

> 结论先说：**不用重装也能把课程里的分区实验完整做一遍**——给虚拟机加一块空盘，用 `fdisk` 分区、`mkfs` 格式化、`mount` 挂载。
> 如果你就是想「重装一次并手动分区」，下面也有对照步骤。

---

## 一、先弄清课程在做什么

CentOS 7.6 装机实验常见的分区方案：

| 分区 | 大小 | 挂载点 | 文件系统 |
| --- | --- | --- | --- |
| /boot | 200MB ~ 1GB | /boot | ext4 / xfs |
| swap | 2GB（或等于内存） | 无挂载点 | swap |
| / | 20GB 左右 | / | ext4 / xfs |
| 剩余空间 | 剩下全部 | /data（课程自己编的） | ext4 / xfs |

你要练的是三件事，跟发行版无关：**分区 → 格式化 → 挂载（写进 fstab 开机自动挂）**。

---

## 二、方法 A（推荐）：加一块空盘，命令行练一遍

### 1. 在 VMware 里加盘

关机状态下：`虚拟机(M)` → `设置` → `添加` → `硬盘` → 下一步 → `SCSI` → `创建新虚拟磁盘` → 容量填 `20` GB → 下一步 → 完成。

加完开机，进系统打开终端。

### 2. 认盘

```bash
lsblk            # 原来的系统盘 = /dev/sda，新加的 = /dev/sdb
sudo fdisk -l /dev/sdb
```

### 3. 分区（fdisk 交互按键）

```bash
sudo fdisk /dev/sdb
```

进去后依次按：

| 按键 | 含义 |
| --- | --- |
| `n` → `p` → `1` → 回车 → `+1G` | 建第 1 个分区 1GB（给 /boot 练） |
| `n` → `p` → `2` → 回车 → `+2G` | 建第 2 个分区 2GB（给 swap） |
| `n` → `p` → `3` → 回车 → 回车 | 建第 3 个分区，吃掉剩余空间（给 /data） |
| `p` | 打印看看分区表对不对 |
| `w` | 保存退出（不保存就按 `q`） |

> 如果系统里是新式 GPT 看到 `gdisk` 提示，也可以直接用 `sudo parted /dev/sdb mklabel gpt` 先建表再分。

### 4. 格式化 + 启用

```bash
sudo partprobe /dev/sdb          # 让内核重新读分区表

sudo mkfs.ext4 /dev/sdb1         # 第一个分区 → ext4（课程里给 /boot）
sudo mkswap  /dev/sdb2           # 第二个分区 → swap
sudo swapon  /dev/sdb2           # 立刻启用 swap
sudo mkfs.ext4 /dev/sdb3         # 第三个分区 → ext4（课程里给 /data）

free -h                          # 能看到 swap 变大了
```

### 5. 挂载 + 开机自动挂载

```bash
sudo mkdir -p /data /boot2
sudo mount /dev/sdb3 /data
sudo mount /dev/sdb1 /boot2
df -h                            # 确认挂上了

sudo blkid /dev/sdb1 /dev/sdb3   # 记下两个 UUID
```

编辑 `/etc/fstab`（`sudo vim /etc/fstab`），末尾加两行（UUID 换成你 `blkid` 看到的）：

```
UUID=上面查到的sdb1的UUID   /boot2   ext4  defaults  0 2
UUID=上面查到的sdb3的UUID   /data    ext4  defaults  0 2
```

检查有没有写错（很重要，写错可能导致开不了机）：

```bash
sudo mount -a     # 没报错就是对的
df -h             # 再确认一次
```

### 6. 清理（练完想还原）

```bash
sudo umount /data /boot2
sudo swapoff /dev/sdb2
# 删掉 /etc/fstab 里加的两行
```

---

## 三、方法 B：重装一次，走安装器的「手动分区」

Ubuntu 24.04 安装器里对应 CentOS「我要配置分区」的地方叫 **手动安装（Manual installation）**。

流程：Live 桌面双击 Install Ubuntu → 语言 → 键盘 → 网络 → 安装类型选 **手动安装** → 选中 60GB 磁盘 → 点「新建分区表」→ 挨个建：

| 要建的分区 | 大小 | 挂载点 | 格式 | 说明 |
| --- | --- | --- | --- | --- |
| EFI 系统分区 | 1GB | /boot/efi | FAT32 | **必须有**，Ubuntu 用 EFI 引导（CentOS 课程的 BIOS+MBR 那套在这里不适用） |
| /boot | 1GB | /boot | ext4 | 可选，课程里有就建 |
| swap | 2GB | 不挂载 | swap | 可从下拉里选 swap |
| / | 20GB | / | ext4 | |
| /data | 剩余 | /data | ext4 | 课程自己编的挂载点，可以照做 |

然后「下一步」→ 建账户 → 时区 → 安装。

> 注意：Ubuntu 24.04 默认不建 swap 分区，而是用一个 2GB 的 `/swap.img` 文件。想跟课程一致，就手动建 swap 分区，装完把 swapfile 关掉：
> `sudo swapoff /swap.img && sudo rm /swap.img`，再从 `/etc/fstab` 里删掉对应那行。

---

## 四、CentOS 课程 → Ubuntu 命令对照

| 课程里（CentOS 7.6） | Ubuntu 24.04 | 备注 |
| --- | --- | --- |
| `yum install 包` | `apt install 包` | Ubuntu 用 apt（`apt update` 刷新源） |
| `yum search 包` | `apt search 包` | |
| `rpm -qa` | `dpkg -l` | 包格式 rpm → deb |
| `systemctl start/status 服务` | 完全一样 | 都用 systemd |
| `firewalld` / `firewall-cmd` | `ufw` | `sudo ufw enable`、`sudo ufw allow 22` |
| SELinux | AppArmor | Ubuntu 默认 AppArmor |
| 网卡配置 `/etc/sysconfig/network-scripts/ifcfg-*` | `/etc/netplan/*.yaml` | 改完 `sudo netplan apply` |
| `hostnamectl set-hostname xxx` | 一样 | |
| 分区工具 `fdisk` / `parted` | 一样 | 命令用法基本通用 |
| 文件系统 xfs | 默认 ext4 | 也能 `mkfs.xfs`（需装 xfsprogs） |

---

## 五、提醒

- 练分区一定用**新加的空盘**（/dev/sdb），别动 `/dev/sda`（那是你的系统盘，动它就起不来了）。
- `/etc/fstab` 写错会导致开机卡在紧急模式，写之前先 `cp /etc/fstab /etc/fstab.bak`。
- 动手前拍快照：VMware 菜单 `虚拟机 → 快照 → 拍摄快照`。
