`wget` не поддерживает HTTPS, используй `curl`:

### **Скачивание через `curl`**
```sh
curl -L -o /opt/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.mipsel
```
Флаг `-L` нужен, чтобы `curl` следовал редиректам.

### **Даем права на выполнение**
```sh
chmod +x /opt/bin/ttyd
```

### **Проверяем запуск**
```sh
/opt/bin/ttyd -p 81 sh
```

Если **не получается скачать напрямую**, скачай файл на ПК и передай на роутер через `scp`:
```sh
scp ttyd.mipsel root@<IP_РОУТЕРА>:/opt/bin/ttyd
```

### 🎉 **Анализ логов `ttyd`**
`ttyd` **успешно запустился** и **слушает порт 81**, но в логах есть **предупреждения (`W: _lws_smd_msg_send: rejecting message on queue depth 40`)**.

#### 📌 **Что означают предупреждения?**
Эти ошибки связаны с `libwebsockets` (LWS) и `lws_smd`, который управляет системными событиями. Они **не критичны**, но означают, что очередь сообщений достигла предела (40 сообщений).  

---

## ✅ **1. Проверяем доступность `ttyd` в браузере**
Попробуй **открыть в браузере** (из локальной сети):
```
http://<IP_РОУТЕРА>:81/
```
Если **работает** → можно игнорировать предупреждения.

Если **не открывается**, проверь через `netstat`:
```sh
netstat -tulnp | grep 81
```
Или через `ss` (если `netstat` не установлен):
```sh
ss -tulnp | grep 81
```
Если `ttyd` не слушает порт, попробуй другой:
```sh
ttyd -p 8080 sh
```
Потом снова зайди в браузер:  
```
http://<IP_РОУТЕРА>:8080/
```

---

## ✅ **2. Добавляем `--writable`, если терминал работает только для чтения**
В логах есть строка:
```
[2025/02/07 10:48:47:1233] N: The --writable option is not set, will start in readonly mode
```
Если терминал **не позволяет вводить команды**, попробуй запустить так:
```sh
ttyd --writable -p 81 sh
```

---

## ✅ **3. Добавляем `ttyd` в автозапуск**
Создай скрипт `/opt/etc/init.d/S99ttyd`:
```sh
nano /opt/etc/init.d/S99ttyd
```
Вставь:
```sh
#!/bin/sh

### Настройки
PORT=81
LOG_FILE="/opt/var/log/ttyd.log"
PID_FILE="/var/run/ttyd.pid"

start() {
    echo "Запуск ttyd..." | tee -a $LOG_FILE
    /opt/bin/ttyd --writable -p $PORT sh >> $LOG_FILE 2>&1 &  
    echo $! > $PID_FILE  
}

stop() {
    echo "Остановка ttyd..." | tee -a $LOG_FILE
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

Даем права на выполнение:
```sh
chmod +x /opt/etc/init.d/S99ttyd
```

Добавляем в автозапуск:
```sh
ln -s /opt/etc/init.d/S99ttyd /opt/etc/init.d/rc.local
```

Запускаем вручную:
```sh
/opt/etc/init.d/S99ttyd start
```

---

## ✅ **4. Очищаем логи от `lws_smd_msg_send`**
Если в логах **слишком много сообщений `rejecting message on queue depth 40`**, можно **отключить системные события LWS**:
```sh
ttyd --writable --skip-syslog -p 81 sh
```
Если работает, добавь этот флаг в **автозапуск**.

---

## **Вывод**
1. **Проверь доступность `ttyd` через браузер (`http://<IP_РОУТЕРА>:81/`)**.
2. **Если терминал только для чтения** → добавь `--writable`.
3. **Если логов слишком много** → добавь `--skip-syslog`.
4. **Добавь `ttyd` в автозапуск** для удобства.

🚀 **Твой `ttyd` уже работает!** Осталось только донастроить. Напиши, если что-то не так. 🔥
