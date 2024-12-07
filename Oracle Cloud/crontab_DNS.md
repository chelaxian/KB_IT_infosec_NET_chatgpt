### 1. Команда для замены содержимого файла `/etc/resolv.conf`:

```bash
echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" > /etc/resolv.conf
```

---

### 2. Команда для добавления задания в `crontab`:

Для выполнения команды каждые 5 минут добавьте строку в `crontab`. Например, для замены содержимого `/etc/resolv.conf`:

```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * echo -e 'nameserver 8.8.8.8\nnameserver 8.8.4.4' > /etc/resolv.conf") | crontab -
```

---

### Объяснение:
- **`echo -e`**: Позволяет вставить строки с помощью символа `\n`.
- **`>`**: Перезаписывает файл `/etc/resolv.conf`.
- **`crontab -l 2>/dev/null`**: Выводит текущие задачи в `crontab` (если они есть).
- **`echo ... | crontab -`**: Добавляет новое задание в `crontab`.

Теперь файл `/etc/resolv.conf` будет обновляться каждые 5 минут.
