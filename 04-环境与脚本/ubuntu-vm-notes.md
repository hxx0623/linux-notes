# Ubuntu 24.04 LTS 虚拟机（VMware Workstation）

## 文件位置

| 内容 | 路径 |
| --- | --- |
| 虚拟机目录 | `D:\VMs\Ubuntu-24.04\` |
| 配置文件 | `D:\VMs\Ubuntu-24.04\Ubuntu-24.04.vmx` |
| 虚拟磁盘（60GB 稀疏） | `D:\VMs\Ubuntu-24.04\Ubuntu-24.04.vmdk` |
| 安装镜像（5.82GB） | `D:\VMs\iso\ubuntu-24.04.5.1-desktop-amd64.iso` |

## 虚拟机规格

- 内存 8GB / 4 vCPU（宿主 31.4GB 内存）
- 60GB 系统盘，SCSI LSI Logic；**2026-10-29 练习分区时又热加了 5GB 盘** → `sdb1` ext4 → 挂 `/newdisk`（写进 fstab，用 UUID）
- EFI 固件、NAT 联网、USB 3.0、声卡、3D 加速开启
- 网卡 **`ens160`**（不是课件里的 `ens33`），**静态 IP `192.168.139.100`**，网关 `192.168.139.2`（10-29 起不再用 DHCP）
- ⚠️ IP 是在桌面 GUI 里设的，`/etc/netplan/50-cloud-init.yaml` 仍写着 `dhcp4: true` —— **不要执行 `sudo netplan apply`**，否则可能打回 DHCP
- ~~ISO 挂在 SATA 光驱，开机遇直接从光盘启动~~ → 2026-10-20 已断开（`sata0:0.startConnected = FALSE`），开机直接进 Ubuntu；要重装再把 vmx 里改回 `TRUE`

## 第二台虚拟机：mini-linux（2026-11-06 建成）

第 22 章「定制自己的 Linux」的实战产物 —— 从上面这台裁剪出来的一块**能独立启动**的系统盘。

| 项 | 值 |
| --- | --- |
| 虚拟机 | 名字 `mini-linux`，配置 `D:\VMs\mini-linux\mini-linux.vmx`，**UEFI**，2 GB / 2 核 |
| 磁盘 | `D:\VMs\Ubuntu-24.04\Ubuntu-24.04-minilinux.vmdk`（16 GB 稀疏，实占约 5.4 GB） |
| 登录 | `tty1` 纯文本，主机名 `mini01`，用户 `cxh`（密码与主系统相同） |
| 分区 | `sda1` 300M vfat `/boot/efi`（ESP）｜`sda2` 1G ext4 `/boot`｜`sda3` 14.7G ext4 `/` |
| UUID | ESP `1676-E9EE`｜/boot `780084d7-1692-4327-981f-a2f213b66b87`｜/ `9c09b34a-e011-4fb9-87d3-448ce78ea850` |
| ⚠️ 引导跳板 | `/boot/efi/boot/grub/grub.cfg` 仅两行：`set root=(hd0,gpt2)` + `configfile /grub/grub.cfg`。**GRUB 的 `$prefix` 是 `(hd0,gpt1)/boot/grub`，不是 `/EFI/BOOT`** |
| ⚠️ 盘锁 | 一块 vmdk 同一时刻只能挂一台虚拟机、一台里只能出现一次；否则报「另一个程序已锁定文件的一部分」 |

> 完整施工流程、7 个踩坑、故障对照表见 `05-课程笔记/韩顺平Linux-笔记-126-128.md`。

## 手动安装步骤（安装向导）

1. 启动后等一下，出现 `GNU GRUB` 菜单选 **Try or Install Ubuntu**（默认项直接回车）。
2. **语言**：English（或中文）→ Continue
3. **键盘布局**：English (US) → Continue
4. **网络**：保持已连接（NAT 自动 DHCP）→ Continue
5. **安装类型**：选 **Interactive installation** → Continue
6. **应用选择**：选 **Default selection**（需要办公/开发全套可选 Extended）→ Continue
7. **第三方驱动**：勾上 **Install third-party software for graphics and Wi-Fi hardware** → Continue
8. **安装方式**：选 **Erase disk and install Ubuntu**（这是虚拟机的新 60GB 空盘，随便擦）→ Continue
9. **创建账户**：填 Your name / 用户名 / 计算机名 / 密码（建议勾选登录需要密码）→ Continue
10. **时区**：点地图上 China / Shanghai → Continue
11. 等 10-20 分钟安装完成 → **Restart now** → 提示时按回车，虚拟机自动从硬盘重启（若又进安装界面，说明光驱先启动，等它超时或断开光驱即可）。

> 中途语言、用户名、密码这些我没法替你定，所以留给你点；其余我都配好了。

## 装好之后

- 分辨率自适应/剪贴板共享/共享文件夹依赖 open-vm-tools-desktop：
  `sudo apt install -y open-vm-tools-desktop` 然后重启。
- 换国内软件源（装软件快）：
  `sudo sed -i 's|http://cn.archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources`
- 快照：VMware 菜单 `虚拟机 → 快照 → 拍摄快照`，装好系统先拍一张，以后折腾坏了能回滚。

## 校验镜像（可选）

SHA256（官方）：
`4da4a0c9035da8e68a59a838674f403f0a54472c78a83b4fb7f78d03588f85a7`

PowerShell 校验：
```powershell
Get-FileHash 'D:\VMs\iso\ubuntu-24.04.5.1-desktop-amd64.iso' -Algorithm SHA256
```
