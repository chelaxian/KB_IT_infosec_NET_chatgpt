Ты столкнулся с типичной ситуацией: у тебя ZFS-пул на loop-файле, и система не может его импортировать после ребута. Сейчас ZFS "не видит" пул, потому что не определено устройство `loop0` как полноценный vdev.

---

### Давай разберёмся пошагово:

---

## 🧠 Что происходит?

- `zpool` говорит: **`no such pool available`**
- Это значит, что он не видит активный ZFS-пул, даже если он существует.
- У тебя используется **loop-файл** (`/mnt/zfs59/zfs-pool.img`) как устройство vdev.
- Но: `zfs` не может его импортировать, пока **loop-устройство (`/dev/loop0`) не создано вручную или через systemd unit**.

---

## 🔍 Проверка

### 1. Проверь, действительно ли loop0 активен:

```bash
losetup -a
```

Ожидаем увидеть:
```
/dev/loop0: [XYZ]: (/mnt/zfs59/zfs-pool.img)
```

Если **не видишь этого** – значит `losetup` не сработал как надо.

---

## ✅ Решение

---

### Шаг 1. Убедись, что loop0 создан:

```bash
losetup /dev/loop0 /mnt/zfs59/zfs-pool.img
```

Проверь:

```bash
losetup -a
```

---

### Шаг 2. Попробуй импортировать вручную:

```bash
zpool import
```

Если там виден твой пул (`zfspool`), то:

```bash
zpool import zfspool
```

Если ругается на активный пул – принудительно:

```bash
zpool import -f zfspool
```

---

### Шаг 3. Проверь:

```bash
zpool status
zfs list
```

---

## 🔁 Если не помогает — попытайся сбросить метаданные пула

(Только если уверен, что пул "завис" и его не монтирует из-за «грязного» состояния после внезапного ребута):

```bash
zpool import -f -F zfspool
```

---

## 🛠 Рекомендации

Чтобы всё автоматом поднималось после перезагрузки:

1. Убедись, что `zfs-loop.service` **выполняется ДО** монтирования пула.
2. Создай свой `systemd` юнит `zfs-import-loop.service`:

```ini
[Unit]
Description=Import ZFS loopback pool
Requires=zfs-loop.service
After=zfs-loop.service

[Service]
Type=oneshot
ExecStart=/sbin/zpool import -f zfspool
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
systemctl daemon-reexec
systemctl enable zfs-import-loop.service
```

---

## ⚠️ Важный момент

Если `zfs-pool.img` лежит на файловой системе, смонтированной вручную (в твоем случае `/mnt/zfs59`), то `zfs-loop.service` и `zfs-import-loop.service` **должны стартовать ПОСЛЕ** монтирования `/mnt/zfs59`.

Тогда добавь в `Unit`:

```ini
After=local-fs.target
```

или даже:

```ini
After=mnt-zfs59.mount
Requires=mnt-zfs59.mount
```

---

## 📌 Почему это не делается автоматически?

### Причины:
1. **`zfs-pool.img` находится на файловой системе (`/mnt/zfs59`)**, которая сама монтируется после старта системы.
2. **`losetup` и `zpool import` должны запускаться *после* монтирования этой ФС**, иначе ZFS не увидит файл.
3. ZFS не "умеет" сам находить образы в файловых системах, ему нужно "натянуть" loop вручную.

---

## ✅ Автоматизация через systemd

Мы создадим **2 systemd юнита**, которые:
- монтируют loop-файл,
- импортируют ZFS-пул,
- и делают это в нужной последовательности после монтирования `/mnt/zfs59`.

---

### 🔧 1. Unit: `zfs-loop.service`

Файл: `/etc/systemd/system/zfs-loop.service`

```ini
[Unit]
Description=Attach ZFS loop file
Requires=mnt-zfs59.mount
After=mnt-zfs59.mount

[Service]
Type=oneshot
ExecStart=/usr/sbin/losetup /dev/loop0 /mnt/zfs59/zfs-pool.img
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

---

### 🔧 2. Unit: `zfs-import-loop.service`

Файл: `/etc/systemd/system/zfs-import-loop.service`

```ini
[Unit]
Description=Import ZFS loopback pool
Requires=zfs-loop.service
After=zfs-loop.service

[Service]
Type=oneshot
ExecStart=/sbin/zpool import -f zfspool
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

---

### 🔧 (опционально) 3. Unit-файл для `/mnt/zfs59`, если он не прописан в `fstab`:

Если ты **не монтируешь /mnt/zfs59 через fstab**, нужно описать его вручную:

```bash
systemctl edit --full mnt-zfs59.mount
```

```ini
[Unit]
Description=Mount ZFS host FS
Before=zfs-loop.service

[Mount]
What=/dev/sda1
Where=/mnt/zfs59
Type=ext4

[Install]
WantedBy=multi-user.target
```

---

### 🚀 Активируем:

```bash
systemctl daemon-reexec
systemctl enable zfs-loop.service
systemctl enable zfs-import-loop.service
```

---

### 🔄 Проверка после ребута

```bash
reboot
```

И затем:

```bash
zpool status
zfs list
```

---

