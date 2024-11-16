Чтобы отменить проброс GPU на хосте Proxmox, вам нужно загрузиться в систему без использования модулей `vfio` и вернуть GPU в контроль хоста. Сделайте следующее:

### 1. **Загрузитесь в режим восстановления**
   - Перезагрузите сервер и на экране загрузки GRUB выберите пункт с `Advanced options for Proxmox` или `Recovery mode`.
   - Если меню GRUB не отображается, удерживайте клавишу `Shift` или `Esc` во время загрузки, чтобы вызвать меню.

---

### 2. **Отредактируйте параметры загрузки (временно)**
   Если вы не можете попасть в Recovery Mode, выполните следующее:
   - В меню GRUB выберите пункт, соответствующий вашей системе (например, `Proxmox`), и нажмите `e`, чтобы отредактировать параметры загрузки.
   - Найдите строку, начинающуюся с `linux`, и удалите `iommu=pt` (или любую другую строку, связанную с VFIO).
   - Удалите параметры, которые указывают `quiet` или `vfio-pci`.
   - Добавьте в конце строки `nomodeset` (это предотвратит попытку инициализации GPU).
   - Нажмите `Ctrl+X` или `F10` для загрузки с изменёнными параметрами.

---

### 3. **Удалите настройки VFIO**
   После загрузки в систему выполните команды:

   ```bash
   sed -i 's/quiet iommu=pt/quiet/' /etc/default/grub
   sed -i '/vfio/d' /etc/modules
   sed -i '/softdep/d' /etc/modprobe.d/vfio.conf
   sed -i '/options vfio-pci/d' /etc/modprobe.d/vfio.conf
   update-grub
   update-initramfs -u -k all
   ```

---

### 4. **Перезагрузите систему**
   После выполнения вышеуказанных шагов выполните перезагрузку:

   ```bash
   shutdown -r now
   ```

---

### 5. **Убедитесь, что сеть работает**
   - Проверьте настройки сети. Если у вас изменился IP-адрес, возможно, он стал динамическим. Попробуйте использовать `ip addr` для определения текущего адреса.
   - Если статический IP сбился, добавьте временную сеть с помощью:

     ```bash
     ip addr add <ваш_IP>/24 dev <ваш_интерфейс>
     ip route add default via <ваш_шлюз>
     ```

   - Далее настройте постоянный IP в `/etc/network/interfaces`.

---

### 6. **(Опционально) Используйте LiveCD или USB для восстановления**
   Если всё равно не удаётся загрузиться в систему, используйте загрузочную флешку с Linux, чтобы войти в систему, примонтировать диск и удалить настройки вручную.

   ```bash
   mount /dev/<ваш_раздел> /mnt
   chroot /mnt
   ```
   Затем выполните команды из шага 3.

---

После выполнения этих действий ваш Proxmox должен загрузиться с работающим GPU на хосте.


---

Вот два скрипта для автоматизации включения и отключения проброса GPU через VFIO. Сохраните их как отдельные файлы на вашем хосте Proxmox.

---

### Скрипт для **включения проброса GPU** (`enable_vfio.sh`):

```bash
#!/bin/bash

# Добавляем параметры для IOMMU в GRUB
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet iommu=pt"/g' /etc/default/grub

# Обновляем конфигурацию GRUB
update-grub

# Добавляем модули VFIO
echo "vfio" >> /etc/modules
echo "vfio_iommu_type1" >> /etc/modules
echo "vfio_pci" >> /etc/modules
echo "vfio_virqfd" >> /etc/modules

# Указываем, какие устройства пробрасывать
echo "options vfio-pci ids=1002:1681,1002:1640" > /etc/modprobe.d/vfio.conf

# Задаем загрузку VFIO до драйверов AMD и звука
echo "softdep radeon pre: vfio-pci" >> /etc/modprobe.d/vfio.conf
echo "softdep amdgpu pre: vfio-pci" >> /etc/modprobe.d/vfio.conf
echo "softdep snd_hda_intel pre: vfio-pci" >> /etc/modprobe.d/vfio.conf

# Обновляем initramfs
update-initramfs -u -k all

# Перезагружаем систему
echo "Система будет перезагружена для применения настроек."
shutdown -r now
```

---

### Скрипт для **отключения проброса GPU** (`disable_vfio.sh`):

```bash
#!/bin/bash

# Убираем параметры IOMMU из GRUB
sed -i 's/quiet iommu=pt/quiet/' /etc/default/grub

# Обновляем конфигурацию GRUB
update-grub

# Удаляем модули VFIO из загрузки
sed -i '/vfio/d' /etc/modules

# Удаляем настройки VFIO из конфигурации modprobe
rm -f /etc/modprobe.d/vfio.conf

# Обновляем initramfs
update-initramfs -u -k all

# Перезагружаем систему
echo "Система будет перезагружена для отключения проброса GPU."
shutdown -r now
```

---

### Инструкция по использованию
1. Сохраните первый скрипт как `enable_vfio.sh`, а второй как `disable_vfio.sh`.
2. Сделайте их исполняемыми:
   ```bash
   chmod +x enable_vfio.sh disable_vfio.sh
   ```
3. Для включения проброса GPU выполните:
   ```bash
   ./enable_vfio.sh
   ```
4. Для отключения проброса GPU выполните:
   ```bash
   ./disable_vfio.sh
   ```

Эти скрипты обеспечивают удобное переключение между состояниями, позволяя автоматизировать процесс.

