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
---

## ‼️ Описание поведение **ванильного GlusterFS**: при **дисперсном (distribute-only) типе тома**:

* выбор backend-сервера (brick'а) идёт **по хешу имени файла**,
* **никакой проверки на свободное место при записи нет**,
* если выбранный brick **не может принять файл** (место кончилось), Gluster просто **падает с ошибкой `ENOSPC` (нет места)**,
* никакого "перебора других brick’ов" **не будет** — Gluster не перераспределяет файл **автоматически**.

---

## 🔥 Что происходит в такой ситуации

> У тебя: 8 серверов = 8 bricks, 360 ГБ суммарно,
> но один из серверов полностью заполнен.

📦 Ты пишешь файл `video.mp4` (1.5 ГБ) —
его имя по хешу попадает на **заполненный brick**, и…

➡️ Gluster возвращает **ошибку записи**, несмотря на то, что **на других bricks места полно**.

---

## 🔁 Что можно сделать в этот момент?

Кратко:
**Нет способа "заставить Gluster" перекинуть файл на другой brick в distribute-only.**

Ты можешь только:

---

### ✅ Вариант 1: изменить имя файла вручную

Поскольку выбор brick зависит от **хеша имени файла**, ты можешь:

1. Изменить имя файла: например, добавить постфикс:
   `video.mp4` → `video__1.mp4`
2. Gluster пересчитает хеш, и теперь он **может попасть на другой brick**.
3. Повторять это до тех пор, пока не попадёт на свободный brick.

```bash
cp video.mp4 /mnt/glusterfs/video__1.mp4
# Если опять ENOSPC, пробуй video__2.mp4 и т.д.
```

✔️ Работает.
❌ Но вручную — неудобно, если не автоматизировать.

---

### ✅ Вариант 2: вручную почистить или увеличить место на brick'е

Если ты **можешь очистить** место на заполненном сервере (удалить лишние файлы, добавить диск, увеличить partition) — это **самый прямой способ**.

```bash
ssh brick7 'rm -rf /bricks/data/some_old_files'
# или добавить диск и ребалансировать
```

---

### ✅ Вариант 3: добавить новый brick и сделать ребаланс

Если у тебя есть ещё хосты или свободные диски:

1. Добавь новый brick:

```bash
gluster volume add-brick myvol serverX:/brick/path
```

2. Запусти **ребалансировку данных**:

```bash
gluster volume rebalance myvol start
```

Это заставит Gluster перераспределить уже существующие файлы по новым rules (включая новый brick).

❗ **Но это НЕ решит ошибку текущей записи**. Просто со временем разгрузит переполненные bricks.

---

### ✅ Вариант 4: использовать **replica** или **disperse** вместо distribute-only

Если у тебя настроен **replica volume** (например, 2x реплика), то запись идёт **на 2 brick’а одновременно**.
Тогда, если один из них полон, запись может **всё ещё пройти**, если у второго есть место.

Но:

* расход места выше (репликация),
* всё равно при полном заполнении всех копий — упадёт.

---

## ❌ Что НЕ поможет

| Метод                                | Почему не сработает                         |
| ------------------------------------ | ------------------------------------------- |
| Перезапуск `glusterd`                | Не влияет на выбор brick                    |
| Перезапуск клиента / монтирование    | Brick всё равно выбирается по хешу          |
| Использование `du` / `df` на клиенте | Клиент не знает о свободном месте на bricks |

---

## ✅ Заключение

Если не хочешь делать автоматизацию — у тебя **всего два рабочих варианта**:

1. **Менять имя файла**, пока не попадёт на свободный brick (ручками или скриптом).
2. **Освободить место** или **добавить новый brick и перебалансировать** (`gluster volume rebalance`).

---

## 🛠 Можно написать скрипт `smart_cp.sh`, который будет:

* узнавать размер файла,
* делать хеши от разных имён (`filename__1`, `__2`, и т.д.),
* находить соответствующий brick по алгоритму,
* проверять на нём свободное место,
* и копировать файл, если хватает места.

---

Скрипт проверяет доступность Gluster-нод **каждые 60 секунд**, потому что в нём указана переменная:

```bash
INTERVAL=60
```

Это значит:

* каждые 60 секунд выполняется проверка всех IP по порту 24007;
* если хотя бы один не отвечает — будет произведён `systemctl restart glusterd`, затем пауза 10 секунд;
* дальше снова цикл ожидания и проверки.

---

### 🔄 Хочешь изменить период?

Просто поменяй значение переменной `INTERVAL=60` в `/usr/local/bin/gluster_watchdog.sh` на нужное тебе, например:

```bash
INTERVAL=15  # Проверка каждые 15 секунд
```

После этого:

```bash
systemctl restart gluster-watchdog.service
```

Вот **полная инструкция** по работе с кластером **GlusterFS**, включая добавление новых узлов, синхронизацию, ребалансировку, проверки состояния, удаление и восстановление. Всё оформлено как **шпаргалка для продакшн-кластера**:

---

## 📦 1. Добавление нового узла в кластер (peer)

### На **любом существующем** узле кластера:

```bash
gluster peer probe <hostname или IP нового узла>
```

❗ Убедись, что на новом узле:

* открыт порт `24007/tcp` (GlusterD)
* работает `glusterd`
* совпадают версии GlusterFS
* корректно разрешаются имена/хосты (`/etc/hosts` или DNS)

👉 Проверить:

```bash
gluster peer status
```

---

## 🧱 2. Создание тома (volume)

```bash
gluster volume create <volume-name> replica <N> transport tcp \
<host1>:/gluster_bricks/brick1 \
<host2>:/gluster_bricks/brick1 \
<hostN>:/gluster_bricks/brick1 force
```

> 📌 Пример: replica 3 — три копии

Запустить:

```bash
gluster volume start <volume-name>
```

Проверить:

```bash
gluster volume info
```

---

## 🔁 3. Подключение нового участника к существующему тому

1. **Создай brick** на новом узле:

```bash
mkdir -p /gluster_bricks/brick1
```

2. **Добавь brick в volume**:

```bash
gluster volume add-brick <volume-name> <new-host>:/gluster_bricks/brick1
```

❗ Для **replica** укажи:

```bash
gluster volume add-brick <volume-name> replica <new-replica-count> \
<host1>:/brick1 <host2>:/brick1 <new-host>:/brick1
```

Проверка:

```bash
gluster volume info
```

---

## 🔄 4. Ребалансировка (rebalancing) после добавления bricks

```bash
gluster volume rebalance <volume-name> start
```

Проверка прогресса:

```bash
gluster volume rebalance <volume-name> status
```

Остановить:

```bash
gluster volume rebalance <volume-name> stop
```

---

## ⚙️ 5. Синхронизация конфигурации на всех нодах

```bash
gluster volume sync <volume-name> all
```

---

## 🧼 6. Проверка статуса и здоровья

```bash
gluster peer status
gluster volume status
gluster volume info
gluster volume heal <volume-name> info
```

---

## 🩹 7. Восстановление / Heal

Проверка недостающих файлов:

```bash
gluster volume heal <volume-name> info
```

Принудительное лечение:

```bash
gluster volume heal <volume-name> full
```

---

## 🧨 8. Удаление brick

❗ Сначала **rebalance**, потом **remove**:

```bash
gluster volume remove-brick <volume-name> replica <new-count> \
<host-to-remove>:/brick1 start
gluster volume remove-brick <volume-name> ... status
gluster volume remove-brick <volume-name> ... commit
```

---

## 🗑️ 9. Удаление участника из кластера

1. Убедись, что **на этом узле больше нет bricks** (`gluster volume info`)
2. Удали peer:

```bash
gluster peer detach <host>
```

Если нода мертва и восстановлению не подлежит:

```bash
gluster peer detach <host> force
```

---

## 📦 10. Монтирование тома на клиенте

На клиенте (должен быть установлен `glusterfs-client`):

```bash
mount -t glusterfs <gluster-host>:/<volume-name> /mnt/gluster
```

---

## 🔐 11. Работа через FUSE или NFS (по выбору)

* FUSE: `mount -t glusterfs`
* NFS: `mount -t nfs -o vers=3 <host>:/<volume> /mnt`

---

## 🧭 12. Автоматизация проверки кластера (помимо watchdog-а)

Периодическая проверка состояния (cron или systemd):

```bash
gluster volume status | grep -q 'Offline' && echo "Есть оффлайн brick-и"
gluster peer status | grep -q 'Disconnected' && echo "Есть отвалившиеся peer-ы"
```

---

## 📌 Советы

| Что                       | Рекомендация                                                                        |
| ------------------------- | ----------------------------------------------------------------------------------- |
| **Синхронизация времени** | Установи `chrony` или `ntpd` на всех узлах                                          |
| **DNS/имена**             | Лучше использовать IP или прописать в `/etc/hosts`                                  |
| **Разделы для brick'ов**  | Не монтируй `/brick1` на `/` — выделяй отдельный раздел или LVM                     |
| **Volume Options**        | Включи полезные фичи: `performance.cache-size`, `server.allow-insecure` и пр.       |
| **WireGuard / VPN**       | Используй `PersistentKeepalive` + убедись, что `glusterd` стартует после `wg-quick` |

---




