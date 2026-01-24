## Полная инструкция: Dante SOCKS5 proxy на Debian/Ubuntu (arm64 bookworm)

Выполняйте от root. Логин: `proxyuser`, пароль: `***`.

### 1. Установка
```
apt update
apt install -y dante-server
systemctl stop danted || true
systemctl disable danted || true
```

### 2. Пользователь (сгенерируйте свой хэш: `openssl passwd -6 'ваш_пароль'`)
```
userdel -r proxyuser || true
useradd -r -s /usr/sbin/nologin proxyuser
usermod -p '[ВАШ_ХЭШ_SHA512]' proxyuser  # openssl passwd -6 ***
```

### 3. Конфиг `/etc/danted.conf` (external: `ip -4 a`)
```
tee /etc/danted.conf >/dev/null << 'EOF'
logoutput: /var/log/danted.log

internal: 0.0.0.0 port = 5555
external: enp0s3  # Замените!

socksmethod: username
clientmethod: none

user.privileged: root
user.unprivileged: nobody
user.libwrap: nobody

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    socksmethod: username
    log: connect disconnect error
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
    socksmethod: username
    log: connect disconnect error
}
EOF
```

### 4. Systemd `/etc/systemd/system/danted.service`
```
tee /etc/systemd/system/danted.service >/dev/null << 'EOF'
[Unit]
Description=Dante SOCKS5 proxy
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/danted -f /etc/danted.conf -D
PIDFile=/var/run/danted.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now danted
```

### 5. Firewall
```
ufw allow 5555/tcp || true
ufw reload || true
```

### 6. Проверка
```
systemctl status danted
ss -tuln | grep 5555
tail /var/log/danted.log
curl -v -x 'socks5://proxyuser:***@127.0.0.1:5555' http://ipinfo.io/ip
```
**Прокси готов:** `socks5://proxyuser:***@IP:5555` [community.hetzner](https://community.hetzner.com/tutorials/install-and-configure-danted-proxy-socks5/)
