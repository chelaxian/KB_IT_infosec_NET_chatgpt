### Краткая инструкция по настройке Proxmox и ZFS в виде файла


#### 1. **Создание ZFS в виде файла**
1. Создайте файл для ZFS:
   ```bash
   df -h #оценить свободное место
   #fallocate -l 31G /zfs-pool.img
   fallocate -l 73G /zfs-pool.img
   ```

2. Создайте ZFS пул:
   ```bash
   zpool create zfspool /zfs-pool.img
   ```

3. Убедитесь, что ZFS пул создан:
   ```bash
   zpool status
   ```

4. Установите точку монтирования:
   ```bash
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
   ExecStart=/usr/sbin/losetup /dev/loop0 /zfs-pool.img
   ExecStop=/usr/sbin/losetup -d /dev/loop0
   RemainAfterExit=yes

   [Install]
   WantedBy=zfs-import.target
   ```

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

