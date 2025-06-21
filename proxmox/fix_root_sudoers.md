Вот **итоговая инструкция** для полного восстановления работоспособности `sudo` внутри LXC/Incus-контейнера, где `root` на самом деле имеет `uid 100000` на хосте.

---

## 🧩 **Проблема**

Права и владельцы важных системных файлов `sudo` были повреждены (в основном — владельцы `100000`, что типично для контейнеров с user namespaces).

---

## ✅ **Цель**

Полностью восстановить `sudo` в работающем состоянии.

---

## 🛠️ **Решение (все команды)**

```bash
# 1. Исправляем владельца и права на основной бинарник sudo
chown root:root /usr/bin/sudo
chmod 4755 /usr/bin/sudo

# 2. Исправляем конфигурационный файл sudo.conf
chown root:root /etc/sudo.conf
chmod 644 /etc/sudo.conf

# 3. Исправляем плагин sudoers.so
chown root:root /usr/libexec/sudo/sudoers.so
chmod 644 /usr/libexec/sudo/sudoers.so

# 4. Исправляем основной файл sudoers
chown root:root /etc/sudoers
chmod 440 /etc/sudoers

# 5. Исправляем каталог с дополнительными конфигурациями
chown root:root /etc/sudoers.d
chmod 755 /etc/sudoers.d

# 6. Исправляем права на включаемые файлы (если они есть)
chown root:root /etc/sudoers.d/90-incus
chmod 440 /etc/sudoers.d/90-incus

chown root:root /etc/sudoers.d/README
chmod 644 /etc/sudoers.d/README
```

---

## 🔍 **Проверка**

После выполнения всех команд:

```bash
# Должно вывести "root"
sudo whoami

# Должно без ошибок обновить пакеты
sudo apt update
```

---

## 📌 **Дополнительно (по желанию)**

Создай простой скрипт для автоматической проверки и фикса в будущем:

```bash
nano /usr/local/bin/fix-sudo.sh
```

```bash
#!/bin/bash
chown root:root /usr/bin/sudo && chmod 4755 /usr/bin/sudo
chown root:root /etc/sudo.conf && chmod 644 /etc/sudo.conf
chown root:root /usr/libexec/sudo/sudoers.so && chmod 644 /usr/libexec/sudo/sudoers.so
chown root:root /etc/sudoers && chmod 440 /etc/sudoers
chown root:root /etc/sudoers.d && chmod 755 /etc/sudoers.d
chown root:root /etc/sudoers.d/90-incus && chmod 440 /etc/sudoers.d/90-incus
chown root:root /etc/sudoers.d/README && chmod 644 /etc/sudoers.d/README
```

```bash
chmod +x /usr/local/bin/fix-sudo.sh
```

И потом использовать:

```bash
bash /usr/local/bin/fix-sudo.sh
```

---

Если контейнер будет клонироваться, снапшотиться или мигрироваться — **этот скрипт гарантирует**, что `sudo` снова заработает.

Готов подсказать, как автоматизировать это через `incus` или `lxc` hooks.
