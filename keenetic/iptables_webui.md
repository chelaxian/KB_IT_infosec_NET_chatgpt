Вот скрипт автозапуска для Entware (`/opt/etc/init.d/S99iptables_webui`), который будет запускать Node.js-приложение **iptables-webui** на Keenetic Giga:

### Скрипт `/opt/etc/init.d/S99iptables_webui`
```sh
#!/bin/sh

### Настройки
APP_DIR="/opt/etc/iptables/iptables"
NODE_BIN="/opt/bin/node"
LOG_FILE="/opt/var/log/iptables-webui.log"
PID_FILE="/var/run/iptables-webui.pid"

start() {
    echo "Запуск iptables-webui..." | tee -a $LOG_FILE
    cd $APP_DIR
    $NODE_BIN server.js >> $LOG_FILE 2>&1 &  # Запускаем сервер в фоне
    echo $! > $PID_FILE  # Сохраняем PID процесса
}

stop() {
    echo "Остановка iptables-webui..." | tee -a $LOG_FILE
    if [ -f "$PID_FILE" ]; then
        kill $(cat $PID_FILE) 2>/dev/null
        rm -f $PID_FILE
    fi
}

restart() {
    stop
    sleep 2
    start
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) restart ;;
    *) echo "Использование: $0 {start|stop|restart}"; exit 1 ;;
esac

exit 0
```

### Установка **iptables-webui** на Keenetic Entware:
```sh
# Устанавливаем Entware, если не установлено
opkg update
opkg install node git

# Клонируем репозиторий и устанавливаем зависимости
mkdir -p /opt/etc/iptables
cd /opt/etc/iptables
git clone https://github.com/puux/iptables
cd iptables
npm install

# Даем права на выполнение скрипта автозапуска
chmod +x /opt/etc/init.d/S99iptables_webui

# Запускаем и добавляем в автозагрузку
/opt/etc/init.d/S99iptables_webui start
ln -s /opt/etc/init.d/S99iptables_webui /opt/etc/init.d/rc.local
```

После этого **iptables-webui** будет автоматически запускаться при загрузке Keenetic Giga.

**Проверка логов работы:**
```sh
tail -f /opt/var/log/iptables-webui.log
```

Если что-то не работает — проверяй `node` и пути к файлам.
