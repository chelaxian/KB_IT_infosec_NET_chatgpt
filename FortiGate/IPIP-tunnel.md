### Итоговый план настройки IPIP-туннеля между FortiGate и Ubuntu с нуля

---

#### **На стороне Ubuntu**

1. **Обновление системы и установка необходимых пакетов**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install iproute2 net-tools iptables-persistent -y
   ```

2. **Настройка IPIP-туннеля**
   - Создать туннель:
     ```bash
     sudo ip tunnel add ipip-tunnel mode ipip local 10.0.0.2 remote 192.168.1.254 dev ens3
     ```
   - Назначить IP-адрес туннелю:
     ```bash
     sudo ip addr add 10.0.1.1/24 dev ipip-tunnel
     ```
   - Активировать интерфейс:
     ```bash
     sudo ip link set ipip-tunnel up
     ```

3. **Настройка маршрутов**
   - Добавить маршруты для удаленных сетей:
     ```bash
     sudo ip route add 192.168.1.0/24 dev ipip-tunnel
     sudo ip route add 10.11.0.0/24 dev ipip-tunnel
     ```

4. **Установка правил iptables**
   - Настроить MSS-коррекцию:
     ```bash
     sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
     ```
   - Включить NAT:
     ```bash
     sudo iptables -t nat -I POSTROUTING -j MASQUERADE
     ```
   - Сохранить правила:
     ```bash
     sudo netfilter-persistent save
     sudo netfilter-persistent reload
     ```

5. **Автоматизация с помощью Netplan**
   - Создать файл конфигурации:
     ```bash
     sudo nano /etc/netplan/99-ipip-tunnel.yaml
     ```
   - Добавить следующую конфигурацию:
     ```yaml
     network:
       version: 2
       renderer: networkd
       tunnels:
         ipip-tunnel:
           mode: ipip
           local: 10.0.0.2
           remote: 192.168.1.254
           addresses:
             - 10.0.1.1/24
           routes:
             - to: 192.168.1.0/24
               via: 10.0.1.2
             - to: 10.11.0.0/24
               via: 10.0.1.2
     ```
   - Применить настройки:
     ```bash
     sudo chmod 600 /etc/netplan/*.yaml
     sudo netplan apply
     ```

---

#### **На стороне FortiGate**

1. **Создание IPIP-туннеля**
   ```plaintext
   config system interface
       edit "IPIP-Tunnel"
           set vdom "root"
           set ip 10.0.1.2 255.255.255.255
           set allowaccess ping
           set type tunnel
           set remote-ip 10.0.1.1 255.255.255.0
           set description "IPIP"
           set alias "IPIP"
           set snmp-index 20
           set interface "internal"
       next
   end
   ```

2. **Настройка маршрутов**
   - Добавить маршрут к удаленной сети через туннель:
     ```plaintext
      config router static
          edit 222
              set dst 8.8.4.4 255.255.255.255
              set device "IPIP-Tunnel"
              set comment "Route to remote network via IPIP tunnel"
          next
          edit 111
              set distance 5
              set priority 40
              set device "IPIP-Tunnel"
              set comment "Route to remote network via IPIP tunnel"
          next
          edit 666
              set distance 5
              set priority 30
              set device "wan1"
              set comment "[ DEFAULT GW ]"
              set dynamic-gateway enable
          next
      end
     ```

3. **Создание объектов для адресов**
   ```plaintext
   config firewall address
       edit "192.168.1.0/24"
           set subnet 192.168.1.0 255.255.255.0
       next
       edit "10.11.0.0/24"
           set subnet 10.11.0.0 255.255.255.0
       next
       edit "8.8.4.4/32"
           set subnet 8.8.4.4 255.255.255.255
       next
   end
   ```

4. **Настройка политик межсетевого экрана**
   - Разрешить трафик между локальной сетью и удаленной:
     ```plaintext
     config firewall policy
         edit 1
             set name "LAN to Remote"
             set srcintf "internal"
             set dstintf "IPIP-Tunnel"
             set action accept
             set srcaddr "192.168.1.0/24" "10.11.0.0/24"
             set dstaddr "8.8.4.4/32"
             set schedule "always"
             set service "ALL"
             set comments "Local LAN to remote LAN via IPIP tunnel"
         next
         edit 2
             set name "Remote to LAN"
             set srcintf "IPIP-Tunnel"
             set dstintf "internal"
             set action accept
             set srcaddr "8.8.4.4/32"
             set dstaddr "192.168.1.0/24" "10.11.0.0/24"
             set schedule "always"
             set service "ALL"
             set comments "Remote LAN to local LAN via IPIP tunnel"
         next
     end
     ```

---

#### **Проверка настройки**

1. **На Ubuntu:**
   - Проверить туннель:
     ```bash
     ip tunnel show
     ip addr show ipip-tunnel
     ```
   - Проверить маршруты:
     ```bash
     ip route
     ```

2. **На FortiGate:**
   - Проверить туннель:
     ```plaintext
     diagnose ip ipip-tunnel list
     ```
   - Проверить маршруты:
     ```plaintext
     get router info routing-table all
     ```

3. **Тест соединения:**
   - Пинг с Ubuntu на FortiGate:
     ```bash
     ping 192.168.1.254
     ```
   - Пинг с FortiGate на Ubuntu:
     ```plaintext
     execute ping 10.0.0.2
     ```

---

Этот план гарантирует корректную настройку IPIP-туннеля между Ubuntu и FortiGate с учетом маршрутизации и межсетевых политик.
