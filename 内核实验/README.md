# 内核编译实验（x86_64 + QEMU）

> 建立于 **2026-11-13**。目标：**从源码编译 Linux 内核，用 QEMU 启动，做出一个能敲命令的最小系统。**
> 这是「香橙派」那条线的准备工作 —— 下一步把同一套流程搬到 **ARM64**。

---

## 零、上下文丢了先看这里

1. **内核**：`linux-6.12.0`（清华镜像 tarball，142 MB，解压 1.6 GB）
2. **目录**：`~/kernel-lab/linux-6.12/`（源码）、`~/kernel-lab/rootfs/`（根文件系统）
3. **实验主机**：Ubuntu 24.04 虚拟机（VMware，**4 核 / 7.8 GB 内存 / 4 GB swap**）
4. **产物**：`vmlinux`（50 MB）、`arch/x86/boot/bzImage`（13 MB）
5. **结果**：QEMU 里拿到 `~ #` 提示符，能跑 272 个 busybox 命令

---

## 一、完整流程（可复用的 SOP）

```bash
# ① 装工具
sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
                    libelf-dev bc git wget xz-utils qemu-system-x86 \
                    busybox-static cpio

# ② 源码（清华镜像，比 kernel.org 快）
mkdir -p ~/kernel-lab && cd ~/kernel-lab
wget https://mirrors.tuna.tsinghua.edu.cn/kernel/v6.x/linux-6.12.tar.xz
tar -xf linux-6.12.tar.xz && cd linux-6.12

# ③ 配置
make defconfig            # 生成 .config（5360 行）

# ④ 编译（4 核实测 16 分钟）
make -j4 > ~/kernel-lab/build.log 2>&1 ; echo "退出码: $?" ; tail -20 ~/kernel-lab/build.log
# 成功标志：Kernel: arch/x86/boot/bzImage is ready  (#1)

# ⑤ 造最小根文件系统
cd ~/kernel-lab && mkdir -p rootfs/{bin,proc,sys,dev}
cp /bin/busybox rootfs/bin/
cd rootfs/bin && for c in $(./busybox --list); do [ "$c" = busybox ] && continue; ln -sf busybox "$c"; done
cd .. && cat > init <<'EOF'
#!/bin/busybox sh
/bin/busybox mount -t proc     none /proc
/bin/busybox mount -t sysfs    none /sys
/bin/busybox mount -t devtmpfs none /dev
echo "=== 我的内核 + 我的根文件系统 ==="
exec /bin/busybox sh
EOF
chmod +x init

# ⑥ 打包（cpio newc 是内核唯一接受的格式）
find . | cpio -o -H newc > ../initramfs.cpio

# ⑦ 启动
cd ~/kernel-lab
qemu-system-x86_64 -kernel linux-6.12/arch/x86/boot/bzImage \
  -initrd initramfs.cpio -append "console=ttyS0 rdinit=/init" \
  -display none -serial stdio -monitor none -m 512
# 退出：Ctrl+C
```

---

## 二、⛔ 踩过的坑（每个都是真踩）

| # | 坑 | 真相 |
| --- | --- | --- |
| 1 | **`busybox --install -s bin`** 建的软链指向 `/home/cxh/kernel-lab/rootfs/bin/busybox`（**主机绝对路径**） | 打包进 initramfs 后路径不存在 → **所有命令 `not found`**。解法：**手动建相对链接** `ln -sf busybox <cmd>`。专业做法是 **chroot** 后再 install |
| 2 | **`rm -f $(./busybox --list)`** 把 busybox 自己删了 | `--list` 的输出**包含 `busybox`**。安全写法：`for c in $(./busybox --list); do [ "$c" = busybox ] && continue; ...; done`。**通用教训：`rm -f $(...)` 是危险模式，先 `echo` 看清单** |
| 3 | **`cpio ... 2>/dev/null`** 吞掉构建错误 | 打出了残缺的包，还查不出来。**造镜像时绝不要吞错误** |
| 4 | QEMU 里 `Ctrl+A X` 有时按不出来 | 键要送进 QEMU 窗口才生效。**改用 `-display none -serial stdio -monitor none`，`Ctrl+C` 直接退** |
| 5 | 去掉 `console=ttyS0` 后"完全没反应" | **内核在跑，只是日志写给了不存在的 VGA**。验证手法：**`-serial file:log.txt`** |
| 6 | 以为 `-m 64` 会起不来 | **实测 64 MB 够用**（内核 ~25 MB + rootfs ~1 MB + 开销）。**内核比想象的小得多** |

---

## 三、关键概念（这次真正建立的）

### 配置（`.config`）
- **5360 行配置**决定了 34667 个 `.c` 里哪些进编译
- **1577 个 `=y`**（编进内核）+ **13 个 `=m`**（模块）+ **2608 个 `is not set`**（砍掉）
- `Kconfig` → `make menuconfig` 画菜单；`defconfig` = 架构的推荐默认

### 编译四阶段（对应屏幕上的标记）
```
CC（预处理+编译→.o） → AS（汇编） → LD（链接 vmlinux） → GZIP/OBJCOPY（打包 bzImage）
```
- `HOSTCC` = 编"在主机上运行的工具"（**自举**）

### `bzImage` 结构
**解压器（不压缩） + gzip 压缩的内核（"piggy"）** → 引导程序先跑解压器，把内核解到内存再跳转。
**原因**：引导阶段加载能力/内存有限；解压成本极低（启动最开始 CPU 闲着）。

### ⭐ 内核态 / 用户态（地基）
```
ring 0（内核态）：能执行所有指令、碰所有内存、操作硬件
ring 3（用户态）：只能碰自己的内存
        唯一的门 = 系统调用 syscall
```
- **`ls /bin` 不是 shell 在执行** —— shell 只做 `fork + exec`，真正干活的是 busybox，它通过 `openat/getdents/write` 请求内核
- **两级权限**：① 硬界限 内核态/用户态 ② 软界限 uid/gid/rwx + SELinux
- 验证：Ubuntu 里 `strace -c ls /bin` 能看见每个 syscall

### 最小系统 = 内核 + 一个 init + 文件系统
- 你做的这套：**1 个进程 + 47 个内核线程**（`[kworker/*]` 方括号 = 内核线程，`[kthreadd]` 是它们的爹 PID 2）
- Ubuntu / Android 加的几百个进程**全是用户态软件**，不是内核的一部分

### `/proc` 是"挂"出来的
```
umount /proc  →  cat /proc/version  →  cat: can't open '/proc/version': No such file or directory
mount -t proc none /proc  →  cat /proc/version  →  正常
```
**`ls /proc` 空输出**证明：目录存在（rootfs 里那个空文件夹），**内容全是内核变出来的**。

### ⭐ 两个报错必须分清的措辞
| 报错 | 含义 |
| --- | --- |
| **`sh: cat: not found`** | **命令**找不到（PATH 里没这个程序 / 软链断） |
| **`cat: can't open '/x': No such file or directory`** | **命令有，文件打不开**（路径不存在 / 没挂载） |

---

## 四、实测数据（这台 VM）

| 项 | 值 |
| --- | --- |
| 编译耗时 | **约 16 分钟**（4 核） |
| 源码目录 | 1.6 GB / 34,667 个 `.c` |
| `vmlinux` | **50 MB**（defconfig 不开 DEBUG_INFO；开了会几百 MB~1GB） |
| `bzImage` | **13 MB**（50M 压缩而来） |
| `System.map` | 174,342 个符号；`start_kernel` 在 `ffffffff83264980` |
| initramfs | 2.1 MB（4238 块，busybox 静态 2 MB + 300 软链） |
| 内核启动耗时 | **2.03 秒**到 `Run /init as init process` |
| `MemTotal` | 478,912 kB（`-m 512` 扣掉内核自用） |
| busybox 命令数 | **272** |

---

## 五、下一步

| 优先级 | 内容 |
| --- | --- |
| **1** | ⭐ **交叉编译 ARM64**（`ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-`）+ QEMU `-M virt -cpu cortex-a72` —— **和板子同架构，这才是通往香橙派的路** |
| 2 | 换真实发行版 rootfs（Alpine/Debian minirootfs），得到一个能装包的 mini 系统 |
| 3 | 挂一块虚拟磁盘（`-drive`），让根文件系统落在 ext4 上而不是 initramfs |
| 4 | 用 `make menuconfig` 手动裁剪（对比 defconfig 的体积/功能差异） |

---

## 六、⭐ ARM64 交叉编译（2026-11-14 完成，闭环打通）

### 结果
- 内核 `Image`：**44 MB**（未压缩；x86 的 bzImage 只有 13M）
- rootfs：**Alpine aarch64 minirootfs**（动态链接 musl，约 3 MB）
- **`uname -m` → `aarch64`**；**`/proc/cpuinfo` 的 `CPU part 0xd0b` → Cortex-A76**（与板子 RK3588S 的大核**同型号**）

### 和 x86 的差异对照
| 项 | x86_64 | **arm64** |
| --- | --- | --- |
| 编译器 | 本机 `gcc` | `aarch64-linux-gnu-gcc` |
| 产物 | `bzImage` 13M（解压器+压缩内核） | **`Image` 44M（裸二进制）** |
| 串口 | `ttyS0` | **`ttyAMA0`**（PL011） |
| 硬件描述 | ACPI/固件（`efi`/`ACPI`/`DMI` 日志） | **设备树**（`Machine model: linux,dummy-virt`，panic 里标 `(DT)`） |
| 配置规模 | `=y` 1577 / `=m` **13** / not set 2608 | `=y` 3164 / `=m` **1167** / not set 4754 |
| 权限分层 | ring 0–3 | **EL0–EL3**；QEMU 默认不给 EL2（`kvm: HYP mode not available`） |

### 命令（arm64）
```bash
# ① 交叉编译（必须 O= 分离目录）
sudo apt install -y gcc-aarch64-linux-gnu qemu-system-arm
cd ~/kernel-lab/linux-6.12
make mrproper                      # ⚠️ 源码树有旧产物时 O= 会被拒绝
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=~/kernel-lab/build-arm64 defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=~/kernel-lab/build-arm64 -j4 Image

# ② rootfs（Alpine，动态链接）
F=$(curl -s https://mirrors.tuna.tsinghua.edu.cn/alpine/latest-stable/releases/aarch64/ \
    | grep -oE 'alpine-minirootfs-[0-9.]+-aarch64\.tar\.gz' | sort -u | tail -1)
wget "https://mirrors.tuna.tsinghua.edu.cn/alpine/latest-stable/releases/aarch64/$F"
mkdir -p rootfs-arm64 && tar -xzf "$F" -C rootfs-arm64
cd rootfs-arm64 && cat > init <<'EOF'
#!/bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
mount -t devtmpfs none /dev
exec /bin/sh
EOF
chmod +x init && find . | cpio -o -H newc | gzip > ../initramfs-arm64.cpio.gz

# ③ 启动
qemu-system-aarch64 -M virt -cpu cortex-a76 -smp 4 -m 512 \
  -kernel build-arm64/arch/arm64/boot/Image \
  -initrd initramfs-arm64.cpio.gz \
  -append "console=ttyAMA0 rdinit=/init" \
  -display none -serial stdio -monitor none
```

### 这一步踩的坑
| 坑 | 真相 |
| --- | --- |
| `*** The source tree is not clean, please run 'make mrproper'` | 源码树里有 in-tree 构建留下的 `.config`/`include/generated` → **`O=` 外编前必须先 mrproper**（先把旧产物拷到 `out-x86/` 再清） |
| rootfs 不能跨架构复用 | x86 的 busybox（ELF x86-64）在 ARM 上一条指令都跑不了 |
| Alpine 的 busybox 是**动态链接** | 依赖 `interpreter /lib/ld-musl-aarch64.so.1` → **必须整包打包，不能只拷 busybox** |
| 实际是 **EL1** 不是 EL2 | QEMU `-M virt` 默认不给虚拟化层；要 EL2 需 `-M virt,virtualization=on -cpu max` |

### 意义
**同一份源码 → 两个架构 → 两个都能启动 → 两个都有 shell。** 交叉编译闭环完成。
**离"上板子"只差一个正确的设备树**：`arch/arm64/boot/dts/rockchip/rk3588s-orangepi-5.dtb`（用 `make ARCH=arm64 ... dtbs` 生成）。

---

## 七、⭐ 设备树验证结果（2026-11-14）

**主线 Linux 6.12 官方收录了 Orange Pi 5 的设备树** —— 这是"能用主线内核跑这块板子"的门票。

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- O=~/kernel-lab/build-arm64 -j4 dtbs
ls ~/kernel-lab/build-arm64/arch/arm64/boot/dts/rockchip | grep -i orangepi
```

实测列表里有：`rk3328-orangepi-r1-plus`、`rk3399-orangepi`、`rk3566-orangepi-3b`、
`rk3588-orangepi-5-plus`、**`rk3588s-orangepi-5.dtb`** ← 本板

### dtb / dts 实测数据
| 项 | 值 |
| --- | --- |
| dtb 大小 | **75 KB**（76693 字节，version 17，boot CPU=0） |
| 反编译后 `.dts` | **4410 行** |
| `model`（主线） | **`Xunlong Orange Pi 5`** |
| `model`（厂商内核，板子上 `/sys/firmware/devicetree/base/model`） | **`Orange Pi 5`** ← 不完全一样，厂商用自己的 dts |
| `compatible` | `"xunlong,orangepi-5", "rockchip,rk3588s"`（板子 + SoC 两级匹配） |
| UART | `serial0`~`serial7`（8 个） |
| GPIO 物理地址 | `gpio@fd8a0000`、`gpio@fec20000` … |
| `memory@` 节点 | **dtb 里没有** —— Rockchip 惯例：内存大小由 U-Boot 启动时填进 `/memory` |

反编译命令：`dtc -I dtb -O dts <dtb> -o out.dts`（需 `apt install device-tree-compiler`）

### 补充实测（2026-11-14）
- **主线 dtb 里 `memory` 节点完全没有** —— `grep -n "memory" /tmp/opi5.dts` **零命中**。内存信息 100% 由 U-Boot 在启动时创建 `/memory` 节点（同一份 dtb 适配 2/4/8/16GB 各版本）。
- **板子厂商 dtb 的顶层节点数 = 346**（`ls /sys/firmware/devicetree/base/ | wc -l`）。
  里面有 `can@fea50000/60000/70000`（3 路 CAN）、`av1d@fdc70000`（AV1 硬解）、`avsd-plus@fdb51000`（AVS 标准）、`arm-pmu`（性能计数器）、`cluster0/1-opp-table`（大小核各自的频率电压表）、`adc-keys`（ADC 按键）、`bt-sco`/`bt-sound`（蓝牙语音）、`__symbols__`（说明厂商编译时开了 dtc overlay 支持）。

### 结论
**「主线内核 + 自己的设备树 → 跑 Linux」这条路是通的**，不需要任何厂商补丁。
**距离真上板子还差两步**：① 用 U-Boot 加载这个 Image+dtb（板子 SPI 里现在是厂商 U-Boot）；
② rootfs 要放到存储上而不是 initramfs。**最省事的入口仍是先刷一个 Armbian/官方 Ubuntu 镜像，再替换内核。**
