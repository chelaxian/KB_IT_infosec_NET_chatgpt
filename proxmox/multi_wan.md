
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

Лучший способ в Debian/Proxmox — оформить systemd-сервис, который будет поднимать все PBR-маршруты и правила iptables после ребута.

---

## 🔹 Шаг 1. Скрипт с маршрутами и SNAT

Создай файл `/usr/local/bin/pbr-routes.sh`:

```bash
#!/bin/bash
### PBR + SNAT config ###

# Очистка старых правил ip rule (чтобы не плодились)
ip rule flush
ip rule add from all lookup local
ip rule add from all lookup main
ip rule add from all lookup default

# Маршруты для таблиц

# vmbr1 (10.10.0.0/24 → enp1s0 → 10.0.0.105)
ip route add 10.10.0.0/24 dev vmbr1 src 10.10.0.1 table vmbr1
ip route add default via 10.0.0.1 dev enp1s0 table vmbr1
ip rule add from 10.10.0.0/24 table vmbr1

# vmbr0 (10.14.0.0/24 → enp0s6 → 10.0.0.103)
ip route add 10.14.0.0/24 dev vmbr0 src 10.14.0.1 table vmbr0
ip route add default via 10.0.0.1 dev enp0s6 table vmbr0
ip rule add from 10.14.0.0/24 table vmbr0

# vmbr10 (10.140.0.0/24 → enp0s6 → 10.0.0.104)
ip route add 10.140.0.0/24 dev vmbr10 src 10.140.0.1 table vmbr10
ip route add default via 10.0.0.1 dev enp0s6 table vmbr10
ip rule add from 10.140.0.0/24 table vmbr10

# vmbr11 (10.100.0.0/24 → enp1s0 → 10.0.0.106)
ip route add 10.100.0.0/24 dev vmbr11 src 10.100.0.1 table vmbr11
ip route add default via 10.0.0.1 dev enp1s0 table vmbr11
ip rule add from 10.100.0.0/24 table vmbr11

# DHCP (10.200.200.0/24 → enp0s6 → 10.0.0.103)
ip route add 10.200.200.0/24 dev DHCP src 10.200.200.1 table dhcpnet
ip route add default via 10.0.0.1 dev enp0s6 table dhcpnet
ip rule add from 10.200.200.0/24 table dhcpnet

# SNAT правила (чётко под свои IP)
iptables -t nat -F POSTROUTING
iptables -t nat -A POSTROUTING -s 10.200.200.0/24 -o enp0s6 -j SNAT --to-source 10.0.0.103
iptables -t nat -A POSTROUTING -s 10.10.0.0/24   -o enp1s0 -j SNAT --to-source 10.0.0.105
iptables -t nat -A POSTROUTING -s 10.14.0.0/24   -o enp0s6 -j SNAT --to-source 10.0.0.103
iptables -t nat -A POSTROUTING -s 10.100.0.0/24  -o enp1s0 -j SNAT --to-source 10.0.0.106
iptables -t nat -A POSTROUTING -s 10.140.0.0/24  -o enp0s6 -j SNAT --to-source 10.0.0.104
```

Делаем исполняемым:

```bash
chmod +x /usr/local/bin/pbr-routes.sh
```

---

## 🔹 Шаг 2. Systemd-unit

Создай файл `/etc/systemd/system/pbr-routes.service`:

```ini
[Unit]
Description=Policy Based Routing and SNAT setup
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pbr-routes.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

---

## 🔹 Шаг 3. Активируем

```bash
systemctl daemon-reexec
systemctl enable pbr-routes.service
systemctl start pbr-routes.service
```

---

## 🔹 Проверка после ребута

```bash
ip rule show
ip route show table vmbr1
iptables -t nat -L POSTROUTING -n -v
```

---

Таким образом:

* после загрузки сети systemd вызовет твой скрипт;
* будут восстановлены все `ip rule` и таблицы маршрутов;
* NAT-правила пересоберутся.

---

Окей, смотрю на дампы.

## Что вижу по состоянию

1. PBR-таблицы есть и заполнены правильно (`vmbr0/1/10/11/dhcpnet`).
2. `ip rule show` выглядит странно: приоритеты отображаются как `0`. Раньше были `32761…`. Похоже, твой скрипт с `ip rule flush` всё вычистил и добавил правила без явных приоритетов (или их порядок теперь не гарантирован). Это может ломать матч правил vs `main`.
3. В `POSTROUTING` снова торчат `MASQUERADE` (11–15). Они лишние и иногда перехватывают трафик вместо SNAT.
4. `rp_filter`: `all=2` (loose), но на всех интерфейсах `=0`. Лучше выставить `all=0`, чтобы исключить влияния (иногда ядро всё равно использует `all` как глобальный флаг проверки).

## Что сделать (шаги и команды)

### 1) Убрать лишние MASQUERADE

Оставляем только явные SNAT (правила 6–10). Удаляем 11–15 снизу вверх:

```bash
iptables -t nat -D POSTROUTING 15
iptables -t nat -D POSTROUTING 14
iptables -t nat -D POSTROUTING 13
iptables -t nat -D POSTROUTING 12
iptables -t nat -D POSTROUTING 11
```

### 2) Починить приоритеты `ip rule`

Сначала удалим текущие PBR-правила для подсетей, потом добавим с понятными приоритетами (меньше 32766, чтобы шли раньше `main`). Я предлагаю такой порядок:

* 10010: vmbr1 (10.10.0.0/24 → enp1s0)
* 10020: vmbr0 (10.14.0.0/24 → enp0s6)
* 10030: vmbr10 (10.140.0.0/24 → enp0s6)
* 10040: vmbr11 (10.100.0.0/24 → enp1s0)
* 10050: dhcpnet (10.200.200.0/24 → enp0s6)

```bash
# удалить старые (без приоритета)
ip rule del from 10.10.0.0/24 table vmbr1 2>/dev/null || true
ip rule del from 10.14.0.0/24 table vmbr0 2>/dev/null || true
ip rule del from 10.140.0.0/24 table vmbr10 2>/dev/null || true
ip rule del from 10.100.0.0/24 table vmbr11 2>/dev/null || true
ip rule del from 10.200.200.0/24 table dhcpnet 2>/dev/null || true

# поставить с приоритетами
ip rule add priority 10010 from 10.10.0.0/24   table vmbr1
ip rule add priority 10020 from 10.14.0.0/24   table vmbr0
ip rule add priority 10030 from 10.140.0.0/24  table vmbr10
ip rule add priority 10040 from 10.100.0.0/24  table vmbr11
ip rule add priority 10050 from 10.200.200.0/24 table dhcpnet

# убедиться
ip rule show
```

> Если увидишь «File exists», сначала `ip rule del priority <номер>` и повтори добавление.

### 3) Отключить глобальный rp\_filter (на всякий случай)

```bash
sysctl -w net.ipv4.conf.all.rp_filter=0
```

И в `/etc/sysctl.d/99-pbr.conf` добавь постоянные настройки:

```bash
cat >/etc/sysctl.d/99-pbr.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
EOF
sysctl --system
```

### 4) Очистить возможные «залипшие» conntrack-сессии (не обязательно, но полезно при смене NAT/маршрута)

Если установлен `conntrack`:

```bash
conntrack -D -s 10.10.0.0/24 2>/dev/null || true
conntrack -D -s 10.14.0.0/24 2>/dev/null || true
conntrack -D -s 10.100.0.0/24 2>/dev/null || true
conntrack -D -s 10.140.0.0/24 2>/dev/null || true
conntrack -D -s 10.200.200.0/24 2>/dev/null || true
```

### 5) Перепроверь, что маршруты в таблицах в порядке (у тебя уже ок):

```bash
ip route show table vmbr1
ip route show table vmbr0
ip route show table vmbr10
ip route show table vmbr11
ip route show table dhcpnet
```

Ожидаемо:

* `vmbr1`: `default via 10.0.0.1 dev enp1s0` и `10.10.0.0/24 dev vmbr1 src 10.10.0.1`
* `vmbr0`: `default via 10.0.0.1 dev enp0s6` и `10.14.0.0/24 dev vmbr0 src 10.14.0.1`
* и т.д.

### 6) Тесты

```bash
# на хосте:
ip route get 9.9.9.9 from 10.10.0.2
ip route get 9.9.9.9 from 10.14.0.2
ip route get 9.9.9.9 from 10.100.0.2
ip route get 9.9.9.9 from 10.140.0.2

# counters NAT
iptables -t nat -L POSTROUTING -n -v --line-numbers
```

И внутри соответствующих контейнеров:

```bash
ping -c 3 9.9.9.9
curl -s ifconfig.io
```

## Важная правка к нашему systemd-сервису

В твоём скрипте был `ip rule flush` — это **опасно** (можно снести служебные правила и поменять порядок). Лучше **не** делать flush. Вместо этого: точечно удаляй/добавляй нужные правила с приоритетом.

Обновлённый `/usr/local/bin/pbr-routes.sh` (без flush и с приоритетами):

```bash
#!/bin/bash
set -e

# Таблицы PBR должны существовать в /etc/iproute2/rt_tables:
# 210 vmbr1, 211 vmbr0, 212 vmbr10, 213 vmbr11, 214 dhcpnet

# Функция: безопасно добавить правило (сначала удалить, если есть)
safe_rule_add() {
  local prio="$1" net="$2" table="$3"
  ip rule del priority "$prio" 2>/dev/null || true
  ip rule add priority "$prio" from "$net" table "$table"
}

# Роуты в таблицах (идемпотентно)
ip route replace 10.10.0.0/24 dev vmbr1  src 10.10.0.1  table vmbr1
ip route replace default         via 10.0.0.1 dev enp1s0 table vmbr1

ip route replace 10.14.0.0/24 dev vmbr0  src 10.14.0.1  table vmbr0
ip route replace default         via 10.0.0.1 dev enp0s6 table vmbr0

ip route replace 10.140.0.0/24 dev vmbr10 src 10.140.0.1 table vmbr10
ip route replace default          via 10.0.0.1 dev enp0s6 table vmbr10

ip route replace 10.100.0.0/24 dev vmbr11 src 10.100.0.1 table vmbr11
ip route replace default          via 10.0.0.1 dev enp1s0 table vmbr11

ip route replace 10.200.200.0/24 dev DHCP   src 10.200.200.1 table dhcpnet
ip route replace default          via 10.0.0.1 dev enp0s6 table dhcpnet

# Правила с фиксированными приоритетами
safe_rule_add 10010 10.10.0.0/24   vmbr1
safe_rule_add 10020 10.14.0.0/24   vmbr0
safe_rule_add 10030 10.140.0.0/24  vmbr10
safe_rule_add 10040 10.100.0.0/24  vmbr11
safe_rule_add 10050 10.200.200.0/24 dhcpnet

# SNAT — чистим только наш «блок» (мягко): удалим MASQUERADE и гарантированно вставим SNAT
iptables -t nat -D POSTROUTING -s 10.14.0.0/24  -o enp0s6   -j MASQUERADE 2>/dev/null || true
iptables -t nat -D POSTROUTING -s 10.140.0.0/24 -o enp0s6:0 -j MASQUERADE 2>/dev/null || true
iptables -t nat -D POSTROUTING -s 10.10.0.0/24  -o enp1s0   -j MASQUERADE 2>/dev/null || true
iptables -t nat -D POSTROUTING -s 10.100.0.0/24 -o enp1s0:0 -j MASQUERADE 2>/dev/null || true
iptables -t nat -D POSTROUTING -s 10.200.200.0/24 -o enp0s6  -j MASQUERADE 2>/dev/null || true

# Убедимся, что нужные SNAT есть (idempotent – допустимы дубли, но лучше чисто)
for rule in \
 "-s 10.200.200.0/24 -o enp0s6  -j SNAT --to-source 10.0.0.103" \
 "-s 10.10.0.0/24   -o enp1s0  -j SNAT --to-source 10.0.0.105" \
 "-s 10.14.0.0/24   -o enp0s6  -j SNAT --to-source 10.0.0.103" \
 "-s 10.100.0.0/24  -o enp1s0  -j SNAT --to-source 10.0.0.106" \
 "-s 10.140.0.0/24  -o enp0s6  -j SNAT --to-source 10.0.0.104"; do
  # если нет — добавим в начало
  iptables -t nat -C POSTROUTING $rule 2>/dev/null || iptables -t nat -I POSTROUTING 1 $rule
done
```

И поправь unit (запуск после сети/бриджей), добавим доп. зависимости:

```ini
# /etc/systemd/system/pbr-routes.service
[Unit]
Description=Policy Based Routing and SNAT setup
After=network-online.target pve-cluster.service
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/pbr-routes.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Активировать:

```bash
systemctl daemon-reload
systemctl enable --now pbr-routes.service
```


