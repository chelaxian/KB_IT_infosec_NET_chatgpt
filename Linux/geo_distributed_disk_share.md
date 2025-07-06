# Объединение 5 VPS в единое распределённое хранилище 250 ГБ с помощью GlusterFS

## Цель

Объединить дисковое пространство 5 VPS-серверов (по 50 ГБ каждый) в единый том объёмом 250 ГБ, доступный по пути `/mnt/vps_shared` на каждом сервере. Используется только как файлохранилище, доступное для Python-скриптов внутри LXC-контейнеров на Proxmox VE 8.

## Предпосылки

- У всех VPS: Debian 11, Proxmox VE 8
- Внутри: LXC-контейнеры с Ubuntu 22.04
- У всех серверов: статический белый IP, root-доступ
- Задержка не критична
- Требуется общая папка /mnt/vps_shared с доступом к 250 ГБ

---

## Шаг 1: Установка GlusterFS

На всех 5 VPS:

```bash
sudo apt update && sudo apt install -y glusterfs-server
sudo systemctl enable --now glusterd
```

Убедитесь, что служба работает:

```bash
sudo systemctl status glusterd
```

---

## Шаг 2: Подготовка каталогов и сеть

Создайте каталог под brick на каждом сервере:

```bash
sudo mkdir -p /gluster-storage
```

Убедитесь, что все серверы доступны по IP или именам (впишите в /etc/hosts при необходимости).

---

## Шаг 3: Объединение серверов в кластер

На одном из серверов (например, server1):

```bash
gluster peer probe server2
gluster peer probe server3
gluster peer probe server4
gluster peer probe server5
gluster peer status
```

---

## Шаг 4: Создание распределённого тома (без репликации)

```bash
sudo gluster volume create vps_shared \
    server1:/gluster-storage \
    server2:/gluster-storage \
    server3:/gluster-storage \
    server4:/gluster-storage \
    server5:/gluster-storage \
    force
```

Запуск тома:

```bash
sudo gluster volume start vps_shared
gluster volume info vps_shared
```

---

## Шаг 5: Монтирование GlusterFS

На каждом сервере:

```bash
sudo mkdir -p /mnt/vps_shared
sudo mount -t glusterfs localhost:/vps_shared /mnt/vps_shared
```

Для автозагрузки добавьте в `/etc/fstab`:

```fstab
localhost:/vps_shared /mnt/vps_shared glusterfs defaults,_netdev 0 0
```

---

## Шаг 6: Проверка

```bash
echo "test" > /mnt/vps_shared/testfile.txt
```

На другом сервере:

```bash
ls /mnt/vps_shared
```

---

## Шаг 7: Проброс папки в LXC-контейнер

На каждом хосте Proxmox:

```bash
pct set <CTID> -mp0 /mnt/vps_shared,mp=/mnt/vps_shared
```

Или вручную в `/etc/pve/lxc/<CTID>.conf`:

```
mp0: /mnt/vps_shared,mp=/mnt/vps_shared
```

---

## Шаг 8: Проверка внутри контейнера

```bash
ls /mnt/vps_shared
df -h
```

---

## Примечания

- Один файл не может превышать 50 ГБ (ограничение одного brick).
- Общий размер: до 250 ГБ.
- Отказоустойчивость не реализована (используется только distribute).
- Для репликации/избыточности используйте другие режимы GlusterFS (replicated, dispersed).