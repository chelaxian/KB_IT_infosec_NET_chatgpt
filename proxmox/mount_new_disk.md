```markdown
# Инструкция по работе с новым разделом диска на Linux

## Шаги создания раздела и монтирования

### 1. Создание нового раздела с помощью `fdisk`
Запустите утилиту `fdisk` для создания нового раздела:
```bash
fdisk /dev/sda
```
Пример работы с `fdisk`:
```
Welcome to fdisk (util-linux 2.38.1).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.

Device does not contain a recognized partition table.
Created a new DOS (MBR) disklabel with disk identifier 0xabb0aa87.

Command (m for help): n
Partition type
   p   primary (0 primary, 0 extended, 4 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (1-4, default 1):
First sector (2048-123731967, default 2048):
Last sector, +/-sectors or +/-size{K,M,G,T,P} (2048-123731967, default 123731967):

Created a new partition 1 of type 'Linux' and of size 59 GiB.

Command (m for help): w
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
```

### 2. Проверка созданного раздела
Убедитесь, что новый раздел создан, с помощью команды:
```bash
fdisk -l
```
Пример вывода:
```
Disk /dev/sda: 59 GiB, 63350767616 bytes, 123731968 sectors
Disk model: BlockVolume
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 1048576 bytes
Disklabel type: dos
Disk identifier: 0xabb0aa87

Device     Boot Start       End   Sectors Size Id Type
/dev/sda1        2048 123731967 123729920  59G 83 Linux
```

### 3. Создание файловой системы на новом разделе
Создайте файловую систему (например, `ext4`) на разделе `/dev/sda1`:
```bash
mkfs.ext4 /dev/sda1
```

### 4. Создание точки монтирования
Создайте директорию для монтирования, если она еще не существует:
```bash
mkdir -p /mnt/zfs59
```

### 5. Монтирование раздела
Смонтируйте новый раздел в созданную директорию:
```bash
mount /dev/sda1 /mnt/zfs59
```

### 6. Проверка монтирования
Убедитесь, что раздел успешно смонтирован:
```bash
df -h
```
Пример вывода:
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        59G   24K   59G   1% /mnt/zfs59
```

### 7. Добавление в автозагрузку (опционально)
Чтобы раздел монтировался автоматически при загрузке системы, добавьте его в файл `/etc/fstab`:
1. Узнайте UUID нового раздела:
   ```bash
   blkid /dev/sda1
   ```
   Пример вывода:
   ```
   /dev/sda1: UUID="123e4567-e89b-12d3-a456-426614174000" TYPE="ext4"
   ```

2. Добавьте строку в `/etc/fstab`:
   ```plaintext
   UUID=123e4567-e89b-12d3-a456-426614174000 /mnt/zfs59 ext4 defaults 0 2
   ```

## Заключение
Следуя этим шагам, вы успешно создадите новый раздел, настроите файловую систему и смонтируете его. При необходимости настройка автозагрузки обеспечит автоматическое монтирование раздела при старте системы.
```
