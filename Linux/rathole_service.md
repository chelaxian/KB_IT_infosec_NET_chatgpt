# Мониторинг и автоматический рестарт сервисов Rathole (сервер и клиент)

## Общее описание

В этой инструкции рассмотрено, как построить надёжную схему мониторинга сервисов Rathole (клиентов и серверов), выполняющих функции реверс-прокси для соединения приложений через NAT.

## Цели

* Обнаружение ошибок (ERROR) в журналах systemd
* Автоматический рестарт сервисов
* Проверка наличия необходимых сетевых портов

---

## 0. Установка (пропустить, если уже установлено)

```
https://github.com/Musixal/Rathole-Tunnel
создание сервисов тоже опускаем, сами разберетесь
```
---

## 1. Содержимое скрипта на сервере rat-hole `/usr/local/bin/rathole-monitor.sh`

```bash
#!/bin/bash

# Карта портов к сервисам
PORT_SERVICE_MAP=(
    [7000]=rathole-SE.service
    [7010]=rathole-DE.service
    [7020]=rathole-IT.service
    [7030]=rathole-FR.service
    [7040]=rathole-UAE.service
    [7050]=rathole-UK.service
)

SERVICES=(
    "rathole-DE.service"
    "rathole-IT.service"
    "rathole-FR.service"
    "rathole-UAE.service"
    "rathole-UK.service"
    "rathole-SE.service"
)

for SERVICE in "${SERVICES[@]}"; do
    echo "$(date): Checking $SERVICE"

    if ! systemctl is-active --quiet "$SERVICE"; then
        echo "$(date): $SERVICE is inactive — restarting..."
        systemctl restart "$SERVICE"
        sleep 5
        continue
    fi

    STARTED_AT=$(systemctl show "$SERVICE" -p ActiveEnterTimestamp | cut -d= -f2)
    if [[ -z "$STARTED_AT" ]]; then
        echo "$(date): $SERVICE — unable to get ActiveEnterTimestamp, skipping check"
        continue
    fi

    UPTIME_SEC=$(( $(date -u +%s) - $(date -d "$STARTED_AT" +%s) ))
    if (( UPTIME_SEC < 300 )); then
        echo "$(date): $SERVICE — uptime < 5 min, skipping check"
        continue
    fi

    ERRORS=$(journalctl -u "$SERVICE" --since "5 minutes ago" --no-pager | grep -c 'ERROR')
    if (( ERRORS > 0 )); then
        echo "$(date): $SERVICE — $ERRORS ERROR(s) in logs — restarting..."
        systemctl restart "$SERVICE"
        sleep 5
        continue
    else
        echo "$(date): $SERVICE — healthy (no ERRORs)"
    fi

done

# Дополнительная проверка: открыты ли нужные порты
OPEN_PORTS=$(ss -ltn | awk 'NR>1 {print $4}' | sed 's/.*://')
for PORT in "${!PORT_SERVICE_MAP[@]}"; do
    SERVICE_NAME=${PORT_SERVICE_MAP[$PORT]}
    if ! echo "$OPEN_PORTS" | grep -q "^$PORT$"; then
        echo "$(date): $SERVICE_NAME — port $PORT not open — restarting..."
        systemctl restart "$SERVICE_NAME"
        sleep 5
    fi

done
```
## 1. Содержимое скрипта на клиенте rat-hole `/usr/local/bin/rathole-monitor.sh`

```bash
#!/bin/bash

SERVICES=(
    "rathole-DE.service"
    #"rathole-IT.service"
    #"rathole-FR.service"
    #"rathole-UAE.service"
    #"rathole-UK.service"
    #"rathole-SE.service"
)

for SERVICE in "${SERVICES[@]}"; do
    echo "$(date): Checking $SERVICE"

    # Проверка: активен ли сервис
    if ! systemctl is-active --quiet "$SERVICE"; then
        echo "$(date): $SERVICE is inactive — restarting..."
        systemctl restart "$SERVICE"
        sleep 5
        continue
    fi

    # Получаем человекочитаемую метку времени запуска сервиса
    SERVICE_STARTED_AT=$(systemctl show "$SERVICE" -p ActiveEnterTimestamp | cut -d= -f2)

    # Валидация
    if [[ -z "$SERVICE_STARTED_AT" ]]; then
        echo "$(date): $SERVICE — unable to get ActiveEnterTimestamp, skipping check"
        continue
    fi

    # Вычисляем аптайм сервиса в секундах
    SERVICE_UPTIME_S=$(( $(date -u +%s) - $(date -d "$SERVICE_STARTED_AT" +%s) ))

    # Если аптайм меньше 5 минут — пропустить
    if (( SERVICE_UPTIME_S < 300 )); then
        echo "$(date): $SERVICE — uptime < 5 min, skipping check"
        continue
    fi

    # Считаем количество ERROR за последние 5 минут
    ERR_COUNT=$(journalctl -u "$SERVICE" --since "5 minutes ago" --no-pager | grep -c 'ERROR')

    if (( ERR_COUNT >= 1 )); then
        echo "$(date): $SERVICE — $ERR_COUNT ERROR(s) in logs — restarting..."
        systemctl restart "$SERVICE"
        sleep 5
    else
        echo "$(date): $SERVICE — healthy (no ERRORs)"
    fi
done
```
---

## 2. systemd unit: `rathole-monitor.service`

```ini
[Unit]
Description=Monitor and restart rathole services if ERRORs found
Wants=rathole-monitor.timer

[Service]
Type=oneshot
ExecStart=/usr/local/bin/rathole-monitor.sh
```

## 3. systemd timer: `rathole-monitor.timer`

```ini
[Unit]
Description=Run rathole-monitor every 5 minutes

[Timer]
OnBootSec=1min
#OnUnitActiveSec=5min
OnCalendar=*:0/5
Unit=rathole-monitor.service

[Install]
WantedBy=timers.target

```

---

## 4. Активация

```bash
chmod +x /usr/local/bin/rathole-monitor.sh

# Создаем и активируем сервис и таймер:
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable --now rathole-monitor.timer
```

---

## 5. Результат

* Автопроверка каждые 5 минут
* Учёт минимального аптайма (5 мин)
* Проверка портов
* Авторестарт в случае сбоев

---

## 6. Проверка корректной работы, отладка и логирование

### Проверка ручного запуска

Чтобы убедиться, что скрипт работает как ожидается, его можно запустить вручную с подробным выводом:

```bash
bash -x /usr/local/bin/rathole-monitor.sh
```

### Проверка состояния таймера и сервиса

```bash
# Проверить таймер
systemctl status rathole-monitor.timer

# Проверить последний запуск
journalctl -u rathole-monitor.service --since "15 minutes ago" --no-pager
```

### Проверка срабатывания рестарта при неоткрытом порте

Ты можешь остановить один из сервисов и убедиться, что скрипт его перезапустит:

```bash
systemctl stop rathole-FR.service
sleep 10
bash /usr/local/bin/rathole-monitor.sh
```

Убедись, что в выводе будет строчка вроде:

```
rathole-FR.service is inactive — restarting...
```

Или:

```
rathole-FR.service — port 7030 not open — restarting...
```

---

## 7. Установка необходимых пакетов

Для корректной работы скриптов необходимо наличие следующих утилит:

* `systemd`
* `ss` (входит в пакет `iproute2`)
* `netstat` (входит в пакет `net-tools`)
* `grep`, `awk`, `cut`, `bc`, `sed`, `date` — базовые GNU-утилиты

Установить всё необходимое можно одной командой:

```bash
apt update && apt install -y net-tools iproute2 bc coreutils systemd
```

На минимальных контейнерах (например, LXC/Proxmox или хостинги без systemd) убедись, что `systemctl` работает и имеет доступ к логам.

