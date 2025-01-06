

Для выполнения этой задачи можно использовать следующую строку в crontab:

```bash
* * * * * printf "nameserver 8.8.8.8\nnameserver 8.8.4.4\n" | sudo tee /etc/resolv.conf /run/systemd/resolve/stub-resolv.conf > /dev/null
```

### Объяснение:
1. `* * * * *`: Выполняется каждую минуту.
2. `eprintf "nameserver 8.8.8.8\nnameserver 8.8.4.4\n"`: Генерирует содержимое для файла.
3. `sudo tee /etc/resolv.conf /run/systemd/resolve/stub-resolv.conf`: Перезаписывает оба файла указанным содержимым.
4. `> /dev/null`: Отключает вывод `tee` в консоль (чтобы не захламлять лог crontab).

### Важно:
1. Убедитесь, что пользователь, выполняющий cron-задачу, имеет право на запись в эти файлы (например, добавьте задачу в crontab для root с помощью `sudo crontab -e`).
2. Возможно, стоит отключить службу `systemd-resolved`, чтобы изменения в файле `/run/systemd/resolve/stub-resolv.conf` не перезаписывались.

---

Чтобы отключить `systemd-resolved`, выполните следующие шаги:

### 1. Отключение службы `systemd-resolved`
```bash
sudo systemctl disable systemd-resolved --now
```
- `--now`: Останавливает службу немедленно.
- `disable`: Предотвращает автоматический запуск службы при загрузке.

### 2. Удаление или обновление символьной ссылки `/etc/resolv.conf`
После отключения `systemd-resolved` файл `/etc/resolv.conf` часто является символической ссылкой на файл `/run/systemd/resolve/stub-resolv.conf`. Чтобы использовать собственный `resolv.conf`, выполните следующие команды:

```bash
sudo rm /etc/resolv.conf
printf "nameserver 8.8.8.8\nnameserver 8.8.4.4\n" | sudo tee /etc/resolv.conf
```

### 3. Убедитесь, что DNS работает корректно
После отключения службы проверьте, что настройки DNS применяются правильно. Например:

```bash
nslookup google.com
```

Если команда возвращает IP-адрес, значит DNS работает корректно.

### 4. (Опционально) Проверка статуса службы
Чтобы убедиться, что `systemd-resolved` полностью отключена, выполните:

```bash
sudo systemctl status systemd-resolved
```

Статус должен быть `inactive (dead)`.

Если потребуется дополнительная помощь, дайте знать!
