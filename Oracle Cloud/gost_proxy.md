### on server
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
check
```ss -tulpn | grep 56789```
or
```netstat -tulpn | grep 56789```
</details>

### on client
manual run
```cmd
gost -L http://:8080 -L socks5://:1080 -F relay://username:password@your.server.net:56789
```
<details><summary>autostart</summary> 
  
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
</details>

install chrome extension [Proxy SwitchyOmega 3 (ZeroOmega)](https://chromewebstore.google.com/detail/proxy-switchyomega-3-zero/pfnededegaaopdmhkdmcofjmoldfiped) and connect to 

http - `127.0.0.1:8080` \
or \
Socks5 - `127.0.0.1:1080`

check IP on https://ipleak.net/
