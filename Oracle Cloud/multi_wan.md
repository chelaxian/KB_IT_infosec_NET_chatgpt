
---

# 🔹 Шаблон настройки PBR (Policy Based Routing) и NAT для Proxmox

## 1. Подготовка

Включаем форвардинг пакетов и сохраняем:

```bash
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p
```

---

## 2. IP-адреса на внешних интерфейсах

Добавляем вторичные IP (если нужно несколько IP на одном интерфейсе):

```bash
ip addr add 10.0.0.103/24 dev enp0s6   # основной IP
ip addr add 10.0.0.104/24 dev enp0s6   # доп. IP
ip addr add 10.0.0.105/24 dev enp1s0   # основной IP
ip addr add 10.0.0.106/24 dev enp1s0   # доп. IP
```

Чтобы сохранить, прописываем в `/etc/network/interfaces` или в systemd-networkd.

---

## 3. Таблицы маршрутизации

В `/etc/iproute2/rt_tables` добавляем уникальные ID для каждой сети:

```ini
201 enp0s6-main
202 enp0s6-extra
203 enp1s0-main
204 enp1s0-extra
210 vmbr1
211 vmbr0
212 vmbr10
213 vmbr11
214 dhcpnet
```

---

## 4. Маршруты для каждой таблицы

### enp0s6-main (10.0.0.103)

```bash
ip route add 10.0.0.0/24 dev enp0s6 src 10.0.0.103 table enp0s6-main
ip route add default via 10.0.0.1 dev enp0s6 table enp0s6-main
```

### enp0s6-extra (10.0.0.104)

```bash
ip route add 10.0.0.0/24 dev enp0s6 src 10.0.0.104 table enp0s6-extra
ip route add default via 10.0.0.1 dev enp0s6 table enp0s6-extra
```

### enp1s0-main (10.0.0.105)

```bash
ip route add 10.0.0.0/24 dev enp1s0 src 10.0.0.105 table enp1s0-main
ip route add default via 10.0.0.1 dev enp1s0 table enp1s0-main
```

### enp1s0-extra (10.0.0.106)

```bash
ip route add 10.0.0.0/24 dev enp1s0 src 10.0.0.106 table enp1s0-extra
ip route add default via 10.0.0.1 dev enp1s0 table enp1s0-extra
```

---

## 5. PBR для мостов (vmbr)

### vmbr1 (10.10.0.0/24 → enp1s0 → 10.0.0.105)

```bash
ip route add default via 10.0.0.1 dev enp1s0 table vmbr1
ip route add 10.10.0.0/24 dev vmbr1 src 10.10.0.1 table vmbr1
ip rule add from 10.10.0.0/24 table vmbr1
```

### vmbr0 (10.14.0.0/24 → enp0s6 → 10.0.0.103)

```bash
ip route add default via 10.0.0.1 dev enp0s6 table vmbr0
ip route add 10.14.0.0/24 dev vmbr0 src 10.14.0.1 table vmbr0
ip rule add from 10.14.0.0/24 table vmbr0
```

### vmbr10 (10.140.0.0/24 → enp0s6 → 10.0.0.104)

```bash
ip route add default via 10.0.0.1 dev enp0s6 table vmbr10
ip route add 10.140.0.0/24 dev vmbr10 src 10.140.0.1 table vmbr10
ip rule add from 10.140.0.0/24 table vmbr10
```

### vmbr11 (10.100.0.0/24 → enp1s0 → 10.0.0.106)

```bash
ip route add default via 10.0.0.1 dev enp1s0 table vmbr11
ip route add 10.100.0.0/24 dev vmbr11 src 10.100.0.1 table vmbr11
ip rule add from 10.100.0.0/24 table vmbr11
```

### DHCP (10.200.200.0/24 → enp0s6 → 10.0.0.103)

```bash
ip route add default via 10.0.0.1 dev enp0s6 table dhcpnet
ip route add 10.200.200.0/24 dev DHCP src 10.200.200.1 table dhcpnet
ip rule add from 10.200.200.0/24 table dhcpnet
```

---

## 6. Правила iptables (SNAT)

Для каждой локальной сети SNAT на нужный внешний IP:

```bash
iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o enp0s6 -j SNAT --to-source 10.0.0.103
iptables -t nat -A POSTROUTING -s 10.10.0.0/24   -o enp1s0 -j SNAT --to-source 10.0.0.105
iptables -t nat -A POSTROUTING -s 10.14.0.0/24   -o enp0s6 -j SNAT --to-source 10.0.0.103
iptables -t nat -A POSTROUTING -s 10.100.0.0/24  -o enp1s0 -j SNAT --to-source 10.0.0.106
iptables -t nat -A POSTROUTING -s 10.140.0.0/24  -o enp0s6 -j SNAT --to-source 10.0.0.104
```

❗ ВАЖНО: удалить все лишние `MASQUERADE`, чтобы они не перебивали SNAT.

---

## 7. Проверка

Проверяем, что всё работает:

```bash
ip rule show
ip route show table vmbr1
ip route get 8.8.8.8 from 10.10.0.2
curl ifconfig.io --interface net1
```

---

## 8. Автоматизация

Скрипт, например `/etc/network/if-up.d/pbr.sh`:

```bash
#!/bin/bash
# включение PBR

# vmbr1
ip route add default via 10.0.0.1 dev enp1s0 table vmbr1
ip route add 10.10.0.0/24 dev vmbr1 src 10.10.0.1 table vmbr1
ip rule add from 10.10.0.0/24 table vmbr1

# vmbr0
ip route add default via 10.0.0.1 dev enp0s6 table vmbr0
ip route add 10.14.0.0/24 dev vmbr0 src 10.14.0.1 table vmbr0
ip rule add from 10.14.0.0/24 table vmbr0

# vmbr10
ip route add default via 10.0.0.1 dev enp0s6 table vmbr10
ip route add 10.140.0.0/24 dev vmbr10 src 10.140.0.1 table vmbr10
ip rule add from 10.140.0.0/24 table vmbr10

# vmbr11
ip route add default via 10.0.0.1 dev enp1s0 table vmbr11
ip route add 10.100.0.0/24 dev vmbr11 src 10.100.0.1 table vmbr11
ip rule add from 10.100.0.0/24 table vmbr11

# DHCP
ip route add default via 10.0.0.1 dev enp0s6 table dhcpnet
ip route add 10.200.200.0/24 dev DHCP src 10.200.200.1 table dhcpnet
ip rule add from 10.200.200.0/24 table dhcpnet
```

Не забыть сделать исполняемым:

```bash
chmod +x /etc/network/if-up.d/pbr.sh
```

---

✅ В итоге:

* SNAT чётко распределяет, какой внешний IP использовать;
* policy routing (ip rule + ip route) гарантирует, что ответка выйдет тем же интерфейсом;
* никаких MASQUERADE «по дефолту» не нужно.

---

