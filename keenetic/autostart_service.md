### 📌 Сервис автозапуска для **Keenetic Giga**: запуск `ping_vpn_fgt.py` после ребута

Этот сервис автоматически запускает `ping_vpn_fgt.py` после перезагрузки **Keenetic Giga**. Скрипт будет работать в фоне, мониторить соединение и управлять туннелями **FortiGate**.

---

## 🔹 **1. Размещение Python-скрипта**
Убедитесь, что `ping_vpn_fgt.py` находится в `/tmp/mnt/EXT/home/`:

```sh
mkdir -p /tmp/mnt/EXT/home
nano /tmp/mnt/EXT/home/ping_vpn_fgt.py
```

Вставьте код скрипта и сохраните (`Ctrl + X`, затем `Y`, `Enter`).

Дайте файлу право на выполнение:

```sh
chmod +x /tmp/mnt/EXT/home/ping_vpn_fgt.py
```

---

## 🔹 **2. Создание стартового скрипта `/opt/etc/init.d/S99vpn_monitor`**
Создадим сервис для автоматического запуска:

```sh
nano /opt/etc/init.d/S99vpn_monitor
```

Вставьте следующий код:

```sh
#!/bin/sh

### Настройки
SCRIPT_PATH="/tmp/mnt/EXT/home/ping_vpn_fgt.py"
LOG_FILE="/tmp/mnt/EXT/home/ping_vpn_fgt.log"

start() {
    echo "Запуск VPN мониторинга..." | tee -a $LOG_FILE
    nohup python3 $SCRIPT_PATH >> $LOG_FILE 2>&1 &
    echo $! > /var/run/vpn_monitor.pid
}

stop() {
    echo "Остановка VPN мониторинга..." | tee -a $LOG_FILE
    if [ -f /var/run/vpn_monitor.pid ]; then
        kill $(cat /var/run/vpn_monitor.pid)
        rm -f /var/run/vpn_monitor.pid
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    *)
        echo "Использование: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
```

Сохраните (`Ctrl + X`, `Y`, `Enter`).

Дайте файлу права на выполнение:

```sh
chmod +x /opt/etc/init.d/S99vpn_monitor
```

---

## 🔹 **3. Запуск сервиса вручную**
Для проверки можно запустить сервис сразу:

```sh
/opt/etc/init.d/S99vpn_monitor start
```

Проверяем работу:

```sh
ps | grep ping_vpn_fgt.py
```

---

## 🔹 **4. Добавление сервиса в автозапуск**
Чтобы сервис стартовал после перезагрузки, создайте ссылку:

```sh
ln -sf /opt/etc/init.d/S99vpn_monitor /opt/etc/rc.d/S99vpn_monitor
```

Теперь сервис будет запускаться автоматически после перезагрузки роутера.

---

## 🔹 **5. Проверка после ребута**
Перезагрузите роутер:

```sh
reboot
```

После загрузки проверьте логи:

```sh
cat /tmp/mnt/EXT/home/ping_vpn_fgt.log
```

Если процесс работает, значит настройка успешна!

🚀 **Теперь `ping_vpn_fgt.py` автоматически стартует после перезагрузки!**
