https://github.com/go-gost/gost \
https://habr.com/ru/articles/777656/

## on server (linux)
download and install
```bash
bash <(curl -fsSL https://github.com/go-gost/gost/raw/master/install.sh) --install
```
manual run 
```bash
gost -L relay://username:password@:56789
```
<details><summary>autostart</summary> 
  
```bash
mkdir -p /root/gost/
nano /root/gost/start_gost_proxies.sh
```
fill in `start_gost_proxies.sh`
```bash
#!/bin/bash
gost -L relay://username:password@:56789
```
```bash
chmod 777 /root/gost/start_gost_proxies.sh
sudo nano /etc/systemd/system/gost.service
```
fill in `gost.service`
```
[Unit]
Description=GOST Proxy Service
After=network.target

[Service]
Type=simple
ExecStart=/root/gost/start_gost_proxies.sh
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable gost.service
sudo systemctl start gost.service
```
check
```
sudo systemctl status gost.service
```
```
ss -tulpn | grep 56789
```
or
```
netstat -tulpn | grep 56789
```
</details>

---

<details><summary>autostart</summary> 
  
place gost.exe in root of C:/
```powershell
$Action = New-ScheduledTaskAction -Execute "C:\gost.exe" -Argument "-L http://:8080 -L socks5://:1080 -F relay://username:password@your.server.net:56789"
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest
$TaskName = "GostAutoStart"

Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -TaskName $TaskName
```
check
```cmd
tasklist | findstr gost.exe
netstat -an | findstr :8080
netstat -an | findstr :1080
```

## on client (windows)
download and extract \
https://github.com/go-gost/gost/releases/latest \
https://github.com/go-gost/gost/releases/download/v3.0.0-nightly.20241002/gost_3.0.0-nightly.20241002_windows_amd64.zip

manual run
```cmd
gost.exe -L http://:8080 -L socks5://:1080 -F relay://username:password@your.server.net:56789
```

Для открытия **Планировщика задач** и настроек **Автозагрузки** в Windows можно использовать следующие команды:

1. **Открытие Планировщика задач**:
   - Нажмите `Win + R` для открытия окна "Выполнить".
   - Введите команду:
     ```cmd
     taskschd.msc
     ```
   - Нажмите `Enter`. Откроется Планировщик задач.

2. **Открытие вкладки "Автозагрузка" в Диспетчере задач**:
   - Нажмите сочетание клавиш `Ctrl + Shift + Esc`, чтобы открыть Диспетчер задач.
   - Перейдите на вкладку **Автозагрузка**.

Если вам нужно запустить автостарта через "Выполнить":
- Нажмите `Win + R` и введите:
  ```cmd
  shell:startup
  ```
  Это откроет папку автозагрузки для текущего пользователя.

Для всех пользователей:
```cmd
shell:common startup
```

</details>

---

install chrome extension [Proxy SwitchyOmega 3 (ZeroOmega)](https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/pfnededegaaopdmhkdmcofjmoldfiped) and connect to 

#### http - `127.0.0.1:8080` 
or 
#### socks5 - `127.0.0.1:1080`

check IP on https://ipleak.net/
