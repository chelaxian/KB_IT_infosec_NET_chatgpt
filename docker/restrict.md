## 1. везде запретить на смежных ВМ доступ

```bash
iptables -I INPUT -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 
iptables -I INPUT -s 10.8.1.0/24 -d 172.16.0.0/12 -j DROP 
iptables -I INPUT -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 

iptables -I FORWARD -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 
iptables -I FORWARD -s 10.8.1.0/24 -d 172.16.0.0/12 -j DROP 
iptables -I FORWARD -s 10.8.1.0/24 -d 10.0.0.0/8 -j DROP 

iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 10.0.0.0/8 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 172.16.0.0/12 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 192.168.0.0/16 -j RETURN 


iptables -L -v -n
iptables -t nat -L -v -n


iptables-save > /etc/iptables/rules.v4
```

## 2. так же запретить доступ внутри контейнера

```bash
iptables -I INPUT -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 
iptables -I INPUT -s 10.8.1.0/24 -d 172.16.0.0/12 -j DROP 
iptables -I INPUT -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 

iptables -I FORWARD -s 10.8.1.0/24 -d 192.168.0.0/16 -j DROP 
iptables -I FORWARD -s 10.8.1.0/24 -d 172.16.0.0/12 -j DROP 
iptables -I FORWARD -s 10.8.1.0/24 -d 10.0.0.0/8 -j DROP 

iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 10.0.0.0/8 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 172.16.0.0/12 -j RETURN 
iptables -t nat -I POSTROUTING -s 10.8.1.0/24 -d 192.168.0.0/16 -j RETURN 


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

`sudo nano /etc/systemd/system/amnezia-wireguard.service`

```service
[Unit]
Description=Amnezia WireGuard Docker Container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStartPre=/bin/sleep 5
#ExecStartPre=/usr/bin/docker start amnezia-wireguard
ExecStart=/usr/bin/docker exec amnezia-wireguard sh -c "/etc/local.d/iptables.start"
#ExecStop=/usr/bin/docker stop amnezia-wireguard

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl start amnezia-wireguard.service
sudo systemctl status amnezia-wireguard.service
```

## 4. reboot docker-хоста и проверка

`reboot`

```bash
docker exec amnezia-wireguard iptables -L -n -v
docker exec amnezia-wireguard iptables -t nat -L -n -v
```
