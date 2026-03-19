# AmneziaWG Web UI on ARM64 Proxmox VE 8 (LXC + Docker) + Kernel Module

**Tested**: Oracle Cloud ARM64 → Proxmox VE 8 (Debian 12, kernel 6.1.0-25-cloud-arm64) → Ubuntu 22.04 LXC → Docker → AWG Web UI (fahrimert arm64 fix).

## 🎯 Проблемы и решения
| Проблема | Причина | Решение |
|----------|---------|---------|
| Docker build fail | x86 static binary | fahrimert PR #34 (multi-stage ARM64) [github](https://github.com/w0rng/amnezia-wg-easy/issues/10) |
| UI "Start" silent fail | `reaped unknown pid` | Manual `awg-quick` + config fixes |
| No handshake (userspace) | amneziawg-go ARM64 bug | **Kernel module on Proxmox HOST** |
| Config path | `/etc/amnezia/amneziawg/` vs `/etc/amnezia/` | `cp` или symlink |
| Invalid PSK | `PresharedKey = None` | `sed -i '/PresharedKey/d' *.conf` |

## 📋 Пошаговая инструкция

### 1. Proxmox HOST: Kernel Module
```bash
# Fix repos (если warnings)
rm -f /etc/apt/sources.list.d/*pve*
echo "deb [arch=arm64] http://download.proxmox.com/debian/pve bookworm pve-no-subscription" >> /etc/apt/sources.list.d/pve-no-subscription.list
wget https://enterprise.proxmox.com/debian/proxmox-release-bookworm.gpg -O /etc/apt/trusted.gpg.d/proxmox-release-bookworm.gpg
apt update

# Headers + deps
apt install -y linux-headers-$(uname -r) linux-headers-cloud-arm64 dkms git build-essential bc bison flex libelf-dev

# Compile & install module
git clone https://github.com/amnezia-vpn/amneziawg-linux-kernel-module.git /tmp/module
cd /tmp/module/src
make clean && make -j$(nproc) && make install
depmod -a
modprobe amneziawg
lsmod | grep amneziawg  # ✅
```

### 2. LXC Config (Ubuntu 22.04, ID=108)
`/etc/pve/lxc/108.conf` (добавь/проверь):
```bash
lxc.mount.entry: /lib/modules lib/modules none bind,optional,create=dir 0
lxc.cgroup2.devices.allow: c *:* rwm
lxc.cap.drop:
features: nesting=1,keyctl=1
```
```bash
pct reboot 108
```

### 3. Ubuntu LXC: Проверка + Docker
```bash
# В LXC
modprobe amneziawg
lsmod | grep amneziawg  # ✅
echo "modprobe amneziawg" >> /etc/rc.local

cd AWG20
git clone -b fix/arm64-support-multistage https://github.com/fahrimert/amneziawg-web-ui.git
cd amneziawg-web-ui

# Docker Compose (удали image:, оставь build: .)
docker compose up --build -d

# UI: http://IP:51821 (admin/пароль из логов)
```

### 4. Docker: Manual Server Start (UI "Start" broken)
```bash
docker exec -it amnezia-web-ui sh
cp /etc/amnezia/amneziawg/wg-XXXX.conf /etc/amnezia/  # path fix
sed -i '/PresharedKey/d' /etc/amnezia/wg-XXXX.conf     # PSK fix
chmod 600 /etc/amnezia/*.conf
awg-quick up wg-XXXX  # ✅ KERNEL MODE (no userspace fallback!)
```

### 5. Проверка
```bash
# В Docker
awg show wg-XXXX  # Jc/S/H params, peer ready
ip a show wg-XXXX # 10.8.0.1/24 UP

# На хосте
tcpdump -i any udp port 51820  # bidirectional traffic!
```

## ✅ Результат
- **ARM64 native build** (fahrimert PR #34).
- **Kernel mode** (no userspace bugs).
- **Client handshakes** мгновенно.
- Manual start (UI fix pending).

