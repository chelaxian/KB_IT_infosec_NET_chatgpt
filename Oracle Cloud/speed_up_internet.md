Bandwidth - 10 TB egress per month, speed limited to 50 Mbps on x64-based VM, 1000 Mbps * core count on ARM-based VM

### to speed up amd x64 VM:
redirect all AMD-internet traffic via proxy on ARM

#### on ARM:
```bash
apt update
apt install squid -y

nano /etc/squid/squid.conf
```

add this lines on top
```bash
acl allowed_ip src 10.0.0.0/24
http_access allow allowed_ip
http_port 10.0.0.XXX:3128 #change XXX to ARM IP
```

```bash
systemctl restart squid
systemctl enable squid
```

#### on AMD:

```bash
#change XXX to ARM IP
export http_proxy="http://10.0.0.XXX:3128" 
export https_proxy="http://10.0.0.XXX:3128" 
```

```bash
#change XXX to ARM IP
echo 'export http_proxy="http://10.0.0.XXX:3128"' >> ~/.bashrc 
echo 'export https_proxy="http://10.0.0.XXX:3128"' >> ~/.bashrc 
```

### before
```bash
Testing download speed...............................................................................
.Download: 49.93 Mbit/s
Testing upload speed......................................................................................................
Upload: 51.32 Mbit/s
```
### after
```bash
Testing download speed................................................................................
Download: 524.90 Mbit/s
Testing upload speed......................................................................................................
Upload: 407.87 Mbit/s
```