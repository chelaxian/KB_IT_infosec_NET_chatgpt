\[ChatGPT 4]

Вот **комбинированная и финальная пошаговая инструкция**, как **объединить 5 VPS в единое распределённое хранилище на 250 ГБ**, **предварительно связав их в полносвязную сеть через WireGuard**, и затем развернуть **кластер GlusterFS**, с пробросом общей папки в LXC-контейнеры Proxmox VE.

---

# 🧩 Комбинированная инструкция: WireGuard + GlusterFS на 5 VPS

## 🧱 ЧАСТЬ 1: Объединение узлов в полносвязную WireGuard-сеть

### Шаг 1. Установка WireGuard на всех 5 VPS

На **каждом** из серверов:

```bash
sudo apt update
sudo apt install -y wireguard
```

Сгенерируйте ключи:

```bash
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
```

Сохраните вывод:

```bash
cat /etc/wireguard/privatekey
cat /etc/wireguard/publickey
```

### Шаг 2. Настройка сети `10.8.0.0/24`

* Пусть IP-адреса для WG будут:

  * `server1` → `10.8.0.1`
  * `server2` → `10.8.0.2`
  * `server3` → `10.8.0.3`
  * `server4` → `10.8.0.4`
  * `server5` → `10.8.0.5`

Создайте файл `/etc/wireguard/wg0.conf` **на каждом сервере**:

```ini
[Interface]
PrivateKey = <PRIVATE_KEY_ТЕКУЩЕГО_СЕРВЕРА>
Address = 10.8.0.X/24
ListenPort = 51820

# Пример: для server1 добавляем остальных как peer'ов

[Peer]
PublicKey = <PUBKEY_server2>
AllowedIPs = 10.8.0.2/32
Endpoint = <EXTERNAL_IP_server2>:51820
PersistentKeepalive = 25

[Peer]
PublicKey = <PUBKEY_server3>
AllowedIPs = 10.8.0.3/32
Endpoint = <EXTERNAL_IP_server3>:51820
PersistentKeepalive = 25

[Peer]
PublicKey = <PUBKEY_server4>
AllowedIPs = 10.8.0.4/32
Endpoint = <EXTERNAL_IP_server4>:51820
PersistentKeepalive = 25

[Peer]
PublicKey = <PUBKEY_server5>
AllowedIPs = 10.8.0.5/32
Endpoint = <EXTERNAL_IP_server5>:51820
PersistentKeepalive = 25
```

На других серверах аналогично, изменяя `[Interface]` и `[Peer]`-блоки.

Убедитесь, что `ufw` или `iptables` разрешает UDP 51820:

```bash
ufw allow 51820/udp
```

Запуск туннеля:

```bash
chmod 600 /etc/wireguard/wg0.conf
wg-quick up wg0
systemctl enable wg-quick@wg0
```

Проверьте пингом и `wg show`, что все пиры подключены.

---

## 📦 ЧАСТЬ 2: Настройка кластера GlusterFS поверх WireGuard

### Шаг 3. Установка GlusterFS

На **всех 5 VPS** (Debian 11):

```bash
sudo apt update && sudo apt install -y glusterfs-server
sudo systemctl enable --now glusterd
```

Убедитесь, что сервис работает:

```bash
sudo systemctl status glusterd
```

### Шаг 4. Настройка `/etc/hosts` или использование IP

Если нет DNS, пропишите в `/etc/hosts` на всех серверах:

```text
10.8.0.1 server1
10.8.0.2 server2
10.8.0.3 server3
10.8.0.4 server4
10.8.0.5 server5
```

### Шаг 5. Создание brick-директории

На каждом узле:

```bash
sudo mkdir -p /gluster-storage
```

### Шаг 6. Объединение узлов в trusted pool

На **одном из серверов** (например, server1):

```bash
gluster peer probe server2
gluster peer probe server3
gluster peer probe server4
gluster peer probe server5
```

Проверь статус:

```bash
gluster peer status
```

### Шаг 7. Создание распределённого тома

```bash
sudo gluster volume create vps_shared \
  server1:/gluster-storage \
  server2:/gluster-storage \
  server3:/gluster-storage \
  server4:/gluster-storage \
  server5:/gluster-storage \
  force
```

Запуск тома:

```bash
sudo gluster volume start vps_shared
gluster volume info vps_shared
```

---

## 📂 ЧАСТЬ 3: Монтирование общего тома

### Шаг 8. Создание точки монтирования и монтирование

На **каждом VPS**:

```bash
sudo mkdir -p /mnt/vps_shared
sudo mount -t glusterfs localhost:/vps_shared /mnt/vps_shared
```

Добавьте в `/etc/fstab`:

```text
localhost:/vps_shared /mnt/vps_shared glusterfs defaults,_netdev 0 0
```

Проверьте:

```bash
df -h
df -h | grep vps_shared
ls /mnt/vps_shared
```

---

## 📦 ЧАСТЬ 4: Проброс папки в LXC-контейнеры Proxmox

### Шаг 9. Добавление bind-mount в контейнер

На **Proxmox-хосте** (в каждом VPS):

```bash
pct set <CTID> -mp0 /mnt/vps_shared,mp=/mnt/vps_shared
```

Или вручную в `/etc/pve/lxc/<CTID>.conf`:

```text
mp0: /mnt/vps_shared,mp=/mnt/vps_shared
```

**Контейнер должен быть остановлен!**

Затем запустите контейнер:

```bash
pct start <CTID>
```

Внутри контейнера:

```bash
ls /mnt/vps_shared
```

---

## ✅ Проверка

1. Создайте файл на одном узле:

   ```bash
   echo "test" > /mnt/vps_shared/hello.txt
   ```

2. Убедитесь, что файл виден на других VPS и в контейнерах:

   ```bash
   cat /mnt/vps_shared/hello.txt
   ```

3. Проверьте, как заполняется пространство (`df -h`, `gluster volume status`, `gluster volume info`).

---

## 📌 Примечания

* GlusterFS не делит один файл на части — каждый файл хранится **целиком** на одном узле.
* Максимальный размер одного файла — \~50 ГБ.
* GlusterFS не любит обрывы связи: WireGuard обеспечивает стабильный туннель.
* Для автоматического восстановления при сбоях можно рассмотреть GlusterFS Heal или использовать Replicated Volumes.

---
Так же можно собрать `ansible-playbook` или bash-скрипты для ускорения и автоматизации всех шагов.
