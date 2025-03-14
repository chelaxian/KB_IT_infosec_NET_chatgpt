# TFTP Server Deployment and Testing Guide

This guide provides step-by-step instructions on setting up a TFTP server using `tftp-go`, verifying its operation, and downloading files from it.

---

## 1. Install and Build TFTP Server

### Prerequisites
Ensure your system has Git and Go installed. If not, install them using:

```bash
apt update && apt install -y golang git
```

### Clone and Build `tftp-go`

```bash
git clone https://github.com/lfkeitel/tftp-go
cd tftp-go/
go build
```

### Download the Boot File

```bash
wget https://boot.netboot.xyz/ipxe/netboot.xyz-arm64.efi
cp netboot.xyz-arm64.efi arm.efi
chmod 644 arm.efi
```

### Start TFTP Server

```bash
./tftp-go -server
```

The TFTP server will start serving files from the `/root/tftp-go` directory.

---

## 2. Verify TFTP Server Functionality

### Check if the TFTP Server is Running
Run:

```bash
ps aux | grep tftp
```

Ensure the process is active.

### Test Locally
From the server, try fetching the file using TFTP:

```bash
tftp 127.0.0.1
get arm.efi
```

If no errors appear, the server is working correctly.

---

## 3. Download File from Windows

Enable the TFTP client on Windows:

```powershell
dism /online /Enable-Feature /FeatureName:TFTP
```

Download the file using TFTP:

```powershell
tftp -i 123.123.123.123 GET arm.efi
```

Verify the file is downloaded successfully.

---

## 4. Download File in OCI (EFI Shell)

### Configure Network
In the EFI shell, assign IP addresses to interfaces:

```shell
Shell> fs0:
FS0:\> cd EFI
FS0:\EFI\> ifconfig -s eth0 static 10.0.0.111 255.255.255.0 10.0.0.1
FS0:\EFI\> ifconfig -s eth1 static 172.16.0.111 255.255.255.0 172.16.0.1
FS0:\EFI\> ifconfig -l eth0
FS0:\EFI\> ifconfig -l eth1
```

```copy-paste
fs0:
cd EFI
ifconfig -s eth0 static 10.0.0.111 255.255.255.0 10.0.0.1
ifconfig -s eth1 static 172.16.0.111 255.255.255.0 172.16.0.1
ifconfig -l eth0
ifconfig -l eth1
```

### Download File
```shell
FS0:\EFI\> ping 123.123.123.123
FS0:\EFI\> tftp 123.123.123.123 arm.efi
```

```copy-paste
ping 123.123.123.123
tftp 123.123.123.123 arm.efi
```

The file will be downloaded and can be used for booting or further processing.

---

## Conclusion
This guide covers:
- Setting up a TFTP server with `tftp-go`
- Verifying the server's functionality
- Downloading files from Windows
- Using TFTP in an EFI shell on OCI

Your TFTP server is now fully functional and ready for use!

