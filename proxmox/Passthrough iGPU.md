Полную инструкцию можно найти на [GitHub](https://github.com/isc30/ryzen-7000-series-proxmox/blob/main/README.md).

Для настройки проброса встроенной видеокарты AMD (например, Radeon 680M/780M) в Proxmox VE на процессорах Ryzen 7000 серии, следуйте следующим шагам:

### 1. Установка Proxmox VE
1. **Загрузите ISO Proxmox VE** с официального сайта и создайте установочный USB с помощью Rufus.
2. **Установите Proxmox** на машину и выполните начальную настройку, включая исправление проблем с графическим интерфейсом.
       <details><summary>Спойлер `(если используете Proxmox 7.4)`</summary>

    ```bash
    Xorg -configure
    cp /root/xorg.conf.new /etc/X11/xorg.conf
    sed -i 's/amdgpu/fbdev/g' /etc/X11/xorg.conf
    ```

    </details>
    
4. **Подключитесь к Proxmox через SSH** и переключитесь на репозитории без подписки:
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
      - Создайте файл на хосте proxmox со следующим содержимым:
    <details><summary>Спойлер `vbios.c`</summary>

    ```c
    #include <stdint.h>
    #include <stdio.h>
    #include <stdlib.h>

    typedef uint32_t ULONG;
    typedef uint8_t UCHAR;
    typedef uint16_t USHORT;

    typedef struct {
        ULONG Signature;
        ULONG TableLength; // Length
        UCHAR Revision;
        UCHAR Checksum;
        UCHAR OemId[6];
        UCHAR OemTableId[8]; // UINT64  OemTableId;
        ULONG OemRevision;
        ULONG CreatorId;
        ULONG CreatorRevision;
    } AMD_ACPI_DESCRIPTION_HEADER;

    typedef struct {
        AMD_ACPI_DESCRIPTION_HEADER SHeader;
        UCHAR TableUUID[16]; // 0x24
        ULONG VBIOSImageOffset; // 0x34. Offset to the first GOP_VBIOS_CONTENT block from the beginning of the stucture.
        ULONG Lib1ImageOffset; // 0x38. Offset to the first GOP_LIB1_CONTENT block from the beginning of the stucture.
        ULONG Reserved[4]; // 0x3C
    } UEFI_ACPI_VFCT;

    typedef struct {
        ULONG PCIBus; // 0x4C
        ULONG PCIDevice; // 0x50
        ULONG PCIFunction; // 0x54
        USHORT VendorID; // 0x58
        USHORT DeviceID; // 0x5A
        USHORT SSVID; // 0x5C
        USHORT SSID; // 0x5E
        ULONG Revision; // 0x60
        ULONG ImageLength; // 0x64
    } VFCT_IMAGE_HEADER;

    typedef struct {
        VFCT_IMAGE_HEADER VbiosHeader;
        UCHAR VbiosContent[1];
    } GOP_VBIOS_CONTENT;

    int main(int argc, char** argv)
    {
        FILE* fp_vfct;
        FILE* fp_vbios;
        UEFI_ACPI_VFCT* pvfct;
        char vbios_name[0x400];

        if (!(fp_vfct = fopen("/sys/firmware/acpi/tables/VFCT", "r"))) {
            perror(argv[0]);
            return -1;
        }

        if (!(pvfct = malloc(sizeof(UEFI_ACPI_VFCT)))) {
            perror(argv[0]);
            return -1;
        }

        if (sizeof(UEFI_ACPI_VFCT) != fread(pvfct, 1, sizeof(UEFI_ACPI_VFCT), fp_vfct)) {
            fprintf(stderr, "%s: failed to read VFCT header!\n", argv[0]);
            return -1;
        }

        ULONG offset = pvfct->VBIOSImageOffset;
        ULONG tbl_size = pvfct->SHeader.TableLength;

        if (!(pvfct = realloc(pvfct, tbl_size))) {
            perror(argv[0]);
            return -1;
        }

        if (tbl_size - sizeof(UEFI_ACPI_VFCT) != fread(pvfct + 1, 1, tbl_size - sizeof(UEFI_ACPI_VFCT), fp_vfct)) {
            fprintf(stderr, "%s: failed to read VFCT body!\n", argv[0]);
            return -1;
        }

        fclose(fp_vfct);

        while (offset < tbl_size) {
            GOP_VBIOS_CONTENT* vbios = (GOP_VBIOS_CONTENT*)((char*)pvfct + offset);
            VFCT_IMAGE_HEADER* vhdr = &vbios->VbiosHeader;

            if (!vhdr->ImageLength)
                break;

            snprintf(vbios_name, sizeof(vbios_name), "vbios_%x_%x.bin", vhdr->VendorID, vhdr->DeviceID);

            if (!(fp_vbios = fopen(vbios_name, "wb"))) {
                perror(argv[0]);
                return -1;
            }

            if (vhdr->ImageLength != fwrite(&vbios->VbiosContent, 1, vhdr->ImageLength, fp_vbios)) {
                fprintf(stderr, "%s: failed to dump vbios %x:%x\n", argv[0], vhdr->VendorID, vhdr->DeviceID);
                return -1;
            }

            fclose(fp_vbios);

            printf("dump vbios %x:%x to %s\n", vhdr->VendorID, vhdr->DeviceID, vbios_name);

            offset += sizeof(VFCT_IMAGE_HEADER);
            offset += vhdr->ImageLength;
        }

        return 0;
    }
    ```

    </details>
    
    - Скомпилируйте `vbios.c` для извлечения vBIOS:
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
