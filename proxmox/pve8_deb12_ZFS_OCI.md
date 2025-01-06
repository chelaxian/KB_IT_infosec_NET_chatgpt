### Краткая инструкция по настройке Proxmox и ZFS в виде файла

#### 0. **Установка ZFS**

1. обновите репо, добавив туда `contrib`, `non-free` и `non-free-firmware`:
   ```bash
   nano /etc/apt/sources.list
   ```

   ```bash
   deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
   deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
   deb http://deb.debian.org/debian-security bookworm-security main contrib non-free non-free-firmware
   ```
2. установите пакеты ZFS:
   ```bash
   apt update
   apt install zfsutils-linux
   apt install zfs-initramfs
   apt install zfs-dkms
   modprobe zfs
   ```

#### 1. **Создание ZFS в виде файла**
1. Создайте файл для ZFS:
   ```bash
   df -h #оценить свободное место
   #fallocate -l 31G /zfs-pool.img
   #fallocate -l 47G /mnt/data/zfs-pool.img
   fallocate -l 55G /mnt/zfs59/zfs-pool.img
   ```

2. Создайте ZFS пул:
   ```bash
   zpool create zfspool /mnt/zfs59/zfs-pool.img
   ```

3. Убедитесь, что ZFS пул создан:
   ```bash
   zpool status
   ```

4. Установите точку монтирования:
   ```bash
   mkdir -p /mnt/zfs
   zfs set mountpoint=/mnt/zfs zfspool
   ```

---

#### 2. **Настройка автоматического монтирования ZFS**
1. Создайте сервис для подключения файла ZFS:
   ```bash
   nano /etc/systemd/system/zfs-loop.service
   ```

2. Добавьте содержимое:
   ```plaintext
   [Unit]
   Description=Attach ZFS loop file
   Before=zfs-import.target
   Requires=zfs-import.target

   [Service]
   Type=oneshot
   ExecStart=/usr/sbin/losetup /dev/loop0 /mnt/zfs59/zfs-pool.img
   ExecStop=/usr/sbin/losetup -d /dev/loop0
   RemainAfterExit=yes

   [Install]
   WantedBy=zfs-import.target
   ```
   вместо `/dev/loop0` может быть `/dev/loop1` или `/dev/loop2`

3. Активируйте и запустите сервис:
   ```bash
   systemctl daemon-reload
   systemctl enable zfs-loop.service
   systemctl start zfs-loop.service
   ```

---

#### 3. **Добавление ZFS в Proxmox**
1. Зарегистрируйте ZFS как хранилище:
   ```bash
   pvesm add zfspool zfspool-storage --pool zfspool --content images,rootdir
   ```

2. Убедитесь, что хранилище отображается:
   ```bash
   pvesm status
   ```

---

#### 4. **Использование ZFS для ВМ и контейнеров**
1. При создании новой ВМ или контейнера выберите хранилище `zfspool-storage` для дисков.
2. Для создания снапшотов используйте веб-интерфейс или команды:
   - **Для LXC контейнеров:**
     ```bash
     pct snapshot <VMID> <snapshot-name>
     ```
   - **Для виртуальных машин:**
     ```bash
     qm snapshot <VMID> <snapshot-name>
     ```

---

#### 5. **Полезные команды ZFS**
- Просмотр пула:
  ```bash
  zpool status
  zfs list
  ```
- Создание снапшота вручную:
  ```bash
  zfs snapshot zfspool@backup
  ```
- Удаление снапшота:
  ```bash
  zfs destroy zfspool@backup
  ```

---

Чтобы удалить пул `zpool1`, который больше не существует, но продолжает отображаться в веб-интерфейсе Proxmox, можно попробовать следующие шаги:

### 1. **Проверьте состояние пулов ZFS**
Первым шагом убедитесь, что пул действительно не существует на уровне ZFS. Выполните команду:

```bash
zpool status
```

Если пул `zpool1` больше не существует, то команда не должна выводить его в списке активных пулов.

### 2. **Проверьте конфигурацию Proxmox**
Proxmox может продолжать ссылаться на этот пул в конфигурационных файлах. Откройте конфигурационный файл для хранилищ:

```bash
nano /etc/pve/storage.cfg
```

В нем найдите запись, которая относится к пулу `zpool1` и удалите или закомментируйте её. Запись может выглядеть как-то так:

```
zfspool: zpool1
    pool zpool1
    content images,rootdir
    path /mnt/zfs
```

Удалите или закомментируйте эту запись.

### 3. **Обновите конфигурацию Proxmox**
После удаления записи из конфигурации перезагрузите службу Proxmox, чтобы изменения вступили в силу:

```bash
systemctl restart pvedaemon
```

### 4. **Проверьте веб-интерфейс**
После этого обновите веб-интерфейс Proxmox, и пул `zpool1` должен исчезнуть из списка хранилищ.

### 5. **Дополнительная проверка**
Если пул продолжает отображаться в интерфейсе, возможно, нужно перезапустить веб-интерфейс:

```bash
systemctl restart pveproxy
```

После этого снова проверьте веб-интерфейс.

---

Если пул отображается из-за другой причины или зависимости, возможно, потребуется дополнительная диагностика на уровне Proxmox, но в большинстве случаев это решается удалением записи из конфигурации и перезапуском служб.
