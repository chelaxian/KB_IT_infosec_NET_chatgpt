# Развертывание и тестирование TFTP-сервера

Это руководство содержит пошаговые инструкции по развертыванию TFTP-сервера с использованием `tftp-go`, проверке его работы и скачиванию файлов.

---

## 0.1 Открытие сетевых доступов

Временно разрешите весь ICMP и UDP-трафик между источником и назначением в обе стороны через брандмауэр или iptables (а также в OCI консоли).

Перейдите на страницу [Default Security List](https://cloud.oracle.com/networking/vcns/) for vcn и настройте брандмауэр, чтобы разрешить весь трафик на виртуальную машину.
![image](https://github.com/user-attachments/assets/010ce2dc-2072-49b1-89b7-0b8c3e6b343b)

## 0.2 Подключение к Cloud Shell

Перейдите в Console Connection и нажмите Launch Cloud Shell Connection.
Появится сессия Cloud Shell. Пока ничего не делайте.
![image](https://github.com/user-attachments/assets/cd3fb36a-cd1e-4108-9142-754ffa660098)

## 1. Установка и сборка TFTP-сервера

Установить TFTP-сервер можно например на соседней always free AMD64 ВМ (для примера с IP-адресом 10.0.0.2)

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

Загрузите файл через TFTP (по внешнему IP-адресу):

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
FS0:\EFI\> ifconfig -s eth0 static 10.0.0.24 255.255.255.0 10.0.0.1
#FS0:\EFI\> ifconfig -s eth1 static 172.16.0.24 255.255.255.0 172.16.0.1 #если несколько сетевых адаптеров
FS0:\EFI\> ifconfig -l eth0
#FS0:\EFI\> ifconfig -l eth1
```

```copy-paste
fs0:
cd EFI
ifconfig -s eth0 static 10.0.0.24 255.255.255.0 10.0.0.1
#ifconfig -s eth1 static 172.16.0.24 255.255.255.0 172.16.0.1 #если несколько сетевых адаптеров
ifconfig -l eth0
ifconfig -l eth1
```

### Скачивание файла
```shell
FS0:\EFI\> ping 10.0.0.2
FS0:\EFI\> tftp 10.0.0.2 arm.efi
```

```copy-paste
ping 10.0.0.2
tftp 10.0.0.2 arm.efi
```

```result
FS0:\EFI\> tftp 10.0.0.2 arm.efi
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
Далее следуйте инструкциям отсюда https://github.com/chelaxian/KB_IT_infosec_NET_chatgpt/blob/main/Oracle%20Cloud/pve8_deb12_install_on_OCI.md
