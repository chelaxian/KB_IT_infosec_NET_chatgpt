
# 1. Установка Proxmox VE на OCI

ссылки на источник: \
https://frank-ruan.com/2023/03/18/installing-proxmox-ve-on-oci/ \
https://frank-ruan.com/2023/06/24/configuring-network-for-proxmox-ve-on-oci-arm/ 

---

## 1.1. Настройка экземпляра

Сначала войдите в консоль Oracle Cloud и перейдите на страницу [Instances](https://cloud.oracle.com/compute/instances). Создайте экземпляр Ampere.
Операционная система значения не имеет, так как мы заменим её позже.

![image](https://github.com/user-attachments/assets/81901937-83dc-411a-a106-46035069dc74)

Далее перейдите на страницу [Default Security List for vcn](https://cloud.oracle.com/networking/vcns/) и настройте брандмауэр, чтобы разрешить весь трафик на виртуальную машину.

<img width="992" alt="image" src="https://github.com/user-attachments/assets/ebc57b81-8c87-4b36-a985-cdbec6791298">


---

## 1.2. Подключение к Cloud Shell

Перейдите в `Console Connection` и нажмите `Launch Cloud Shell Connection`.

Появится сессия Cloud Shell. Пока ничего не делайте.

![image](https://github.com/user-attachments/assets/8d5edb75-cb16-48d1-95fa-b1efed76ac59)

---

## 1.3. Загрузка EFI файлов

Подключитесь к машине по SSH и скачайте необходимые EFI файлы:

```bash
sudo -i
cd /boot/efi
wget https://boot.netboot.xyz/ipxe/netboot.xyz-arm64.efi
```
![image](https://github.com/user-attachments/assets/86d75c8d-1bb6-433d-a364-0281fd3e42a4)

После этого отключитесь от машины и вернитесь в консоль OCI.

---

## 1.4. Перезагрузка и вход в Boot Maintenance Manager

Нажмите `Reboot` на странице деталей и выберите опцию `Force reboot the instance by immediately powering off, then powering back on`.

В момент перезагрузки обратите внимание на окно Cloud Shell. Нажимайте ESC, пока не войдете в страницу, похожую на BIOS.  

![image](https://github.com/user-attachments/assets/f6997145-1f7c-4b74-8968-804f61c97936) 

Управляйте стрелками и перейдите в `Boot Maintenance Manager` -> `Boot From File` -> Выберите единственный жесткий диск -> `netboot.xyz-arm64.efi`.

---

## 1.5. Установка Debian

В интерфейсе iPXE выберите `Linux Network Installs` -> `Debian` -> `Debian 12.0 (bookworm)` -> `Text Based Install`.

![image](https://github.com/user-attachments/assets/14eb000a-4f75-4912-b583-103924c93a83)

Укажите домен для машины. Например, если ваш домен `pve.domain.net`, а IP `1.1.1.1`, добавьте запись A.

Используйте `pve` как имя хоста и `pve.domain.net` как домен.

При настройке разделов выберите `Guided - use entire disk and set up LVM`, так как Proxmox предпочитает LVM.

![image](https://github.com/user-attachments/assets/ba40e7cd-d708-4121-89b4-bdf59830514c)

Остальные настройки оставьте по умолчанию.

![image](https://github.com/user-attachments/assets/cdc383f4-0052-4221-9317-d35628f6809c)

![image](https://github.com/user-attachments/assets/8200f7fc-07b4-4e2b-b50c-1586c06c9cfe)

---

## 1.6. Настройка Debian после установки

После установки войдите в машину через Cloud Shell под пользователем root и добавьте свой SSH-ключ в `~/.ssh`.

По умолчанию OpenSSH Server не позволяет входить в систему root-пользователю по паролю, но это возможно с использованием SSH-ключа.

Либо же можно разрешить вход под `root` с помощью внесения сообвествующих настроек: \
`PermitRootLogin yes` и `PasswordAuthentication yes` \
 в файлы `/etc/ssh/ssh_config` и `/etc/ssh/sshd_config` и последующего перезапуска сервиса командами

```bash
systemctl restart ssh
systemctl restart sshd
```

---

### Установка полезного ПО

Установите следующие пакеты:

```bash
apt install sudo wget curl iftop vnstat neofetch vim nano net-tools
```

---

### Настройка сетевого интерфейса

Проверьте IP адрес с помощью команды:

```bash
ip address
```

Откройте файл `/etc/network/interfaces` в вашем редакторе. Измените его следующим образом:

```bash
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enp0s6
# iface enp0s6 inet dhcp
# Define Static IP
iface enp0s6 inet static
	address 10.0.0.132
	netmask 255.255.255.0
	gateway 10.0.0.1
```

Настройте маску сети в зависимости от CIDR. Например, /24 означает `255.255.255.0`.

---

### Добавление записи в /etc/hosts

Убедитесь, что имя хоста вашей машины разрешается через `/etc/hosts`. Например:

```bash
127.0.0.1       localhost.localdomain localhost
10.0.0.132   prox4m1.proxmox.com prox4m1

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```

Проверьте настройки с помощью команды:

```bash
hostname --ip-address
```

---

## 1.7. Установка Proxmox VE

Добавьте репозиторий Proxmox VE:

```bash
echo 'deb [arch=arm64] https://mirrors.apqa.cn/proxmox/debian/pve bookworm port'>/etc/apt/sources.list.d/pveport.list
```

Добавьте ключ репозитория:

```bash
curl -L https://mirrors.apqa.cn/proxmox/debian/pveport.gpg -o /etc/apt/trusted.gpg.d/pveport.gpg 
```

Обновите репозиторий и систему:

```bash
apt update && apt full-upgrade
```

Установите пакеты Proxmox VE:

```bash
apt install proxmox-ve postfix open-iscsi
```

Выберите нужные параметры при установке пакетов, например, для postfix.

После завершения установки подключитесь к веб-интерфейсу (https://youripaddress:8006).

---

## 1.8. Настройка моста

Добавьте в файл `/etc/network/interfaces` следующие строки:

```bash
auto vmbr0
iface vmbr0 inet static
        address 10.200.0.1/24
        bridge_ports none
        bridge_stp off
        bridge_fd 0
        post-up echo 1 > /proc/sys/net/ipv4/ip_forward
        post-up iptables -t nat -A POSTROUTING -s '10.200.0.0/24' -o enp0s6 -j MASQUERADE
        post-down iptables -t nat -D POSTROUTING -s '10.200.0.0/24' -o enp0s6 -j MASQUERADE
```

Перезапустите сетевой сервис:

```bash
systemctl restart networking
```

---

## 1.9. Настройка ZFS

Если вы хотите иметь возможность делать снапшоты VM и LXC тогда вам необходимо установить файловую систему ZFS. Процесс установки описан в   
[статье по ссылке](https://github.com/chelaxian/KB_IT_infosec_NET_chatgpt/blob/main/proxmox/pve8_deb12_ZFS_OCI.md)

---

## 1.10. Создание контейнера

Перейдите в консоль PVE и создайте контейнер. Не забудьте предварительно скачать шаблон контейнера в веб-интерфейсе `Proxmox VE` в разделе `CT Templates` или по ссылке:  
https://uk.lxd.images.canonical.com/images/

<img width="565" alt="image" src="https://github.com/user-attachments/assets/29bfc31b-d320-49c6-825a-ff3accc18b68">

После входа в контейнер установите следующие пакеты и настройте доступ по SSH:
```bash
apt install sudo cron htop nano net-tools dnsutils wget curl git speedtest-cli openssh-server
```
