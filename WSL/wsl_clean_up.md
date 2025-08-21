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

### Чтобы довести до «идеальной чистоты» можешь сделать ещё:

#### 1. Почистить apt-кэш до нуля

```bash
sudo rm -rf /var/cache/apt/archives/*
sudo rm -rf /var/cache/apt/*.bin
```

#### 2. Проверить «мусорные» ядра и заголовки

Ты уже видел, что `autoremove` снёс лишние `linux-headers`. Если хочешь дожать:

```bash
dpkg -l | grep linux-headers
dpkg -l | grep linux-image
```

и руками удалить всё, что не нужно. В WSL ядра из дистрибутива вообще не используются (ядро у WSL своё). Так что **все пакеты `linux-image-*` и `linux-headers-*` можно безопасно снести** — они только место едят.

```bash
sudo apt purge "linux-image-*" "linux-headers-*" -y
```

#### 3. Очистить кеши systemd-resolved (если надо)

```bash
sudo resolvectl flush-caches
```

---

### 🚀 Итог

После этого у тебя внутри Ubuntu останется только реально нужное.
А чтобы уменьшить размер VHDX на диске Windows — после всех чисток сделай:

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

---

*(нужен модуль Hyper-V, работает в Windows 11 Pro/Enterprise)*

---

команда `Optimize-VHD` доступна только если включён **Hyper-V** (Windows 11 Pro / Enterprise).
На **Windows 11 Home** и без Hyper-V VMM она даёт именно такую ошибку: *"Virtual Machine Management service… not found"*.

---

### Варианты решения:

#### 🔹 1. Включить Hyper-V (если у тебя Pro/Enterprise)

```powershell
dism.exe /Online /Enable-Feature:Microsoft-Hyper-V /All
```

после перезагрузки будет работать `Optimize-VHD`.

---

#### 🔹 2. Если Windows Home — использовать встроенную оптимизацию WSL

С недавних версий у `wsl.exe` появился свой механизм очистки VHDX:

```powershell
wsl --shutdown
wsl --manage Ubuntu --compact
```

или для всех дистрибутивов:

```powershell
wsl --shutdown
wsl --system --compact
```

Это работает и на Home, и на Pro.

---

#### 🔹 3. Альтернативно — вручную через DiskPart

Если Hyper-V нет и `--compact` не помогает, можно подключить VHDX руками:

```powershell
diskpart
select vdisk file="C:\Users\chelaxian\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu24.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
exit
```

