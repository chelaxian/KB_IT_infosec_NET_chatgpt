отлично, добили ✊
ниже — финальная, рабочая инструкция + автозагрузка. я сделал всё идемпотентно: повторный запуск ничего не сломает.

---

# Шаблон финальной конфигурации PBR + SNAT для двух uplink в одной подсети

## 0) Предпосылки (один раз)

* uplink-и:

  * `enp0s6`: 10.0.0.103 (/24), доп. 10.0.0.104
  * `enp1s0`: 10.0.0.105 (/24), доп. 10.0.0.106
  * общий GW: 10.0.0.1 (доступен по обоим интерфейсам)
* внутренние бриджи/сети:

  * `vmbr0`  → 10.14.0.0/24 (NAT через enp0s6 / 10.0.0.103)
  * `vmbr10` → 10.140.0.0/24 (NAT через enp0s6 / 10.0.0.104)
  * `vmbr1`  → 10.10.0.0/24 (NAT через enp1s0 / 10.0.0.105)
  * `vmbr11` → 10.100.0.0/24 (NAT через enp1s0 / 10.0.0.106)
  * `DHCP`   → 10.200.200.0/24 (NAT через enp0s6 / 10.0.0.103)

---

## 1) Маршрутные таблицы (rt\_tables)

Добавляем имена (если ещё не добавлены):

```bash
grep -q '^210 vmbr1$'  /etc/iproute2/rt_tables || echo '210 vmbr1'  | tee -a /etc/iproute2/rt_tables
grep -q '^211 vmbr0$'  /etc/iproute2/rt_tables || echo '211 vmbr0'  | tee -a /etc/iproute2/rt_tables
grep -q '^212 vmbr10$' /etc/iproute2/rt_tables || echo '212 vmbr10' | tee -a /etc/iproute2/rt_tables
grep -q '^213 vmbr11$' /etc/iproute2/rt_tables || echo '213 vmbr11' | tee -a /etc/iproute2/rt_tables
grep -q '^214 dhcpnet$' /etc/iproute2/rt_tables || echo '214 dhcpnet' | tee -a /etc/iproute2/rt_tables
```

---

## 2) Роуты в кастомных таблицах (всегда с `src`)

```bash
ip route replace 10.10.0.0/24   dev vmbr1  src 10.10.0.1    table vmbr1
ip route replace default via 10.0.0.1 dev enp1s0 src 10.0.0.105 table vmbr1

ip route replace 10.14.0.0/24   dev vmbr0  src 10.14.0.1    table vmbr0
ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.103 table vmbr0

ip route replace 10.140.0.0/24  dev vmbr10 src 10.140.0.1   table vmbr10
ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.104 table vmbr10

ip route replace 10.100.0.0/24  dev vmbr11 src 10.100.0.1   table vmbr11
ip route replace default via 10.0.0.1 dev enp1s0 src 10.0.0.106 table vmbr11

ip route replace 10.200.200.0/24 dev DHCP   src 10.200.200.1 table dhcpnet
ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.103 table dhcpnet
```

---

## 3) Policy rules — порядок и приоритеты

Правильный baseline для IPv4:

* `pref 0` → `local`
* **наши PBR**: iif и fwmark — 10005…10050
* `pref 32766` → `main`
* `pref 32767` → `default`

```bash
# фикс системных «нулевых» правил, если они вдруг появились
ip -4 rule del pref 0 lookup main 2>/dev/null || true
ip -4 rule del pref 0 lookup default 2>/dev/null || true
ip -4 rule add pref 0 from all lookup local 2>/dev/null || true
ip -4 rule add pref 32766 from all lookup main 2>/dev/null || true
ip -4 rule add pref 32767 from all lookup default 2>/dev/null || true

# iif (чтобы даже без меток маршрутизация была правильной)
ip -4 rule replace pref 10005 iif vmbr1  lookup vmbr1
ip -4 rule replace pref 10015 iif vmbr0  lookup vmbr0
ip -4 rule replace pref 10025 iif vmbr10 lookup vmbr10
ip -4 rule replace pref 10035 iif vmbr11 lookup vmbr11
ip -4 rule replace pref 10045 iif DHCP   lookup dhcpnet

# fwmark (для устойчивости и в случаях локального исходящего трафика контейнеров)
ip -4 rule replace pref 10010 fwmark 10 lookup vmbr1
ip -4 rule replace pref 10020 fwmark 14 lookup vmbr0
ip -4 rule replace pref 10030 fwmark 114 lookup vmbr10
ip -4 rule replace pref 10040 fwmark 110 lookup vmbr11
ip -4 rule replace pref 10050 fwmark 200 lookup dhcpnet
```

---

## 4) Mangle/CONNMARK — порядок

Всегда **restore первым** в PREROUTING/OUTPUT, затем — `MARK` и `CONNMARK save`:

```bash
# очистить mangle аккуратно (по желанию)
# iptables -t mangle -F

# restore-mark ДОЛЖЕН быть первым
iptables -t mangle -D PREROUTING -j CONNMARK --restore-mark 2>/dev/null || true
iptables -t mangle -I PREROUTING 1 -j CONNMARK --restore-mark
iptables -t mangle -D OUTPUT -j CONNMARK --restore-mark 2>/dev/null || true
iptables -t mangle -I OUTPUT 1 -j CONNMARK --restore-mark

# метим по подсетям (значения меток согласованы с правилами выше)
# vmbr1 → enp1s0
iptables -t mangle -C PREROUTING -s 10.10.0.0/24 -j MARK --set-mark 10 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.10.0.0/24 -j MARK --set-mark 10
iptables -t mangle -C PREROUTING -s 10.10.0.0/24 -j CONNMARK --save-mark 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.10.0.0/24 -j CONNMARK --save-mark

# vmbr0 → enp0s6
iptables -t mangle -C PREROUTING -s 10.14.0.0/24 -j MARK --set-mark 14 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.14.0.0/24 -j MARK --set-mark 14
iptables -t mangle -C PREROUTING -s 10.14.0.0/24 -j CONNMARK --save-mark 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.14.0.0/24 -j CONNMARK --save-mark

# vmbr10 → enp0s6
iptables -t mangle -C PREROUTING -s 10.140.0.0/24 -j MARK --set-mark 114 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.140.0.0/24 -j MARK --set-mark 114
iptables -t mangle -C PREROUTING -s 10.140.0.0/24 -j CONNMARK --save-mark 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.140.0.0/24 -j CONNMARK --save-mark

# vmbr11 → enp1s0
iptables -t mangle -C PREROUTING -s 10.100.0.0/24 -j MARK --set-mark 110 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.100.0.0/24 -j MARK --set-mark 110
iptables -t mangle -C PREROUTING -s 10.100.0.0/24 -j CONNMARK --save-mark 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.100.0.0/24 -j CONNMARK --save-mark

# dhcpnet → enp0s6
iptables -t mangle -C PREROUTING -s 10.200.200.0/24 -j MARK --set-mark 200 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.200.200.0/24 -j MARK --set-mark 200
iptables -t mangle -C PREROUTING -s 10.200.200.0/24 -j CONNMARK --save-mark 2>/dev/null \
  || iptables -t mangle -A PREROUTING -s 10.200.200.0/24 -j CONNMARK --save-mark
```

---

## 5) SNAT, без дублей MASQUERADE

```bash
# убрать потенциальные MASQUERADE, чтобы SNAT не перебивался
for r in \
 "-s 10.14.0.0/24  -o enp0s6" \
 "-s 10.140.0.0/24 -o enp0s6:0" \
 "-s 10.10.0.0/24  -o enp1s0" \
 "-s 10.100.0.0/24 -o enp1s0:0" \
 "-s 10.200.200.0/24 -o enp0s6" ; do
  iptables -t nat -D POSTROUTING $r -j MASQUERADE 2>/dev/null || true
done

# гарантируем SNAT
for rule in \
 "-s 10.14.0.0/24   -o enp0s6  -j SNAT --to-source 10.0.0.103" \
 "-s 10.140.0.0/24  -o enp0s6  -j SNAT --to-source 10.0.0.104" \
 "-s 10.10.0.0/24   -o enp1s0  -j SNAT --to-source 10.0.0.105" \
 "-s 10.100.0.0/24  -o enp1s0  -j SNAT --to-source 10.0.0.106" \
 "-s 10.200.200.0/24 -o enp0s6 -j SNAT --to-source 10.0.0.103" ; do
  iptables -t nat -C POSTROUTING $rule 2>/dev/null || iptables -t nat -I POSTROUTING 1 $rule
done
```

---

## 6) sysctl

```bash
cat >/etc/sysctl.d/99-pbr.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
EOF
sysctl --system
```

---

## 7) Проверка

```bash
ip -4 rule show
ip route show table vmbr1; ip route show table vmbr0
iptables -t mangle -L PREROUTING -n -v --line-numbers
iptables -t nat -L POSTROUTING -n -v --line-numbers

ip route flush cache
ip route get 9.9.9.9 from 10.10.0.2 iif vmbr1
ip route get 9.9.9.9 from 10.14.0.2 iif vmbr0
```

---

# Автозагрузка (systemd)

## Скрипт `/usr/local/sbin/pbr-setup.sh`

```bash
#!/bin/bash
set -euo pipefail

# ---------- sysctl ----------
apply_sysctl() {
  install -m 0644 /dev/stdin /etc/sysctl.d/99-pbr.conf <<'EOF'
net.ipv4.ip_forward=1
net.ipv4.conf.all.rp_filter=0
net.ipv4.conf.default.rp_filter=0
EOF
  sysctl --system >/dev/null
}

# ---------- rt_tables ----------
ensure_rt_tables() {
  add() { grep -q "^$1[[:space:]]\+$2$" /etc/iproute2/rt_tables || echo "$1 $2" >>/etc/iproute2/rt_tables; }
  add 210 vmbr1
  add 211 vmbr0
  add 212 vmbr10
  add 213 vmbr11
  add 214 dhcpnet
}

# ---------- routes (with src) ----------
apply_routes() {
  ip route replace 10.10.0.0/24    dev vmbr1  src 10.10.0.1    table vmbr1
  ip route replace default via 10.0.0.1 dev enp1s0 src 10.0.0.105 table vmbr1

  ip route replace 10.14.0.0/24    dev vmbr0  src 10.14.0.1    table vmbr0
  ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.103 table vmbr0

  ip route replace 10.140.0.0/24   dev vmbr10 src 10.140.0.1   table vmbr10
  ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.104 table vmbr10

  ip route replace 10.100.0.0/24   dev vmbr11 src 10.100.0.1   table vmbr11
  ip route replace default via 10.0.0.1 dev enp1s0 src 10.0.0.106 table vmbr11

  ip route replace 10.200.200.0/24 dev DHCP   src 10.200.200.1 table dhcpnet
  ip route replace default via 10.0.0.1 dev enp0s6 src 10.0.0.103 table dhcpnet
}

# ---------- rules ----------
apply_rules() {
  # fix system rules
  ip -4 rule del pref 0 lookup main 2>/dev/null || true
  ip -4 rule del pref 0 lookup default 2>/dev/null || true
  ip -4 rule add pref 0 from all lookup local 2>/dev/null || true
  ip -4 rule add pref 32766 from all lookup main 2>/dev/null || true
  ip -4 rule add pref 32767 from all lookup default 2>/dev/null || true

  # iif first
  ip -4 rule replace pref 10005 iif vmbr1  lookup vmbr1
  ip -4 rule replace pref 10015 iif vmbr0  lookup vmbr0
  ip -4 rule replace pref 10025 iif vmbr10 lookup vmbr10
  ip -4 rule replace pref 10035 iif vmbr11 lookup vmbr11
  ip -4 rule replace pref 10045 iif DHCP   lookup dhcpnet

  # fwmark rules
  ip -4 rule replace pref 10010 fwmark 10  lookup vmbr1
  ip -4 rule replace pref 10020 fwmark 14  lookup vmbr0
  ip -4 rule replace pref 10030 fwmark 114 lookup vmbr10
  ip -4 rule replace pref 10040 fwmark 110 lookup vmbr11
  ip -4 rule replace pref 10050 fwmark 200 lookup dhcpnet
}

# ---------- mangle/CONNMARK ----------
apply_mangle() {
  # restore first
  iptables -t mangle -D PREROUTING -j CONNMARK --restore-mark 2>/dev/null || true
  iptables -t mangle -I PREROUTING 1 -j CONNMARK --restore-mark
  iptables -t mangle -D OUTPUT -j CONNMARK --restore-mark 2>/dev/null || true
  iptables -t mangle -I OUTPUT 1 -j CONNMARK --restore-mark

  # helper to ensure rule existence
  ensure() { iptables -t mangle -C PREROUTING "$@" 2>/dev/null || iptables -t mangle -A PREROUTING "$@"; }

  ensure -s 10.10.0.0/24   -j MARK --set-mark 10
  ensure -s 10.10.0.0/24   -j CONNMARK --save-mark
  ensure -s 10.14.0.0/24   -j MARK --set-mark 14
  ensure -s 10.14.0.0/24   -j CONNMARK --save-mark
  ensure -s 10.140.0.0/24  -j MARK --set-mark 114
  ensure -s 10.140.0.0/24  -j CONNMARK --save-mark
  ensure -s 10.100.0.0/24  -j MARK --set-mark 110
  ensure -s 10.100.0.0/24  -j CONNMARK --save-mark
  ensure -s 10.200.200.0/24 -j MARK --set-mark 200
  ensure -s 10.200.200.0/24 -j CONNMARK --save-mark
}

# ---------- SNAT (и снос лишних MASQUERADE) ----------
apply_snat() {
  # drop MASQUERADE duplicates that may appear
  delm() { iptables -t nat -D POSTROUTING "$@" 2>/dev/null || true; }
  delm -s 10.14.0.0/24    -o enp0s6   -j MASQUERADE
  delm -s 10.140.0.0/24   -o enp0s6:0 -j MASQUERADE
  delm -s 10.10.0.0/24    -o enp1s0   -j MASQUERADE
  delm -s 10.100.0.0/24   -o enp1s0:0 -j MASQUERADE
  delm -s 10.200.200.0/24 -o enp0s6   -j MASQUERADE

  ensure_nat() { iptables -t nat -C POSTROUTING "$@" 2-/dev/null || iptables -t nat -I POSTROUTING 1 "$@"; }

  ensure_nat -s 10.14.0.0/24    -o enp0s6   -j SNAT --to-source 10.0.0.103
  ensure_nat -s 10.140.0.0/24   -o enp0s6   -j SNAT --to-source 10.0.0.104
  ensure_nat -s 10.10.0.0/24    -o enp1s0   -j SNAT --to-source 10.0.0.105
  ensure_nat -s 10.100.0.0/24   -o enp1s0   -j SNAT --to-source 10.0.0.106
  ensure_nat -s 10.200.200.0/24 -o enp0s6   -j SNAT --to-source 10.0.0.103
}

main() {
  apply_sysctl
  ensure_rt_tables
  apply_routes
  apply_rules
  apply_mangle
  apply_snat
  ip route flush cache || true
}
main
```

```bash
chmod +x /usr/local/sbin/pbr-setup.sh
```

## Юнит `/etc/systemd/system/pbr-setup.service`

```ini
[Unit]
Description=Policy Based Routing & NAT setup (multi-uplink same subnet)
After=network-online.target pve-firewall.service
Wants=network-online.target pve-firewall.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/pbr-setup.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
systemctl daemon-reload
systemctl enable --now pbr-setup.service
```

---

## Быстрый чек-лист после перезагрузки

```bash
hostname; date
ip -4 rule show
ip route show table vmbr1; ip route show table vmbr0; ip route show table vmbr10; ip route show table vmbr11; ip route show table dhcpnet
iptables -t mangle -L PREROUTING -n -v --line-numbers
iptables -t nat -L POSTROUTING -n -v --line-numbers

ip route flush cache
ip route get 9.9.9.9 from 10.10.0.2 iif vmbr1
ip route get 9.9.9.9 from 10.14.0.2 iif vmbr0
```

ожидаемо:

* трафик 10.10.0.0/24 идёт через **enp1s0** (внешний IP 80.225.89.177),
* трафик 10.14.0.0/24 — через **enp0s6** (внешний IP 158.180.231.91),
* остальные — по своим uplink согласно таблицам.

если захочешь — добавим экспорт в `/etc/iptables/rules.v4` (через `iptables-save`/`iptables-restore`), но c systemd-скриптом уже всё стабильно и воспроизводимо.
