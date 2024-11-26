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
In my case, it is 10.0.0.132.

Use your favorite editor to open /etc/network/interfaces. The default one looks like this.

```bash
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
allow-hotplug enp0s6
iface enp0s6 inet dhcp
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
allow-hotplug enp0s6
# iface enp0s6 inet dhcp
# Define Static IP
iface enp0s6 inet static
	address 10.0.0.132
	netmask 255.255.255.0
	gateway 10.0.0.1
```
You should judge the netmask according to the CIDR. /16 usually means `255.255.0.0`, /24 usually means `255.255.255.0`, you can find converter on the Internet.

---

Add an `/etc/hosts` entry for your IP address
Please make sure that your machine's hostname is resolvable via `/etc/hosts`, i.e. you need an entry in `/etc/hosts` which assigns an address to its hostname.

Make sure that you have configured one of the following addresses in `/etc/hosts` for your hostname:
```
1 IPv4 or
1 IPv6 or
1 IPv4 and 1 IPv6
Note: This also means removing the address 127.0.1.1 that might be present as default.
```
For instance, if your IP address is `192.168.15.77`, and your hostname prox4m1, then your `/etc/hosts` file could look like:
```bash
127.0.0.1       localhost.localdomain localhost
192.168.15.77   prox4m1.proxmox.com prox4m1

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```
You can test if your setup is ok using the hostname command:
```bash
hostname --ip-address
192.168.15.77 # should return your IP address here
```
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

---

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

Now log in to your PVE console, we are going to configure the bridge.

Go to Shell and open /etc/network/interfaces and add the following lines.
```bash
auto vmbr0
iface vmbr0 inet static
        address 10.200.0.1/24
        bridge_ports none
        bridge_stp off
        bridge_fd 0
        post-up echo 1 > /proc/sys/net/ipv4/ip_forward
        post-up iptables -t nat -A POSTROUTING -s '10.200.0.0/24' -o enp0s6 -j MASQUERADE
        post-down iptables -t nat -D POSTROUTING -s '10.200.0.0/24' -o enp0s6 -j MASQUERADE
```
This will create a /24 LAN CIDR, `10.200.0.0/24`, and we asked iptables to forward all traffic to our default network interface, `enp0s6`.

Use systemctl restart networking to restart the networking service.

Go back to the PVE console, and create a container. (Don’t forget to download the CT template first.)

It is suggested to download the template from here: https://uk.lxd.images.canonical.com/images/
