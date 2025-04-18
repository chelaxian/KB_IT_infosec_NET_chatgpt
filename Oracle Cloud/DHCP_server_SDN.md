Ниже — **пошаговая инструкция по настройке DHCP в Proxmox VE через SDN**, соответствующая твоим скриншотам и ручной установке `dnsmasq`. Всё максимально сжато, по делу, и полностью повторяемо.

---

## ✅ Инструкция: **настройка DHCP через SDN в Proxmox VE**

---

### 🧩 Общая схема

- **Zone ID**: `DHCP`
- **VNet Name**: `DHCP`
- **Subnet**: `10.200.200.0/24`, шлюз `10.200.200.1`
- **DHCP-сервер**: встроенный `dnsmasq` (автоматически запускается Proxmox SDN) \
<img width="559" alt="image" src="https://github.com/user-attachments/assets/439e6932-ccc5-45d9-9df0-64b54bb9c71f" />


---

### 1. 🧱 Установка `dnsmasq` на ноде

```bash
apt update
apt install dnsmasq
```

---

### 2. ⚙️ Настройка SDN в веб-интерфейсе Proxmox

#### 2.1. Создание зоны

- Путь: **Datacenter → SDN → Zones → Create**
- Тип: `Simple`
- ID: `DHCP`
- IPAM: `pve` (или `none`)
- Галка **automatic DHCP** — включена ✅

**Результат**: создаётся зона `DHCP` с поддержкой встроенного DHCP через `dnsmasq`. \
<img width="296" alt="image" src="https://github.com/user-attachments/assets/f17d8a49-eb13-457c-b9c4-0b56a73b2371" />

---

#### 2.2. Создание виртуальной сети (VNet)

- Путь: **SDN → Vnets → Create**
- Name: `DHCP`
- Alias: `DHCP`
- Zone: `DHCP`
- Галки: `Isolate Ports` и `VLAN Aware` — **выключены**

**Результат**: создаётся виртуальная L2-сеть `DHCP` внутри одноимённой зоны. \
<img width="260" alt="image" src="https://github.com/user-attachments/assets/af6cc70a-ae78-45f8-aa42-2e819f2937d5" />

---

#### 2.3. Создание подсети (Subnet)

- Путь: **SDN → Subnets → Create**
- Subnet: `10.200.200.0/24`
- Gateway: `10.200.200.1`
- SNAT: включено ✅
- Привязка к VNet: `DHCP`
- Перейди во вкладку **DHCP Ranges** и задай диапазон:
  ```
  10.200.200.100 - 10.200.200.200
  ```

**Результат**: встроенный `dnsmasq` будет автоматически раздавать адреса в этом диапазоне. \
<img width="256" alt="image" src="https://github.com/user-attachments/assets/1662ba7f-b9b0-4d30-b96c-7d9e911039ed" />

---

### 3. 🔄 Применение конфигурации

После внесения изменений нажми:
```text
Datacenter → SDN → Apply
```

Это активирует SDN и поднимет `dnsmasq` на нужной ноде автоматически.

После внесения изменений перезагрузи PVE:
```bash
sudo reboot
```

---

### 4. 🧪 Проверка

#### 4.1. Убедись, что `dnsmasq` поднялся

```bash
ps aux | grep dnsmasq
```

Ожидаемый вывод:
```
/usr/sbin/dnsmasq --conf-file=/etc/pve/sdn/dnsmasq.conf ...
```

#### 4.2. Убедись, что порт 67 слушается

```bash
netstat -tulnp | grep :67
```

#### 4.3. Проверь журнал

```bash
journalctl -u dnsmasq
```

Должно быть видно:
```
DHCP, IP range 10.200.200.100 -- 10.200.200.200
```

---

### 5. ⚡ Подключение ВМ

1. Подключи ВМ к VNet: `DHCP`
2. Внутри ВМ включи DHCP-клиент:
   - **Linux**:
     ```bash
     dhclient -v
     ```
   - **Windows**:
     ```powershell
     ipconfig /renew
     ```

---

### 🧩 Дополнительно (по желанию)

Если хочешь добавить DNS или указать кастомные опции:
- редактируй `/etc/pve/sdn/dnsmasq.conf` — **но не рекомендуется**, т.к. SDN может его перегенерировать.
- или используй вкладку **DNS Server** в настройке Zone/Subnet.
