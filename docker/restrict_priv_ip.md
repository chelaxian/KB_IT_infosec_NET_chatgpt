## 1. везде запретить на смежных ВМ доступ

```bash
iptables -I INPUT -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 
iptables -I INPUT -s 10.8.0.0/23 -d 172.16.0.0/12 -j DROP 
iptables -I INPUT -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 

iptables -I FORWARD -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 
iptables -I FORWARD -s 10.8.0.0/23 -d 172.16.0.0/12 -j DROP 
iptables -I FORWARD -s 10.8.0.0/23 -d 10.0.0.0/8 -j DROP 

iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 10.0.0.0/8 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 172.16.0.0/12 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 192.168.0.0/16 -j RETURN 

iptables -L -v -n
iptables -t nat -L -v -n

mkdir -p /etc/iptables/
iptables-save > /etc/iptables/rules.v4
```
`apt-get update && apt-get install -y iptables-persistent`

## 2. так же запретить доступ внутри контейнера
`docker exec -it amnezia-wireguard sh` \
`docker exec -it amnezia-openvpn sh` \
`docker exec -it amnezia-awg sh ` \
`#docker exec -it amnezia-wg-easy sh` \
`#docker exec -it wg-easy sh`

```bash
iptables -I INPUT -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 
iptables -I INPUT -s 10.8.0.0/23 -d 172.16.0.0/12 -j DROP 
iptables -I INPUT -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 

iptables -I FORWARD -s 10.8.0.0/23 -d 192.168.0.0/16 -j DROP 
iptables -I FORWARD -s 10.8.0.0/23 -d 172.16.0.0/12 -j DROP 
iptables -I FORWARD -s 10.8.0.0/23 -d 10.0.0.0/8 -j DROP 

iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 10.0.0.0/8 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 172.16.0.0/12 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.0.0/23 -d 192.168.0.0/16 -j RETURN 

iptables -L -v -n
iptables -t nat -L -v -n

iptables-save > /etc/iptables/rules.v4
```

далее создать скрипт

```bash
mkdir -p /etc/local.d
cat > /etc/local.d/iptables.start <<EOF
#!/bin/sh
iptables-restore < /etc/iptables/rules.v4
EOF
chmod +x /etc/local.d/iptables.start
```

## 3. на docker-хосте создать скрипт

`sudo nano /etc/systemd/system/amnezia-no-private.service`

```service
[Unit]
Description=Amnezia WireGuard Docker Container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/docker exec amnezia-wireguard sh -c "/etc/local.d/iptables.start"

[Install]
WantedBy=multi-user.target
```

<details><summary>если контейнеров несколько то можно так:</summary>
  
```service
[Unit]
Description=Amnezia WireGuard Docker Container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/docker exec amnezia-wireguard sh -c "/etc/local.d/iptables.start"
ExecStartPost=/usr/bin/docker exec amnezia-openvpn sh -c "/etc/local.d/iptables.start"
ExecStartPost=/usr/bin/docker exec amnezia-awg sh -c "/etc/local.d/iptables.start"
#ExecStartPost=/usr/bin/docker exec amnezia-wg-easy sh -c "/etc/local.d/iptables.start"
#ExecStartPost=/usr/bin/docker exec wg-easy sh -c "/etc/local.d/iptables.start"

[Install]
WantedBy=multi-user.target
```
</details>
    
```
sudo systemctl daemon-reload
sudo systemctl start amnezia-no-private.service
sudo systemctl enable amnezia-no-private.service
sudo systemctl status amnezia-no-private.service
```

## 4. reboot docker-хоста и проверка

`reboot`

```bash
docker exec amnezia-wireguard iptables -L -n -v
docker exec amnezia-wireguard iptables -t nat -L -n -v
```

```bash
docker exec amnezia-awg iptables -L -n -v
docker exec amnezia-awg iptables -t nat -L -n -v
```

```bash
docker exec amnezia-openvpn iptables -L -n -v
docker exec amnezia-openvpn iptables -t nat -L -n -v
```

```bash
#docker exec amnezia-wg-easy iptables -L -n -v
#docker exec amnezia-wg-easy iptables -t nat -L -n -v
```
## 5. исключения в контейнере

пример:

```bash
iptables -I INPUT -p udp -m multiport --dports 53,5353 -j ACCEPT
iptables -I FORWARD -p udp -m multiport --dports 53,5353 -j ACCEPT

iptables -I INPUT -p tcp --dport 53 -j ACCEPT
iptables -I FORWARD -p tcp --dport 53 -j ACCEPT

iptables -t nat -I POSTROUTING -p udp -m multiport --dports 53,5353 -j MASQUERADE 
iptables -t nat -I POSTROUTING -p tcp -m multiport --dports 53 -j MASQUERADE 

iptables -L -v -n
iptables -t nat -L -v -n

iptables-save > /etc/iptables/rules.v4
```

## 6. редирект DNS на хосте

```bash
#iptables -t nat -A PREROUTING -d 1.1.1.0/30 -p udp -m udp --dport 53 -j DNAT --to-destination 77.88.8.8:53
```
