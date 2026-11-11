#!/usr/bin/env bash
# Ubuntu 24.04 学习环境初始化（面向命令行初学者）
# 用法：在虚拟机里执行  bash setup.sh
set -euo pipefail

echo "==> 1/5 切换软件源为清华镜像（装软件快很多）"
if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
  sudo sed -i \
    -e 's|http://cn.archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' \
    -e 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' \
    -e 's|http://security.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' \
    /etc/apt/sources.list.d/ubuntu.sources
fi

echo "==> 2/5 更新软件列表"
sudo apt-get update -y

echo "==> 3/5 安装命令行常用工具"
sudo apt-get install -y \
  openssh-server \
  vim tmux tree htop curl wget git \
  net-tools bash-completion unzip zip \
  man-db manpages-zh \
  build-essential python3-pip \
  open-vm-tools-desktop

echo "==> 4/5 开启 SSH（方便从 Windows 终端连进来贴命令）"
sudo systemctl enable --now ssh

echo "==> 5/5 基本信息"
echo "主机名：$(hostname)"
echo "用户名：$(whoami)"
echo "本机 IP（Windows 里 ssh 用这个地址）："
ip -4 -o addr show scope global | awk '{print "  " $2 "  " $4}'
echo
echo "完成。建议现在拍一张 VMware 快照，之后折腾坏了可以回滚。"
