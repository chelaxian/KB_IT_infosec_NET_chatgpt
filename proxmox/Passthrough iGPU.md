Полную инструкцию можно найти на [GitHub](https://github.com/isc30/ryzen-7000-series-proxmox/blob/main/README.md).

Для настройки проброса встроенной видеокарты AMD (например, Radeon 680M/780M) в Proxmox VE на процессорах Ryzen 7000 серии, следуйте следующим шагам:

### 1. Установка Proxmox VE
1. **Загрузите ISO Proxmox VE** с официального сайта и создайте установочный USB с помощью Rufus.
2. **Установите Proxmox** на машину и выполните начальную настройку, включая исправление проблем с графическим интерфейсом (если используете Proxmox 7.4).
3. **Подключитесь к Proxmox через SSH** и переключитесь на репозитории без подписки:
    ```bash
    bash -c "$(wget -qLO - https://github.com/tteck/Proxmox/raw/main/misc/post-pve-install.sh)"
    ```

### 2. Настройка IOMMU и VFIO
1. **Настройте IOMMU** в BIOS/UEFI:
   - Включите опции IOMMU и SVM.
2. **Добавьте параметры IOMMU в GRUB**:
    ```bash
    sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet"/GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"/g' /etc/default/grub
    update-grub
    ```
3. **Настройте модули VFIO**:
    ```bash
    echo "vfio" >> /etc/modules
    echo "vfio_iommu_type1" >> /etc/modules
    echo "vfio_pci" >> /etc/modules
    echo "vfio_virqfd" >> /etc/modules
    ```
4. **Укажите устройства для VFIO**:
    - Найдите идентификаторы PCI вашей видеокарты и аудиоустройства:
        ```bash
        lspci -nn | grep -e 'AMD/ATI'
        ```
    - Добавьте их в конфигурацию VFIO:
        ```bash
        echo "options vfio-pci ids=1002:1681,1002:1640" >> /etc/modprobe.d/vfio.conf
        ```

5. **Обновите initramfs и перезагрузите систему**:
    ```bash
    update-initramfs -u -k all
    shutdown -r now
    ```

### 3. Настройка Windows VM
1. **Создайте виртуальную машину (ВМ)** с Windows 10:
    - Загрузите ISO-образ Windows и создайте ВМ с параметрами:
      - Machine: `q35`
      - BIOS: `SeaBIOS`
      - Диск: `64GB`, Discard: `ON`, SSD: `ON`
2. **После установки Windows** остановите ВМ и настройте GPU BIOS:
    - Скачайте и скомпилируйте `vbios.c` для извлечения vBIOS:
        ```bash
        gcc vbios.c -o vbios
        ./vbios
        ```
    - Переместите файл `vbios_*.bin` в `/usr/share/kvm/`.
3. **Добавьте GPU и аудиоустройства в ВМ** через веб-интерфейс Proxmox, выбрав соответствующие PCI-устройства.

4. **Измените конфигурацию ВМ** для использования корректного vBIOS:
    - Отредактируйте файл конфигурации `/etc/pve/qemu-server/<VM_ID>.conf`:
    ```diff
    +args: -cpu 'host,-hypervisor,kvm=off'
    hostpci0: 0000:34:00.0,pcie=1,romfile=vbios_7xxx.bin
    hostpci1: 0000:34:00.1,pcie=1
    ```

### 4. Установка драйверов и исправление ошибок
1. **Установите драйверы VirtIO и драйверы AMD** (используйте оффлайн-установщик).
2. **Установите RadeonResetBugFix** для предотвращения ошибок "AMD Reset Bug".

### 5. Настройка Primary GPU
1. Включите удаленный доступ (RDP) в Windows и установите GPU как основной.
2. Запустите ВМ и подключитесь через RDP или подключите монитор к проброшенному GPU.

### 6. Настройка OVMF (UEFI BIOS) для решения ошибки 43
1. Скачайте и установите `AMDGopDriver.rom`, добавьте его в конфигурацию:
    ```diff
    hostpci1: 0000:34:00.1,pcie=1,romfile=AMDGopDriver.rom
    ```

### 7. Перезагрузите ВМ и проверьте работу GPU.

Следуя этим шагам, вы сможете успешно настроить проброс GPU и USB-устройств на Proxmox VE с процессорами Ryzen 7000 серии и встроенными графическими процессорами AMD.
