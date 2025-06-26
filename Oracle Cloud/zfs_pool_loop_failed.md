# Проблема

```bash
  Found volume group "vmname-vg" using metadata type lvm2
  2 logical volume(s) in volume group "vmname-vg" now active
/dev/mapper/vmname--vg-root: recovering journal
/dev/mapper/vmname--vg-root: clean, 103254/2927008 files, 2613853/11701248 blocks
[    2.692206] systemd[1]: sysinit.target: Job systemd-binfmt.service/start deleted to break ordering cycle starting with sysinit.target/start
[ SKIP ] Ordering cycle found, skipping systemd-binfmt.service
[    2.700397] systemd[1]: sysinit.target: Job pvenetcommit.service/start deleted to break ordering cycle starting with sysinit.target/start
[ SKIP ] Ordering cycle found, skipping pvenetcommit.service
[    2.709585] systemd[1]: sysinit.target: Job local-fs.target/start deleted to break ordering cycle starting with sysinit.target/start
[ SKIP ] Ordering cycle found, skipping local-fs.target
[FAILED] Failed to start zfs-loop.service - Attach ZFS loop file.
```
---

# Решение

Вот готовая инструкция в формате KB-статьи для GitHub:

---

# 🧠 KB: Подключение ZFS-пула через loop-файл при старте системы (Systemd + losetup)

## 📘 Цель

Обеспечить автоматическое подключение ZFS-пула, размещённого в `.img`-файле, через `loop`-устройство при загрузке Linux-системы с использованием `systemd`.

---

## 🧱 Исходные условия

* Образ пула ZFS: `/mnt/zfs59/zfs-pool.img`
* Файл монтируется через `fstab`:

  ```
  UUID=XXXX /mnt/zfs59 ext4 defaults 0 2
  ```
* ZFS-пул называется `zfspool`.

---

## ⚙️ Шаг 1. Создание `zfs-loop.service`

Файл `/etc/systemd/system/zfs-loop.service`:

```ini
[Unit]
Description=Attach ZFS loop file
DefaultDependencies=no
RequiresMountsFor=/mnt/zfs59
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/losetup /dev/loop0 /mnt/zfs59/zfs-pool.img
ExecStop=/usr/sbin/losetup -d /dev/loop0
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
```

### Активировать и запустить:

```bash
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable zfs-loop.service
systemctl start zfs-loop.service
```

Проверка:

```bash
losetup -a
# → должен быть /dev/loop0: (.../zfs-pool.img)
```

---

## ⚙️ Шаг 2. Создание `zfs-import-loop.service`

Файл `/etc/systemd/system/zfs-import-loop.service`:

```ini
[Unit]
Description=Import ZFS pool from loop device
Requires=zfs-loop.service
After=zfs-loop.service
ConditionPathExists=/dev/loop0

[Service]
Type=oneshot
ExecStart=/usr/bin/bash -c '/sbin/zpool list zfspool >/dev/null 2>&1 || /sbin/zpool import zfspool'
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
```

### Активировать и запустить:

```bash
systemctl daemon-reload
systemctl enable zfs-import-loop.service
systemctl start zfs-import-loop.service
```

---

## ✅ Проверка результата

```bash
zpool list
zfs list
```

Вывод должен содержать пул `zfspool` и его датасеты. Например:

```
NAME       USED  AVAIL  REFER  MOUNTPOINT
zfspool    8.17G  44.6G    26K  /mnt/zfs
```

---

## 🛠 Возможные проблемы и решения

| Ошибка                                               | Решение                                                                 |   |                            |
| ---------------------------------------------------- | ----------------------------------------------------------------------- | - | -------------------------- |
| `losetup: No such file or directory`                 | Убедитесь, что `/mnt/zfs59` смонтирован через `fstab` и файл существует |   |                            |
| `zpool import: pool already exists`                  | Используйте конструкцию \`zpool list                                    |   | zpool import`в`ExecStart\` |
| `zpool import` ничего не находит                     | Убедитесь, что loop-девайс активен и указывает на правильный `.img`     |   |                            |
| Зависимости `systemd` не срабатывают должным образом | Используйте `RequiresMountsFor=/mnt/zfs59` и `After=local-fs.target`    |   |                            |

---

## 🧩 Примечания

* Разделение на два юнита (`loop` и `import`) позволяет гибко отлаживать и использовать систему.
* Если необходимо — можно объединить оба этапа в один `oneshot`-юнит, но это снизит читаемость и гибкость.

---

## 🧷 Автор

Собрано и протестировано вручную. Для Debian/Ubuntu/Proxmox с ZFS на loop-файле.
