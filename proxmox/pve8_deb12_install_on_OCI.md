https://frank-ruan.com/2023/03/18/installing-proxmox-ve-on-oci/ \
https://frank-ruan.com/2023/06/24/configuring-network-for-proxmox-ve-on-oci-arm/

First, log in to your Oracle Cloud console and jump right to the `Instances` page. Create an Ampere instance.
![image](https://github.com/user-attachments/assets/81901937-83dc-411a-a106-46035069dc74)
The OS doesn`t matter, we will replace it later.

Next, set up your firewall to let all traffic go to the virtual machine.

Go to `Console Connection`, and Click `Launch Cloud Shell Connection`.

A Cloud Shell session would appear. Don`t do anything yet.
![image](https://github.com/user-attachments/assets/8d5edb75-cb16-48d1-95fa-b1efed76ac59)

SSH to the machine, and download the EFI files we need.

```bash
sudo -i
cd /boot/efi
wget https://boot.netboot.xyz/ipxe/netboot.xyz-arm64.efi
```
![image](https://github.com/user-attachments/assets/86d75c8d-1bb6-433d-a364-0281fd3e42a4)

After that, disconnect from the machine. And go back to the OCI console.

Click `Reboot` on the top of the detail page. And check `Force reboot the instance by immediately powering off, then powering back on`.

Now pay attention, once the machine starts to reboot, focus on the Cloud Shell page, and smash your ESC button. Until you enter a BIOS-like page like below. \
![image](https://github.com/user-attachments/assets/f6997145-1f7c-4b74-8968-804f61c97936) \
Control the page with your arrow keys. Navigate to `Boot Maintenance Manager` -> `Boot From File` -> Choose your only hard disk -> `netboot.xyz-arm64.efi`.

Then you will enter the iPXE interface which netboot offers.

![image](https://github.com/user-attachments/assets/14eb000a-4f75-4912-b583-103924c93a83)

Navigate to `Linux Network Installs` -> `Debian` -> `Debian 11.0 (bullseye)` -> `Text Based Install`

And you will enter the normal Debian netinst page.

Now please point a domain to your machine. So if your domain is pve.contoso.com and your IP is 1.1.1.1, you should add an A record.

Use `pve` as your hostname, and `pve.contoso.com` as your domain in this case.

Then finallize your Debian installation as usual.

When you are setting up the partitioner, select `Guided - use entire disk and set up LVM` instead of the default one. Proxmox prefers LVM.

![image](https://github.com/user-attachments/assets/ba40e7cd-d708-4121-89b4-bdf59830514c)

Leave everything default for the rest of the installation.

![image](https://github.com/user-attachments/assets/cdc383f4-0052-4221-9317-d35628f6809c)

![image](https://github.com/user-attachments/assets/8200f7fc-07b4-4e2b-b50c-1586c06c9cfe)

After finishing the Debian installation, log in to your machine in the Cloud Shell use the root user and put your SSH key in ~/.ssh

By default, OpenSSH Server doesn`t allow users to SSH to the machine using the root user with a password. However, you can do it as long as you have an SSH key.

OpenSSH would ask you to delete the host key since we have changed our OS. Don`t be frightened by them.

After SSH to the machine, install some useful software.

```bash
apt install sudo wget curl iftop vnstat neofetch vim nano net-tools
```

Check your IP using the following command.
```bash
ip address
```
In my case, it is 10.0.117.132.

Use your favorite editor to open /etc/network/interfaces. The default one looks like this.

```bash
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enp0s3
iface enp0s3 inet dhcp
```
Change to the following:
```bash
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enp0s3
# iface enp0s3 inet dhcp
# Define Static IP
iface enp0s3 inet static
	address 10.0.117.132
	netmask 255.255.0.0
	gateway 10.0.0.1
```
You should judge the netmask according to the CIDR. /16 usually means 255.255.0.0, /24 usually means 255.255.255.0, you can find converter on the Internet.

Now open /etc/hosts, delete all the content, and replace with the following.
```bash
127.0.0.1 localhost
PUBLIC_IP HOSTNAME.proxmox.com HOSTNAME
```
Replace the `PUBLIC_IP` with your machine`s public IP and `HOSTNAME` with your hostname. e.g. `1.1.1.1 pve.contoso.com pve`.

Now reboot your machine, please.

https://github.com/jiangcuo/Proxmox-Port/wiki/Install-Proxmox-VE-on-Debian-bookworm

Install Proxmox VE
Add the Proxmox VE repository:
```bash
echo 'deb [arch=arm64] https://mirrors.apqa.cn/proxmox/debian/pve bookworm port'>/etc/apt/sources.list.d/pveport.list
```
Add the Proxmox VE repository key:
```bash
curl -L https://mirrors.apqa.cn/proxmox/debian/pveport.gpg -o /etc/apt/trusted.gpg.d/pveport.gpg 
```
Update your repository and system by running:
```bash
apt update && apt full-upgrade
```
Install Proxmox VE packages
Install the ifupdown2 packages
```bash
apt install ifupdown2
```
Install the Proxmox VE packages
```bash
apt install proxmox-ve postfix open-iscsi
```
Configure packages which require user input on installation according to your needs (e.g. Samba asking about WINS/DHCP support). If you have a mail server in your network, you should configure postfix as a satellite system, your existing mail server will then be the relay host which will route the emails sent by the Proxmox server to their final recipient.

If you don't know what to enter here, choose local only and leave the system name as is.

Finally, you can connect to the admin web interface (https://youripaddress:8006).

After installation, we need to install some dependencies.

Execute the following command.
```bash
apt install autoconf-archive -y
apt build-dep apparmor
```

```bash
apt install git bison flex autoconf libtool swig gettext python3 python3-dev python3-pip -y
git clone https://gitlab.com/apparmor/apparmor.git
cd apparmor
export PYTHONPATH=$(realpath libraries/libapparmor/swig/python)
export PYTHON=/usr/bin/python3
export PYTHON_VERSION=3
export PYTHON_VERSIONS=python3
cd ./libraries/libapparmor
./autogen.sh
./configure --prefix=/usr --with-perl --with-python
make
make install
cd ../../binutils/
make
make install
cd ../parser/
make
make install
cd ../utils/
make
make install

reboot
```
Hooray!
You now have a fully functional Proxmox VE on OCI! Visit https://IP:8006 for more configurations.
