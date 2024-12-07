я увеличил диск с 47GB до 59GB. как сначала увеличить sda до максимума а потом LVM тоже растянуть на все новое свободное место?

<details><summary>Или под спойлером:</summary>

```shell
root:~# fdisk -l
GPT PMBR size mismatch (97677311 != 123731967) will be corrected by write.
The backup GPT table is not on the end of the device.
Disk /dev/sda: 59 GiB, 63350767616 bytes, 123731968 sectors
Disk model: BlockVolume

Device       Start      End  Sectors  Size Type
/dev/sda1     2048  1050623  1048576  512M EFI System
/dev/sda2  1050624  2050047   999424  488M Linux filesystem
/dev/sda3  2050048 97675263 95625216 45.6G Linux LVM

Disk /dev/mapper/vg-root: 44.64 GiB, 47928311808 bytes, 93609984 sectors

Disk /dev/mapper/vg-swap_1: 980 MiB, 1027604480 bytes, 2007040 sectors
```

</details>

Понял задачу. Увеличим сначала размер диска `sda`, затем расширим раздел `sda3`, после чего перераспределим его для LVM. Вот пошаговое руководство:

---

### Шаг 1: Исправление GPT PMBR Size Mismatch
Убедимся, что GPT структура исправлена. Это не затронет данные, но подготовит диск к дальнейшим действиям.

```bash
gdisk /dev/sda
```

- Выберите `w` (write) для записи изменений и выхода.

---

### Шаг 2: Увеличение раздела `/dev/sda3`
1. Запустите `parted`:
   ```bash
   parted /dev/sda
   ```

2. Выберите раздел `sda3` и увеличьте его до конца диска:
   ```bash
   resizepart 3 100%
   ```

3. Проверьте изменения:
   ```bash
   print
   ```

4. Завершите работу `parted`:
   ```bash
   quit
   ```

---

### Шаг 3: Пересканирование таблицы разделов
Обновим таблицу разделов, чтобы изменения применились:
```bash
partprobe
```

---

### Шаг 4: Расширение физического тома LVM
Теперь нужно расширить физический том (`PV`) на весь доступный размер раздела:

```bash
pvresize /dev/sda3
```

---

### Шаг 5: Расширение Volume Group (VG)
Проверим, появилось ли свободное место:
```bash
vgdisplay
```

Если место есть, используем его для расширения логического тома.

---

### Шаг 6: Расширение логического тома (LV)
Увеличим логический том `vg-root` на всё доступное пространство:

```bash
lvextend -l +100%FREE /dev/mapper/vg-root
```

---

### Шаг 7: Расширение файловой системы
Последний шаг — увеличить файловую систему, чтобы она использовала всё доступное пространство.

#### Для `ext4`:
```bash
resize2fs /dev/mapper/vg-root
```

#### Для `xfs`:
```bash
xfs_growfs /
```

---

### Шаг 8: Проверка результата
Убедимся, что размер увеличен:
```bash
df -h
```

---
вот что у меня получилось
```shell
root:~# parted /dev/sda
GNU Parted 3.5
Using /dev/sda
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) resizepart 3 100%
(parted) print
Model: ORACLE BlockVolume (scsi)
Disk /dev/sda: 63.4GB
Sector size (logical/physical): 512B/4096B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name                  Flags
 1      1049kB  538MB   537MB   fat16        EFI System Partition  boot, esp
 2      538MB   1050MB  512MB   ext2
 3      1050MB  63.4GB  62.3GB                                     lvm

(parted) quit
Information: You may need to update /etc/fstab.

root:~# partprobe
root:~# pvresize /dev/sda3
  Physical volume "/dev/sda3" changed
  1 physical volume(s) resized or updated / 0 physical volume(s) not resized
root:~# vgdisplay
  --- Volume group ---
  VG Name               vg-root
  System ID
  Format                lvm2
  Metadata Areas        1
  Metadata Sequence No  5
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                2
  Open LV               2
  Max PV                0
  Cur PV                1
  Act PV                1
  VG Size               <58.02 GiB
  PE Size               4.00 MiB
  Total PE              14853
  Alloc PE / Size       11672 / 45.59 GiB
  Free  PE / Size       3181 / <12.43 GiB

root:~# lvextend -l +100%FREE /dev/mapper/vg-root
  Size of logical volume vg/root changed from <44.64 GiB (11427 extents) to 57.06 GiB (14608 extents).
  Logical volume vg/root successfully resized.
root:~# resize2fs /dev/mapper/vg-root
resize2fs 1.47.0 (5-Feb-2023)
Filesystem at /dev/mapper/vg-root is mounted on /; on-line resizing required
old_desc_blocks = 6, new_desc_blocks = 8
The filesystem on /dev/mapper/vg-root is now 14958592 (4k) blocks long.

root:~# df -h
Filesystem                     Size  Used Avail Use% Mounted on
udev                           9.8G     0  9.8G   0% /dev
tmpfs                          2.0G  972K  2.0G   1% /run
/dev/mapper/vg-root   56G  4.0G   50G   8% /
tmpfs                          9.8G   28M  9.8G   1% /dev/shm
tmpfs                          5.0M     0  5.0M   0% /run/lock
/dev/sda2                      456M  140M  292M  33% /boot
/dev/sda1                      512M  6.1M  506M   2% /boot/efi
/dev/fuse                      128M   16K  128M   1% /etc/pve
tmpfs                          2.0G     0  2.0G   0% /run/user/0
```

---

Поздравляю! Вы успешно увеличили размер раздела `/dev/sda3`, физического тома LVM, логического тома и файловой системы. Теперь файловая система `/dev/mapper/vg-root` занимает 56 GB, из которых 50 GB свободны.

### Итог выполненных шагов:
1. Исправлена структура GPT с помощью `gdisk`.
2. Раздел `/dev/sda3` увеличен до конца доступного пространства на диске с помощью `parted`.
3. Физический том LVM (`pvresize`) расширен до нового размера раздела.
4. Объем группы томов (VG) увеличен, что позволило выделить свободное место.
5. Логический том (`lvextend`) был расширен на всё доступное место.
6. Файловая система (`resize2fs`) увеличена онлайн без перезагрузки.

Теперь вы можете использовать доступное пространство для хранения данных или других нужд. Если потребуется помощь с другими задачами, обращайтесь! 🚀
