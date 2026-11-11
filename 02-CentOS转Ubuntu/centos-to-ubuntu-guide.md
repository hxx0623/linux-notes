# CentOS 7.6 课程 → Ubuntu 24.04 对照手册

> 用法：看课程时遇到不认识的命令，先在本表里查「CentOS 怎么写 / Ubuntu 怎么写」。
> 原则：**思路一样，工具名可能不同**。`systemctl`、`fdisk`、`mount`、`chmod`、`ps`、`ss`、`grep` 这些几乎完全通用，不用翻译。

---

## 一、包管理（差异最大，优先记）

| 目的 | CentOS 7（yum） | Ubuntu 24.04（apt） |
| --- | --- | --- |
| 刷新软件列表 | `yum makecache` | `sudo apt update` |
| 装软件 | `yum install -y httpd` | `sudo apt install -y apache2` |
| 卸载 | `yum remove httpd` | `sudo apt remove apache2`（含配置用 `purge`） |
| 搜索 | `yum search nginx` | `apt search nginx` |
| 查已装 | `rpm -qa` | `dpkg -l` |
| 查某文件属于哪个包 | `rpm -qf /usr/bin/vim` | `dpkg -S /usr/bin/vim` |
| 查包装了哪些文件 | `rpm -ql nginx` | `dpkg -L nginx` |
| 查某个命令在哪个包 | `yum provides */ifconfig` | `apt install apt-file && sudo apt-file update && apt-file search ifconfig` |
| 查可用版本 | `yum list available | grep nginx` | `apt list nginx`（`apt policy nginx` 更全） |
| 清理缓存 | `yum clean all` | `sudo apt clean` |
| 升级全部 | `yum update` | `sudo apt upgrade` |
| 软件源配置 | `/etc/yum.repos.d/*.repo` | `/etc/apt/sources.list.d/ubuntu.sources` |
| 本地装包 | `rpm -ivh x.rpm` | `sudo dpkg -i x.deb`（缺依赖 `sudo apt -f install`） |

### 课程里最常装的软件，名字对照

| 课程（CentOS 包名） | Ubuntu 包名 | 备注 |
| --- | --- | --- |
| `httpd` | `apache2` | 网站服务，配置文件路径完全不同 |
| `mariadb-server` / `mysql-server` | `mariadb-server` | Ubuntu 默认也是 MariaDB |
| `php` | `php` | 差不多，模块名 `php` 而非 `php-fpm` 需要单独装 |
| `vsftpd` | `vsftpd` | 一样 |
| `nginx` | `nginx` | 一样，但配置目录 `/etc/nginx/` 结构略有差别 |
| `openssh-server` | `openssh-server` | 一样 |
| `net-tools`（ifconfig） | `net-tools` | 一样，Ubuntu 也可以直接用 `ip` |
| `firewalld` | `ufw`（默认） | 见第六节 |
| `chrony` | `systemd-timesyncd`（默认）/`chrony` | 都能装 |
| `rsync`、`vim`、`wget`、`curl`、`tree`、`unzip` | 同名 | 通用 |
| `bash-completion` | `bash-completion` | 一样 |
| `telnet` | `telnet` | 一样（客户端） |

---

## 二、服务管理（基本一致）

```bash
systemctl start/stop/restart/status 服务名
systemctl enable/disable 服务名
systemctl enable --now 服务名     # 开机自启并立刻启动
systemctl list-unit-files | grep xxx
```

差异只在**服务名**：

| 服务 | CentOS 名 | Ubuntu 名 |
| --- | --- | --- |
| Web | `httpd` | `apache2` |
| SSH | `sshd` | `ssh` |
| 防火墙 | `firewalld` | `ufw`（用 `sudo ufw ...` 管理，不是 systemctl） |
| 网络 | `network` | `NetworkManager`（桌面版）/ `systemd-networkd` |
| 时间同步 | `chronyd` | `systemd-timesyncd` |

`chkconfig 服务 on`（CentOS 6 老写法）→ 一律换成 `systemctl enable 服务`。

---

## 三、配置文件与日志路径对照

| 内容 | CentOS 7 | Ubuntu 24.04 |
| --- | --- | --- |
| Apache 主配置 | `/etc/httpd/conf/httpd.conf` | `/etc/apache2/apache2.conf` + `sites-available/` |
| Apache 站点根 | `/var/www/html` | `/var/www/html`（一样） |
| Apache 日志 | `/var/log/httpd/` | `/var/log/apache2/` |
| MySQL/MariaDB 配置 | `/etc/my.cnf` | `/etc/mysql/mysql.conf.d/mysqld.cnf` |
| Nginx 配置 | `/etc/nginx/nginx.conf` | `/etc/nginx/nginx.conf`（一样，sites 用 `sites-available/`） |
| SSH 配置 | `/etc/ssh/sshd_config` | 一样 |
| 系统日志 | `/var/log/messages` | `/var/log/syslog`（`journalctl` 两边都通用） |
| 网卡配置 | `/etc/sysconfig/network-scripts/ifcfg-xxx` | `/etc/netplan/*.yaml` |
| 环境变量（全局） | `/etc/profile`、`/etc/profile.d/` | 一样 |
| 开机自启脚本 | `/etc/rc.d/rc.local`（需 `chmod +x`） | 默认没有，自建 systemd service 或用 `crontab @reboot` |
| 定时任务 | `/etc/crontab`、`crontab -e` | 一样 |
| DNS | `/etc/resolv.conf`（直接改） | `/etc/resolv.conf` 由 systemd-resolved 托管，改 `/etc/systemd/resolved.conf` |

---

## 四、用户与权限（几乎通用）

```bash
useradd -m 用户名         # -m 建家目录（CentOS/RHEL 习惯）
passwd 用户名
usermod -aG sudo 用户名   # CentOS 里是 usermod -aG wheel 用户名
id 用户名
groupadd / groupdel
chmod 755 文件 ; chown 用户:组 文件 ; umask
```
- 管理员组：CentOS 是 `wheel`，Ubuntu 是 `sudo`。
- `sudo` 配置：`/etc/sudoers`（两边一样，用 `visudo` 改）。
- 目录默认权限同为 755，用户家目录同为 700/750。

---

## 五、网络（命令通用，配置方式不同）

```bash
ip addr ; ip route ; ss -tlnp ; ping ; traceroute ; dig/nslookup ; hostname -I
```
- `ifconfig`/`netstat` 需要 `sudo apt install net-tools`。
- **静态 IP**：课程改 `ifcfg-ens33`（`BOOTPROTO=static`、`IPADDR=...`）→ Ubuntu 改 netplan：
  ```yaml
  # /etc/netplan/01-netcfg.yaml
  network:
    version: 2
    ethernets:
      ens33:
        dhcp4: false
        addresses: [192.168.100.10/24]
        routes:
          - to: default
            via: 192.168.100.2
        nameservers:
          addresses: [223.5.5.5, 114.114.114.114]
  ```
  改完 `sudo netplan apply`。
- 开 SSH：`sudo apt install openssh-server`（CentOS 默认装了）。

---

## 六、防火墙：firewalld → ufw

| 目的 | CentOS（firewall-cmd） | Ubuntu（ufw） |
| --- | --- | --- |
| 查看状态 | `firewall-cmd --state` | `sudo ufw status verbose` |
| 放行端口 | `firewall-cmd --add-port=80/tcp --permanent` | `sudo ufw allow 80/tcp` |
| 放行服务 | `firewall-cmd --add-service=http --permanent` | `sudo ufw allow 'Apache'` |
| 拒绝端口 | `firewall-cmd --remove-port=80/tcp` | `sudo ufw delete allow 80/tcp` |
| 重载 | `firewall-cmd --reload` | 不需要（立即生效） |
| 开机启用 | `systemctl enable --now firewalld` | `sudo ufw enable` |

> ufw 默认拒绝所有入站、允许所有出站，思路和 firewalld 的 zone 一样简单化。想看规则：`sudo ufw status numbered`。
> 底层都是 nftables/iptables，`iptables -L -n` 两边都能看。

---

## 七、SELinux → AppArmor

| 目的 | CentOS（SELinux） | Ubuntu（AppArmor） |
| --- | --- | --- |
| 看状态 | `getenforce` | `sudo aa-status` |
| 临时关闭 | `setenforce 0` | `sudo systemctl stop apparmor` |
| 永久关闭 | `/etc/selinux/config` 改 `SELINUX=disabled` | `sudo systemctl disable apparmor` |
| 看日志 | `/var/log/audit/audit.log` | `/var/log/kern.log`、`dmesg` |

课程里讲 SELinux 部分，Ubuntu 上直接记 AppArmor 是同类东西即可；做实验时通常 Ubuntu 不会因它拦你。

---

## 八、课程实验在 Ubuntu 上怎么做

| 课程实验 | Ubuntu 里的做法 |
| --- | --- |
| 安装系统、手动分区 | 已装好；想练分区就加一块 20GB 空盘，用 `fdisk`/`mkfs`/`mount`（见 `../03-命令速查/ubuntu-partition-guide.md`） |
| 用户与组管理 | 完全一样，只把 `wheel` → `sudo` |
| 文件权限、ACL | 一样（ACL 用 `setfacl`，装 `acl` 包两边都要） |
| 进程管理 `ps/top/kill` | 一样，`top` 建议换 `htop` |
| 软件安装实验 | 视频 `yum install nginx` → 你 `sudo apt install nginx`，验证方式一样 `systemctl status nginx` |
| Apache 建站 | 装 `apache2`，配置改 `/etc/apache2/`，页面放 `/var/www/html` |
| LAMP 环境 | `sudo apt install apache2 mariadb-server php libapache2-mod-php`，然后 `sudo mysql_secure_installation` |
| 防火墙放行 80 | `sudo ufw allow 80/tcp` |
| SSH 免密登录 | `ssh-keygen` + `ssh-copy-id` 完全一样 |
| 磁盘挂载 / fstab | 完全一样 |
| 定时任务 crontab | 完全一样 |
| 日志查看 | `journalctl -u 服务 -f` 一样；`/var/log/messages` → `/var/log/syslog` |
| Shell 脚本 | 完全一样（`#!/bin/bash`） |

---

## 九、想在 Ubuntu 里练 yum 命令（可选小技巧）

装 Docker 后可以跑一个 CentOS 7 容器，专门练 `yum`：

```bash
sudo apt install -y docker.io
sudo docker run -it --rm centos:7 bash
# 容器里就能用 yum（需要先修好 vault 源：sed -i 's|mirror.centos.org|vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo）
```

容器是临时的，`--rm` 退出即删，不占空间，适合对照着玩。

---

## 十、你的 Ubuntu 环境清单（备忘）

| 项目 | 情况 |
| --- | --- |
| 系统 | Ubuntu 24.04.5 LTS，内核 7.0.0-38-generic |
| 分区 | `/dev/sda1` 1GB vfat → `/boot/efi`；`/dev/sda2` 59GB ext4 → `/`；swap 用 `/swap.img` 文件 2GB |
| 虚拟机 | VMware Workstation 17.5.2，8GB 内存 / 4 核 / 60GB 盘 |
| 镜像 | `D:\VMs\iso\ubuntu-24.04.5.1-desktop-amd64.iso`（SHA256 已校验） |
| 待办 | 换国内源、装常用工具、开 SSH（setup.sh 已备好） |
