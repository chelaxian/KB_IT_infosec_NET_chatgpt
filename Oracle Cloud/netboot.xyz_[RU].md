# Развертывание и тестирование TFTP-сервера

Это руководство содержит пошаговые инструкции по развертыванию TFTP-сервера с использованием `tftp-go`, проверке его работы и скачиванию файлов.

---

## 0. Временно разрешите весь ICMP и UDP-трафик между источником и назначением в обе стороны через брандмауэр или iptables

## 1. Установка и сборка TFTP-сервера

### Предварительные требования
Убедитесь, что у вас установлены Git и Go. Если нет, установите их:

```bash
apt update && apt install -y golang git
```

### Клонирование и сборка `tftp-go`

```bash
git clone https://github.com/lfkeitel/tftp-go
cd tftp-go/
go build
```

### Загрузка загрузочного файла

```bash
wget https://boot.netboot.xyz/ipxe/netboot.xyz-arm64.efi
cp netboot.xyz-arm64.efi arm.efi
chmod 644 arm.efi
```

### Запуск TFTP-сервера

```bash
./tftp-go -server
```

TFTP-сервер начнет раздачу файлов из каталога `/root/tftp-go`.

---

## 2. Проверка работы TFTP-сервера

### Проверка работы сервера
Запустите:

```bash
ps aux | grep tftp
```

Убедитесь, что процесс активен.

### Локальное тестирование
С сервера попробуйте загрузить файл с помощью TFTP:

```bash
tftp 127.0.0.1
get arm.efi
```

Если ошибки отсутствуют, сервер работает корректно.

---

## 3. Скачивание файла с Windows

Включите клиент TFTP в Windows:

```powershell
dism /online /Enable-Feature /FeatureName:TFTP
```

Загрузите файл через TFTP:

```powershell
tftp -i 123.123.123.123 GET arm.efi
```

Проверьте, что файл загружен успешно.

---

## 4. Скачивание файла в OCI (EFI Shell)

### Настройка сети
В EFI Shell назначьте IP-адреса для интерфейсов:

```shell
Shell> fs0:
FS0:\> cd EFI
FS0:\EFI\> ifconfig -s eth0 static 10.0.0.111 255.255.255.0 10.0.0.1
FS0:\EFI\> ifconfig -s eth1 static 172.16.0.111 255.255.255.0 172.16.0.1
FS0:\EFI\> ifconfig -l eth0
FS0:\EFI\> ifconfig -l eth1
```

```copy-paste
fs0:
cd EFI
ifconfig -s eth0 static 10.0.0.111 255.255.255.0 10.0.0.1
ifconfig -s eth1 static 172.16.0.111 255.255.255.0 172.16.0.1
ifconfig -l eth0
ifconfig -l eth1
```

### Скачивание файла
```shell
FS0:\EFI\> ping 123.123.123.123
FS0:\EFI\> tftp 123.123.123.123 arm.efi
```

```copy-paste
ping 123.123.123.123
tftp 123.123.123.123 arm.efi
```

```result
FS0:\EFI\> tftp 123.123.123.123 arm.efi
Downloading the file 'arm.efi'
[=======================================>]    1082 Kb
```

Файл будет загружен и может быть использован для загрузки системы или дальнейшей обработки.

---

## Заключение
Это руководство охватывает:
- Развертывание TFTP-сервера с `tftp-go`
- Проверку его работы
- Скачивание файлов с Windows
- Использование TFTP в EFI Shell на OCI

Ваш TFTP-сервер теперь полностью настроен и готов к работе!
