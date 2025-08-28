Отлично 🚀! Тогда я соберу **полную пошаговую инструкцию**, чтобы в будущем у тебя было всё в одном месте: от Oracle Cloud до LXC и Docker.

---

# Полная настройка IPv6 (Oracle Cloud → Proxmox (PVE) → LXC → Docker)

## 1. Oracle Cloud (VNIC и подсети)

1. Включить IPv6 в настройках VCN и Subnet (в Oracle Console).

   * Указать **IPv6 CIDR block** (например, `2603:c027:d:f500::/56`).
   * Для VNIC хоста (PVE) включить **IPv6 auto-configuration**.
2. В Security List добавить правила:

   * **Egress**: разрешить `::/0` → `All Protocols`.
   * **Ingress**: разрешить `::/0` → нужные порты (например, 22/tcp, 80/tcp, 443/tcp).

---

## 2. Proxmox (PVE host)

### 2.1 Сеть

В `/etc/network/interfaces` (или через GUI) настроен мост **vmbr0**:

```bash
auto vmbr0
iface vmbr0 inet static
    address 10.14.0.1/24

iface vmbr0 inet6 static
    address 2603:c027:d:f500::1/64
```

Физический интерфейс `enp2s0` имеет публичный IPv6 (от Oracle) и служит WAN.

### 2.2 sysctl

В `/etc/sysctl.conf`:

```bash
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1

# RA принимать только на внешнем интерфейсе
net.ipv6.conf.enp2s0.accept_ra=2
net.ipv6.conf.vmbr0.accept_ra=0

# Proxy NDP
net.ipv6.conf.enp2s0.proxy_ndp=1
net.ipv6.conf.vmbr0.proxy_ndp=1
```

Применить:

```bash
sysctl -p
```

### 2.3 ndppd (для Proxy NDP, если нужен прямой IPv6 в LXC)

`/etc/ndppd.conf`:

```conf
proxy enp2s0 {
    rule 2603:c027:d:f500::/64 {
        auto
    }
}
```

и перезапуск:

```bash
systemctl enable ndppd --now
```

### 2.4 NAT66 (упрощённый вариант)

Чтобы контейнеры всегда ходили наружу (без выделения им реальных адресов):

```bash
ip6tables -t nat -A POSTROUTING -s 2603:c027:d:f500::/64 -o enp2s0 -j MASQUERADE
```

Сохраняем:

```bash
ip6tables-save > /etc/ip6tables.rules
```

(поднимается через `netfilter-persistent`).

---

## 3. Контейнер LXC (например, `amnezia-tg`)

В конфиге контейнера (`/etc/pve/lxc/103.conf`):

```conf
net0: name=eth0,bridge=vmbr0,firewall=1,gw=10.14.0.1,hwaddr=BC:24:11:3B:49:6E,\
ip=10.14.0.4/24,ip6=2603:c027:d:f500::101/64,gw6=2603:c027:d:f500::1,type=veth
```

После запуска в контейнере:

```bash
ifconfig eth0
```

Видим IPv4 (`10.14.0.4`) и IPv6 (`2603:c027:d:f500::101`).

Проверка:

```bash
ping -6 google.com
```

---

## 4. Docker внутри LXC

Есть 2 способа прокинуть IPv6 дальше.

### 4.1 NAT66 и для Docker

Если LXC сидит за NAT66, то Docker будет работать «из коробки».
В `daemon.json` (обычно `/etc/docker/daemon.json`) можно добавить:

```json
{
  "ipv6": true,
  "fixed-cidr-v6": "fd00:dead:beef::/48"
}
```

Это даст Docker контейнерам **ULA IPv6**, а исходящие пойдут наружу через NAT66.

### 4.2 Прямой IPv6 в Docker контейнер

Если хочешь, чтобы **Docker-контейнеры имели реальные публичные IPv6**:

1. В LXC сделать macvlan-сеть, которая пробрасывает интерфейс контейнера напрямую в `vmbr0`.
2. В `docker-compose.yml` или при запуске указать:

```yaml
networks:
  default:
    driver: macvlan
    driver_opts:
      parent: eth0
    ipam:
      config:
        - subnet: "2603:c027:d:f500::/64"
          gateway: "2603:c027:d:f500::1"
```

3. Назначить IPv6 контейнеру вручную, например `2603:c027:d:f500::201`.

---

## 5. Что работает сейчас у тебя

* Oracle Cloud раздаёт публичный `/56` IPv6.
* PVE получил IPv6 на `enp2s0` и на `vmbr0`.
* Включили IPv6 форвардинг + Proxy NDP.
* Для упрощения включили NAT66, и теперь **LXC ходит в интернет по IPv6 через адрес хоста**.
* В контейнере LXC IPv6 работает на исходящие запросы.

---

## 6. Следующий шаг: прокинуть IPv6 в Docker

* Если нужны только исходящие → достаточно NAT66 (уже работает).
* Если нужен публичный IPv6 прямо в Docker → делаем **macvlan** и выделяем адрес из подсети (`2603:c027:d:f500::/64`).

---

👉 Хочешь, я соберу тебе готовый **пример `docker-compose.yml`** с IPv6 (оба варианта: NAT66 и прямой публичный IPv6)?
