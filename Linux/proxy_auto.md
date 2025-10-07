# 0) Предпосылки

* Root-доступ на новом сервере.

* Узнай IP интерфейса, на котором будет слушать Squid (далее используем переменную `$IP`):

  ```bash
  ip -4 addr show | awk '/inet /{print $2,$NF}'
  ```

  Пример: возьмём `10.0.0.10`.

* Наши целевые параметры:

  ```
  PROXY_TYPE=http
  PROXY_IP=10.0.0.10         # слушать на этом IP
  PROXY_PORT=3128
  PROXY_USER=user
  PROXY_PASSWORD='passw0rd!'
  ```

---

# 1) Установка пакетов

```bash
apt-get update
apt-get install -y squid apache2-utils curl dos2unix
```

---

# 2) Настройка BasicAuth для Squid

Создаём файл паролей и пользователя:

```bash
htpasswd -c /etc/squid/passwd user
# введи пароль: passw0rd!
chmod 640 /etc/squid/passwd
chown root:squid /etc/squid/passwd 2>/dev/null || true
```

> Если хочешь без интерактива:
> `printf "user:$(openssl passwd -apr1 'passw0rd!')\n" > /etc/squid/passwd`

---

# 3) Конфиг Squid

Сделаем минимально нужный, повторяющий твою рабочую логику.

**/etc/squid/squid.conf**

```conf
# --- ACL по IP (доступ без пароля) ---
acl allowed_ip src 192.168.0.0/16
acl allowed_ip src 172.16.0.0/12
acl allowed_ip src 10.0.0.0/8
acl allowed_ip src 79.72.31.231/32
acl allowed_ip src 193.123.84.19/32
acl allowed_ip src 143.47.224.96/32
acl allowed_ip src 2603:c027:d:f57e:0:3e61:7d20:aa24

# --- Basic Auth ---
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/squid/passwd
auth_param basic realm "Proxy Authentication Required"
auth_param basic credentialsttl 2 hours
auth_param basic casesensitive off
acl authenticated proxy_auth REQUIRED

# --- Разрешённые порты и методы ---
acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 443
acl Safe_ports port 1025-65535
acl CONNECT method CONNECT

# --- Политики доступа ---
http_access allow CONNECT SSL_ports
http_access allow CONNECT Safe_ports
http_access allow allowed_ip           # без пароля по белым сетям
http_access allow authenticated        # всем остальным с паролем
http_access allow localhost            # локальному хосту
http_access deny all

# --- DNS (можешь заменить на свои) ---
dns_nameservers 8.8.8.8 8.8.4.4

# --- Сокет прослушивания (важно: на локальном IP) ---
http_port 10.0.0.10:3128
```

Проверка синтаксиса и запуск:

```bash
squid -k parse
systemctl enable --now squid
systemctl status squid --no-pager
ss -ltnp | grep 3128
```

Ожидаем LISTEN на `10.0.0.10:3128` процессом `squid`.

---

# 4) Конфиг healthcheck (ядро)

Создаём файл окружения для чека:

**/etc/default/squid-healthcheck**

```bash
# Proxy settings
PROXY_TYPE="http"
PROXY_IP="10.0.0.10"
PROXY_PORT=3128
PROXY_USER="user"
PROXY_PASSWORD="passw0rd!"

# Healthcheck tuning
MAX_FAILS=3
TIMEOUT=8
SVC_NAME="squid"

# Probe targets (можешь заменить на корпоративные)
URL_HTTP="http://ya.ru"
URL_HTTPS="https://example.com"
```

---

# 5) Скрипт healthcheck (с интерактивным выводом)

**/usr/local/bin/squid-healthcheck.sh**

```bash
#!/bin/bash
# Proxy/Squid health-check with human-friendly interactive output
# - Interactive (TTY or VERBOSE=1): печатает понятный отчёт
# - Non-interactive (systemd): тихо, но логирует через logger
# - Supports http/https/socks4/socks5/socks5h
# - Restarts $SVC_NAME after N consecutive failures
set -euo pipefail
VERSION="1.3.1"

CONFIG="/etc/default/squid-healthcheck"
[[ -f "$CONFIG" ]] && source "$CONFIG"

PROXY_TYPE="${PROXY_TYPE:-http}"
PROXY_IP="${PROXY_IP:-127.0.0.1}"
PROXY_PORT="${PROXY_PORT:-3128}"
PROXY_USER="${PROXY_USER:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

MAX_FAILS="${MAX_FAILS:-3}"
TIMEOUT="${TIMEOUT:-8}"
SVC_NAME="${SVC_NAME:-squid}"
URL_HTTP="${URL_HTTP:-http://example.com}"
URL_HTTPS="${URL_HTTPS:-https://example.com}"

STATE_DIR="/run/squid-health"
STATE_FILE="${STATE_DIR}/fail_count"

CURL="$(command -v curl || echo /usr/bin/curl)"
LOGGER="$(command -v logger || echo /usr/bin/logger)"
SYSTEMCTL="$(command -v systemctl || echo /bin/systemctl)"
mkdir -p "$STATE_DIR"; chmod 755 "$STATE_DIR"

# Mode detection
IS_TTY=0; [[ -t 1 ]] && IS_TTY=1
VERBOSE="${VERBOSE:-$IS_TTY}"
NO_COLOR="${NO_COLOR:-0}"

# Colors
if [[ "$VERBOSE" -eq 1 && "$NO_COLOR" -eq 0 ]] && command -v tput >/dev/null 2>&1 && [[ $(tput colors) -ge 8 ]]; then
  C_RESET="$(tput sgr0)"; C_DIM="$(tput dim)"; C_BOLD="$(tput bold)"
  C_GREEN="$(tput setaf 2)"; C_YELLOW="$(tput setaf 3)"; C_RED="$(tput setaf 1)"; C_CYAN="$(tput setaf 6)"
else
  C_RESET=""; C_DIM=""; C_BOLD=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_CYAN=""
fi

log() { "$LOGGER" -t squid-healthcheck -- "$*"; }
say() { [[ "$VERBOSE" -eq 1 ]] && echo -e "$*"; }

# Validate proxy type
case "$PROXY_TYPE" in
  http|https|socks4|socks5|socks5h) ;;
  *) log "Unsupported PROXY_TYPE='$PROXY_TYPE', fallback to http"; PROXY_TYPE="http";;
esac

PROXY_URL="${PROXY_TYPE}://${PROXY_IP}:${PROXY_PORT}"

# curl base opts (array -> корректное экранирование)
CURL_BASE=(-x "$PROXY_URL" -sS -m "$TIMEOUT" -o /dev/null)
if [[ -n "$PROXY_USER" ]]; then
  CURL_BASE+=( --proxy-user "${PROXY_USER}:${PROXY_PASSWORD}" )
fi

# Helpers
is_code_ok() { [[ "$1" =~ ^2[0-9]{2}$ || "$1" =~ ^3[0-9]{2}$ ]]; }

probe_once() {
  local url="$1"
  local out
  out="$("$CURL" "${CURL_BASE[@]}" -w "%{http_code} %{time_connect} %{time_appconnect} %{time_starttransfer} %{time_total}" "$url" 2>/dev/null || true)"
  [[ -z "$out" ]] && echo "000 0 0 0 0" || echo "$out"
}

tcp_port_open() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 2 bash -c "</dev/tcp/$PROXY_IP/$PROXY_PORT" >/dev/null 2>&1 && return 0 || return 1
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -ltnH "sport = :$PROXY_PORT" | grep -q . && return 0 || return 1
  fi
  return 2
}

# Header (interactive)
if [[ "$VERBOSE" -eq 1 ]]; then
  say "${C_BOLD}Proxy Health-Check v${VERSION}${C_RESET}"
  say "${C_DIM}Host: ${C_RESET}$(hostname)    ${C_DIM}Now: ${C_RESET}$(date '+%Y-%m-%d %H:%M:%S %Z')"
  say ""
  say "${C_BOLD}Parameters:${C_RESET}"
  say "  Proxy type      : ${C_CYAN}${PROXY_TYPE}${C_RESET}"
  say "  Proxy address   : ${C_CYAN}${PROXY_IP}:${PROXY_PORT}${C_RESET}"
  if [[ -n "$PROXY_USER" ]]; then
    pwlen=${#PROXY_PASSWORD}
    masked="$(printf '%*s' "$pwlen" '' | tr ' ' '*')"
    say "  Proxy auth      : user='${C_CYAN}${PROXY_USER}${C_RESET}' pass='${C_CYAN}${masked}${C_RESET}'"
  else
    say "  Proxy auth      : ${C_YELLOW}none${C_RESET}"
  fi
  say "  Timeout         : ${C_CYAN}${TIMEOUT}s${C_RESET}"
  say "  Service name    : ${C_CYAN}${SVC_NAME}${C_RESET}"
  say "  Max fails       : ${C_CYAN}${MAX_FAILS}${C_RESET}"
  say "  Probe URLs      : ${C_CYAN}${URL_HTTP}${C_RESET} (HTTP), ${C_CYAN}${URL_HTTPS}${C_RESET} (HTTPS)"
  say ""
fi

# Start service if down
if ! $SYSTEMCTL is-active --quiet "$SVC_NAME"; then
  log "Service $SVC_NAME is not active; restarting"
  $SYSTEMCTL restart "$SVC_NAME" || true
  sleep 2
fi

# Port state (interactive)
if [[ "$VERBOSE" -eq 1 ]]; then
  if tcp_port_open; then
    say "  TCP ${PROXY_IP}:${PROXY_PORT} : ${C_GREEN}LISTEN (reachable)${C_RESET}"
  else
    rc=$?
    [[ $rc -eq 1 ]] && say "  TCP ${PROXY_IP}:${PROXY_PORT} : ${C_RED}NOT REACHABLE${C_RESET}" || say "  TCP ${PROXY_IP}:${PROXY_PORT} : ${C_YELLOW}UNKNOWN${C_RESET}"
  fi
  say ""
fi

# Probes
read -r H_CODE H_TCONN H_TTLS H_TTFB H_TTOT <<<"$(probe_once "$URL_HTTP")"
read -r S_CODE S_TCONN S_TTLS S_TTFB S_TTOT <<<"$(probe_once "$URL_HTTPS")"

# Sanitized commands (interactive)
if [[ "$VERBOSE" -eq 1 ]]; then
  SAN_AUTH=""; [[ -n "$PROXY_USER" ]] && SAN_AUTH="--proxy-user ${PROXY_USER}:******"
  say "${C_BOLD}Commands (sanitized):${C_RESET}"
  say "  curl -x ${PROXY_URL} ${SAN_AUTH} -m ${TIMEOUT} -o /dev/null -w '%{http_code} ...' ${URL_HTTP}"
  say "  curl -x ${PROXY_URL} ${SAN_AUTH} -m ${TIMEOUT} -o /dev/null -w '%{http_code} ...' ${URL_HTTPS}"
  say ""
fi

# Decision
fail_count="$(cat "$STATE_FILE" 2>/dev/null || echo 0)"
healthy=0
is_code_ok "$H_CODE" && healthy=1 || true
is_code_ok "$S_CODE" && healthy=1 || true

if [[ $healthy -eq 1 ]]; then
  [[ "$fail_count" != "0" ]] && log "Proxy recovered: http=$H_CODE https=$S_CODE"
  echo 0 >"$STATE_FILE"
  if [[ "$VERBOSE" -eq 1 ]]; then
    say "${C_BOLD}Results:${C_RESET}"
    say "  HTTP   ${URL_HTTP}        -> code=${C_CYAN}${H_CODE}${C_RESET}  connect=${H_TCONN}s  tls=${H_TTLS}s  ttfb=${H_TTFB}s  total=${H_TTOT}s"
    say "  HTTPS  ${URL_HTTPS}       -> code=${C_CYAN}${S_CODE}${C_RESET}  connect=${S_TCONN}s  tls=${S_TTLS}s  ttfb=${S_TTFB}s  total=${S_TTOT}s"
    say ""
    say "${C_GREEN}${C_BOLD}STATUS: HEALTHY${C_RESET}"
  fi
  exit 0
else
  fail_count=$((fail_count + 1))
  echo "$fail_count" >"$STATE_FILE"
  log "Proxy unhealthy (${fail_count}/${MAX_FAILS}): http=$H_CODE https=$S_CODE"
  if [[ "$VERBOSE" -eq 1 ]]; then
    say "${C_BOLD}Results:${C_RESET}"
    say "  HTTP   ${URL_HTTP}        -> code=${C_RED}${H_CODE}${C_RESET}  connect=${H_TCONN}s  tls=${H_TTLS}s  ttfb=${H_TTFB}s  total=${H_TTOT}s"
    say "  HTTPS  ${URL_HTTPS}       -> code=${C_RED}${S_CODE}${C_RESET}  connect=${S_TCONN}s  tls=${S_TTLS}s  ttfb=${S_TTFB}s  total=${S_TTOT}s"
    say ""
    if (( fail_count < MAX_FAILS )); then
      say "${C_YELLOW}${C_BOLD}STATUS: UNHEALTHY${C_RESET} — consecutive fails ${fail_count}/${MAX_FAILS} (no restart yet)"
    fi
  fi
  if (( fail_count >= MAX_FAILS )); then
    log "Restarting $SVC_NAME after ${fail_count} consecutive failures"
    $SYSTEMCTL restart "$SVC_NAME" || true
    echo 0 >"$STATE_FILE"
    [[ "$VERBOSE" -eq 1 ]] && say "${C_RED}${C_BOLD}ACTION: RESTART ${SVC_NAME}${C_RESET}"
  fi
fi

exit 0
```

Права:

```bash
dos2unix /usr/local/bin/squid-healthcheck.sh 2>/dev/null || true
chmod 0755 /usr/local/bin/squid-healthcheck.sh
```

---

# 6) systemd unit + timer

**/etc/systemd/system/squid-healthcheck.service**

```ini
[Unit]
Description=Proxy health-check (oneshot) with auto-restart
After=network-online.target squid.service
Wants=network-online.target

[Service]
Type=oneshot
EnvironmentFile=-/etc/default/squid-healthcheck
ExecStart=/usr/local/bin/squid-healthcheck.sh
User=root
Group=root
Nice=10
SuccessExitStatus=0

[Install]
WantedBy=multi-user.target
```

**/etc/systemd/system/squid-healthcheck.timer**

```ini
[Unit]
Description=Run proxy health-check every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
AccuracySec=30s
RandomizedDelaySec=10s
Unit=squid-healthcheck.service
Persistent=true

[Install]
WantedBy=timers.target
```

Активация:

```bash
systemctl daemon-reload
systemctl enable --now squid-healthcheck.timer
systemctl status squid-healthcheck.timer --no-pager
```

---

# 7) Проверка

* Ручной отчёт (человеко-читаемо):

  ```bash
  VERBOSE=1 /usr/local/bin/squid-healthcheck.sh
  ```
* Таймер тикает:

  ```bash
  systemctl list-timers --all | grep -i squid-healthcheck
  ```
* Логи:

  ```bash
  journalctl -u squid-healthcheck.service -n 50 --no-pager
  journalctl -t squid-healthcheck --since "15 min ago" --no-pager
  ```
* Интеграционный тест авто-рестарта:

  ```bash
  systemctl stop squid
  sleep 70
  journalctl -t squid-healthcheck --since "2 min ago" --no-pager
  systemctl status squid
  ```

---

# 8) (Опционально) Автоперезапуск самого демона при падении процесса

```bash
systemctl edit squid
```

Вставить:

```ini
[Service]
Restart=always
RestartSec=5s
StartLimitIntervalSec=0
```

Применить:

```bash
systemctl daemon-reload
systemctl restart squid
```

---

# 9) (Опционально) Фаервол

nftables/iptables/ufw — открой порт **только** нужным сетям (или вообще не открывай наружу, если прокси только для LAN).

Пример ufw:

```bash
ufw allow from 10.0.0.0/8 to any port 3128 proto tcp
ufw allow from 192.168.0.0/16 to any port 3128 proto tcp
ufw allow from 172.16.0.0/12 to any port 3128 proto tcp
# при необходимости отдельные адреса:
ufw allow from 79.72.31.231 to any port 3128 proto tcp
```

---

# 10) Быстрый self-check чеклист

```bash
# 1) слушает ли порт?
ss -ltnp | grep 3128

# 2) работает ли auth?
curl -x http://10.0.0.10:3128 --proxy-user user:'passw0rd!' -I http://example.com

# 3) healthcheck вручную:
VERBOSE=1 /usr/local/bin/squid-healthcheck.sh

# 4) таймер:
systemctl list-timers --all | grep -i squid-healthcheck

# 5) логи:
journalctl -u squid-healthcheck.service -n 30 --no-pager
journalctl -t squid-healthcheck --since "10 min ago" --no-pager
```

Ок, вот **продолжение инструкции** для варианта c **SOCKS5 (Dante)**. Вставляй этот раздел сразу после предыдущего гайда про Squid — он полностью совместим с уже установленным `healthcheck`.

---

# B) SOCKS5-прокси на Dante + healthcheck

## B.1) Переменные окружения (под себя)

```bash
IP="10.0.0.100"      # IP интерфейса контейнера/хоста, где будет слушать SOCKS5
PORT="1080"
USER="user"
PASS="passw0rd!"
SVC="danted"        # у некоторых пакетов юнит зовётся "sockd": проверь ниже
```

Проверь IP:

```bash
hostname -I
ip -4 addr show | awk '/inet /{print $2,$NF}'
```

## B.2) Установка Dante

```bash
apt-get update
apt-get install -y dante-server curl dos2unix
# выяснить точное имя systemd-юнита:
systemctl status danted || systemctl status sockd || true
# при необходимости:
# SVC="sockd"
```

## B.3) Создать системного пользователя для auth

```bash
id -u "$USER" >/dev/null 2>&1 || useradd -M -s /usr/sbin/nologin "$USER"
echo "${USER}:${PASS}" | chpasswd
```

## B.4) Конфиг `/etc/danted.conf` (минимальный рабочий)

Определим внешний интерфейс для исходящих соединений:

```bash
EXT_IF="$(ip -o -4 route show to default | awk '{print $5}' | head -1)"
echo "EXT_IF=${EXT_IF}"
```

Сгенерируем конфиг:

```bash
cat >/etc/danted.conf <<EOF
logoutput: syslog

internal: ${IP} port = ${PORT}
external: ${EXT_IF}

user.privileged: root
user.notprivileged: nobody
user.libwrap: nobody

# Клиентские методы (к самому демону) и методы SOCKS:
clientmethod: none
socksmethod: username   # требуем user/pass (системные пользователи)

# Кто может подключаться к SOCKS (источники):
client pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  log: connect disconnect error
}

# Что разрешаем через SOCKS (наружу):
socks pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  command: connect
  protocol: tcp
  log: connect disconnect error
}

# Явный запрет остального
socks block {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  log: error
}
EOF
```

Старт и автозапуск:

```bash
systemctl daemon-reload
systemctl enable --now "${SVC}"
systemctl status "${SVC}" --no-pager
ss -ltnp | grep ":${PORT}\b" || journalctl -u "${SVC}" -n 50 --no-pager
```

Ожидаем `LISTEN ${IP}:${PORT}` процессом `danted`/`sockd`.

## B.5) Привязка healthcheck к Dante (SOCKS5H)

> **Важно:** для корректного DNS через прокси используем `socks5h` (DNS-резолвинг на стороне прокси).

Файл окружения:

```bash
cat >/etc/default/squid-healthcheck <<EOF
PROXY_TYPE="socks5h"
PROXY_IP="${IP}"
PROXY_PORT=${PORT}
PROXY_USER="${USER}"
PROXY_PASSWORD="${PASS}"

MAX_FAILS=3
TIMEOUT=8
SVC_NAME="${SVC}"

URL_HTTP="http://ya.ru"
URL_HTTPS="https://example.com"
EOF
```

(Если скрипт и таймер уже стоят с прошлого раздела — этот шаг просто их перепривяжет к Dante. Если нет — поставь из предыдущей инструкции разделы «скрипт», «service», «timer».)

Перечитать юниты (если впервые ставишь):

```bash
systemctl daemon-reload
systemctl enable --now squid-healthcheck.timer
```

## B.6) Проверка (ручная и через systemd)

Ручной «человеческий» отчёт:

```bash
VERBOSE=1 /usr/local/bin/squid-healthcheck.sh
```

Ожидаем:

* `TCP ${IP}:${PORT} : LISTEN (reachable)`
* `STATUS: HEALTHY`, коды `HTTP=302/200`, `HTTPS=200`

Таймер тикает:

```bash
systemctl list-timers --all | grep -i squid-healthcheck
```

Логи:

```bash
journalctl -u squid-healthcheck.service -n 30 --no-pager
journalctl -t squid-healthcheck --since "15 min ago" --no-pager
```

Интеграционный тест авто-рестарта:

```bash
systemctl stop "${SVC}"
sleep 70
journalctl -t squid-healthcheck --since "2 min ago" --no-pager
systemctl status "${SVC}"
```

## B.7) Типовые узкие места (быстро)

* `code=000` при `LISTEN` → почти всегда **DNS не через прокси** → ставь `PROXY_TYPE="socks5h"`.
* `authentication failed` в журналах Dante → нет системного пользователя/неверный пароль.
* `no matching rule` → поправь `client pass`/`socks pass` (источники/направления/команды).
* Нет исхода в интернет у самого сервера → проверь `curl -I http[s]://example.com` без прокси, маршрут/файрвол.

## B.8) Ужесточение (по желанию)

* Ограничить источники:

  ```conf
  client pass { from: 10.0.0.0/8 to: 0.0.0.0/0 }
  ```
* Ограничить направления/порты:

  ```conf
  socks pass { from: 10.0.0.0/8 to: 0.0.0.0/0 port = 80-443 command: connect protocol: tcp }
  ```
* Systemd-перезапуск самого демона при падении:

  ```bash
  systemctl edit "${SVC}"
  ```

  Вставить:

  ```ini
  [Service]
  Restart=always
  RestartSec=5s
  StartLimitIntervalSec=0
  ```

  Применить:

  ```bash
  systemctl daemon-reload
  systemctl restart "${SVC}"
  ```

---

## 1) Быстрый фикс резолвинга: `socks5h`

В конфиге хелсчека переключи тип на `socks5h`, чтобы **DNS шёл через прокси**:

```bash
sed -i 's/^PROXY_TYPE=.*/PROXY_TYPE="socks5h"/' /etc/default/squid-healthcheck
VERBOSE=1 /usr/local/bin/squid-healthcheck.sh
```

Если после этого коды станут 200/30x — дело было в DNS, готово.

---

## 2) Проверка аутентификации к Dante

`danted` по-умолчанию проверяет **системных** пользователей (PAM). Если юзер `user` не существует в системе — логин не пройдёт. Создай учётку без шелла:

```bash
id user || useradd -M -s /usr/sbin/nologin user
echo 'user:passw0rd!' | chpasswd
```

Быстрый явный тест (видно причину, если auth/ACL не пускают):

```bash
curl -v --socks5-hostname 10.0.0.100:1080 \
     --proxy-user 'user:passw0rd!' \
     http://example.com -I
```

* Если увидишь в выводе `SOCKS5 authentication failed` → проблема с логином/паролем/методом.
* Если `Connection denied` / `general SOCKS server failure` → упёрся в ACL `danted`.

---

## 3) Минимальный рабочий `danted.conf` (с паролями)

Уточни внешний интерфейс (для исходящих от Dante):

```bash
IFACE=$(ip -o -4 route show to default | awk '{print $5}')
echo "$IFACE"
```

Пример конфига (Ubuntu/Jammy, пакет `dante-server`), подставь свой `IFACE`:

```conf
# /etc/danted.conf
logoutput: syslog
internal: 10.0.0.100 port = 1080
external: IFACE_NAME

user.privileged: root
user.notprivileged: nobody
user.libwrap: nobody

clientmethod: none
socksmethod: username   # требуем user/pass (PAM: системные пользователи)

# Разрешаем клиентам коннектиться к SOCKS
client pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
}

# Разрешаем все TCP CONNECT наружу (можно ужать под свои сети/порты)
socks pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  protocol: tcp
  command: connect
}

# (опционально) запрет всего остального явно
socks block { from: 0.0.0.0/0 to: 0.0.0.0/0 }
```

Применить:

```bash
sed -i "s/IFACE_NAME/$IFACE/" /etc/danted.conf
systemctl restart danted || systemctl restart sockd
systemctl status danted --no-pager || systemctl status sockd --no-pager
ss -ltnp | grep 1080
```

Повтори тест:

```bash
curl -v --socks5-hostname 10.0.0.100:1080 \
     --proxy-user 'user:passw0rd!' \
     http://example.com -I
```

Ожидаем `HTTP/1.1 301/200`. Если ок — хелсчек тоже начнёт давать 2xx/3xx.

---

## 4) Исключаем проблемы выхода в интернет у самого хоста

С самой машины с Dante без прокси:

```bash
curl -4 -I http://example.com
curl -4 -I https://example.com
```

Если здесь не отвечает — чиним маршрут/файрвол (nftables/iptables), а не прокси.

---

## 5) Доведём хелсчек до зелёного

* В `/etc/default/squid-healthcheck` оставь:

```bash
PROXY_TYPE="socks5h"
PROXY_IP="10.0.0.100"
PROXY_PORT=1080
PROXY_USER="user"
PROXY_PASSWORD="passw0rd!"
SVC_NAME="danted"   # или "sockd" — как называется unit у тебя: проверь `systemctl list-units | grep -i dante`
```

* Ручной прогон (наглядный):

```bash
VERBOSE=1 /usr/local/bin/squid-healthcheck.sh
```

Ожидаем `STATUS: HEALTHY` и коды `HTTP=30x/200`, `HTTPS=200`.

---

## 6) Если всё ещё 000 — быстрое чтение логов Dante

Включи подробный лог и смотри причину отказа:

```bash
# временно в /etc/danted.conf можно на время диагностики:
logoutput: stderr

systemctl restart danted
journalctl -u danted -n 100 --no-pager
```

Чаще всего там прямо видно: «no matching rule», «method not supported», «authentication failed».

---

### Короткий TL;DR

1. Поставь `PROXY_TYPE="socks5h"` → DNS через прокси.
2. Убедись, что в системе есть пользователь `user` с нужным паролем (PAM у Dante).
3. Проверь ACL в `danted.conf` (примеры выше).
4. `curl -v --socks5-hostname ...` должен дать 200/301.
5. После этого хелсчек будет **HEALTHY** и перезапускать `danted` при падениях.


