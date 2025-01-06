

Для выполнения этой задачи можно использовать следующую строку в crontab:

```bash
* * * * * echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" | sudo tee /etc/resolv.conf /run/systemd/resolve/stub-resolv.conf > /dev/null
```

### Объяснение:
1. `* * * * *`: Выполняется каждую минуту.
2. `echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4"`: Генерирует содержимое для файла.
3. `sudo tee /etc/resolv.conf /run/systemd/resolve/stub-resolv.conf`: Перезаписывает оба файла указанным содержимым.
4. `> /dev/null`: Отключает вывод `tee` в консоль (чтобы не захламлять лог crontab).

### Важно:
1. Убедитесь, что пользователь, выполняющий cron-задачу, имеет право на запись в эти файлы (например, добавьте задачу в crontab для root с помощью `sudo crontab -e`).
2. Возможно, стоит отключить службу `systemd-resolved`, чтобы изменения в файле `/run/systemd/resolve/stub-resolv.conf` не перезаписывались. 
