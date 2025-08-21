сделаем «генеральную уборку» в WSL2 (Ubuntu).
Разобьём на шаги, чтобы ничего нужного случайно не снести.

---

## 🔹 1. Очистка кэша apt/dpkg

Удаляет кэш пакетов, временные deb-файлы, лишние зависимости:

```bash
sudo apt-get clean           # очистить кэш пакетов ( /var/cache/apt/archives )
sudo apt-get autoclean       # удалить устаревшие пакеты
sudo apt-get autoremove -y   # удалить неиспользуемые зависимости
```

---

## 🔹 2. Очистка системных логов

В WSL systemd-журналы обычно не критичны (и могут занимать гигабайты).

```bash
sudo journalctl --vacuum-time=1d
sudo journalctl --rotate
sudo journalctl --vacuum-size=100M
```

(оставим только последние сутки и ограничим размер до 100M).

Если systemd у тебя не нужен → можно вообще:

```bash
sudo rm -rf /var/log/*
```

(пересоздастся автоматически).

---

## 🔹 3. Очистка временных директорий

```bash
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
```

---

## 🔹 4. Очистка snap (если установлен)

```bash
sudo du -sh /var/lib/snapd/snaps   # посмотреть размер
sudo snap set system refresh.retain=2
sudo snap remove $(snap list --all | awk '/disabled/{print $1, $2}' | xargs -n2 echo)
```

---

## 🔹 5. Очистка кэшей пользователей

```bash
rm -rf ~/.cache/*
```

---

## 🔹 6. Проверка размера мусора (опционально)

```bash
sudo du -sh /var/cache/*
sudo du -sh /var/log/*
du -sh ~/.cache/*
```

---

## 🔹 7. Сжатие виртуального диска (если надо уменьшить VHDX)

После очистки можно сжать сам файл диска WSL:

1. Завершаем WSL:

   ```powershell
   wsl --shutdown
   ```
2. В PowerShell:

   ```powershell
   Optimize-VHD -Path "C:\Users\chelaxian\AppData\Local\Packages\<Canonical...>\LocalState\ext4.vhdx" -Mode Full
   ```

   (нужен модуль Hyper-V, работает только на Windows Pro/Enterprise).

---

⚠️ Все команды выше **безопасны** для системы, они чистят только кэши/логи/временные файлы, которые пересоздаются автоматически.

