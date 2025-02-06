Вот итоговая инструкция в формате **Markdown** для публикации на GitHub:


# Настройка автоматической замены `/etc/resolv.conf` через `cron` на Keenetic (Entware)

Эта инструкция позволяет автоматически обновлять файл `/etc/resolv.conf` каждую минуту с заданным содержимым.

## 1. Установка необходимых пакетов (если не установлены)

Подключитесь к роутеру по SSH и выполните:

```sh
opkg update
opkg install nano cron
```

## 2. Создание и редактирование `crontab`

Откройте файл `crontab` для редактирования:

```sh
nano /opt/etc/crontab
```

Добавьте в конец файла следующую строку:

```sh
* * * * * echo -e "nameserver 192.168.1.99\nnameserver 127.0.0.1\noptions timeout:1 attempts:1 rotate" > /etc/resolv.conf
```

Сохраните изменения (`Ctrl + X`, затем `Y` и `Enter`).

## 3. Применение `crontab`

Загрузите новый `crontab`:

```sh
crontab /opt/etc/crontab
```

## 4. Перезапуск `cron`

Чтобы `cron` применил новое расписание, выполните:

```sh
/opt/etc/init.d/S10cron restart
```

## 5. Проверка работы

Через несколько минут проверьте содержимое `/etc/resolv.conf`:

```sh
cat /etc/resolv.conf
```

Вы должны увидеть следующий вывод:

```plaintext
nameserver 192.168.1.99
nameserver 127.0.0.1
options timeout:1 attempts:1 rotate
```

Теперь `cron` будет автоматически обновлять файл `/etc/resolv.conf` каждую минуту.
