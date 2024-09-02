### Usefull links

[Развёртывание Indeed PAM 2.10, базовый курс.](https://edu.indeed-company.ru/mod/page/view.php?id=68) \
[Дистрибутив Indeed PAM](https://download.indeed-company.ru/s/q8zoOXIGhxhfR2q) \
[Документация Indeed PAM](https://docs.indeed-company.ru/privileged-access-manager/2.10/intro/) \
[База знаний](https://support.indeed-company.ru/Knowledgebase/List/Index/50/indeed-privileged-access-manager) 

### Install dependensies
```
sudo apt-get update && sudo apt-get install openssh-server nano htop zip unzip net-tools curl wget python3 python-is-python3 sudo iptables tcpdump ldap-utils -y
```
### Install docker
#### Debian
```
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```
#### Other's distro
https://docs.docker.com/engine/install/

### Install portainer
```
sudo docker volume create portainer_data
sudo touch /var/run/docker.sock
sudo chmod 777 /var/run/docker.sock
```
```
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v "/var/run/docker.sock:/var/run/docker.sock" -v "portainer_data:/data" portainer/portainer-ce:2.21.0
```

### Copy certs and configs to folders and start deploy
```
cd /home/$(whoami)/
unzip IndeedPAM_2.10.1_RU.zip
cp ca.crt /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/ca-certificates/
cp cert.pfx /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/certs/
#cp vars.yml /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/scripts/ansible/
#cp config.json /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/
cd /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/
```
```
sudo chmod 777 *.sh
sudo bash run-deploy.sh --bench-skip -vvv
```
<details><summary>Spoiler (If you want to pass Benchmark without skipping)</summary>

### Fix Docker Bench for Security

```bash
IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark/local.docker.log
```
  
```
sudo -i
```

```
echo '{
  "debug": true,
  "log-level": "info",
  "storage-driver": "overlay2",
  "bip": "172.17.0.1/16",
  "iptables": true,
  "userns-remap": "default"
}' > /etc/docker/daemon.json

chown root:root /etc/docker/daemon.json
chmod 644 /etc/docker/daemon.json
```

```
echo '[plugins."io.containerd.grpc.v1.cri".containerd]
  snapshotter = "overlayfs"
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2"
' > /etc/containerd/config.toml

chown root:root /etc/containerd/config.toml
chmod 644 /etc/containerd/config.toml
```

```
echo 'DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"' > /etc/default/docker

chown root:root /etc/default/docker
chmod 644 /etc/default/docker
```

```
mkdir -p /etc/sysconfig
echo '# /etc/sysconfig/docker
DOCKER_STORAGE_OPTIONS="--storage-driver=overlay2"
DOCKER_NETWORK_OPTIONS="--bip=172.17.0.1/16"
' > /etc/sysconfig/docker

chown root:root /etc/sysconfig/docker
chmod 644 /etc/sysconfig/docker
```

```
mkdir -p /etc/docker/certs.d
openssl req -newkey rsa:4096 -nodes -keyout /etc/docker/certs.d/server-key.pem -x509 -days 365 -out /etc/docker/certs.d/server-cert.pem -subj "/CN=localhost"
chown root:root /etc/docker/certs.d/server-key.pem /etc/docker/certs.d/server-cert.pem
chmod 400 /etc/docker/certs.d/server-key.pem
chmod 444 /etc/docker/certs.d/server-cert.pem
```
```
sudo apt-get install containerd runc -y
sudo autoremove
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```
```
sudo systemctl restart docker
exit
```
### Run Deploing script
```
sudo bash run-deploy.sh -vvv
```
</details>

<details><summary>Spoiler (If you have problems with permissions while Deploying)</summary>
  
### Fix permissons
```
sudo mkdir -p /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
sudo mkdir -p /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
sudo mkdir -p /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs
sudo mkdir -p /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark
sudo mkdir -p /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/selfsigned

sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state
```
</details>

### Warnings

On Debian 12 you will have visual bug - Docker Containers may look like `Unhealthy` while fully Healthy and Running.
You may ignore that.
<details><summary>Screenshot</summary>
  <img width="875" alt="image" src="https://github.com/user-attachments/assets/16cec3c1-7745-40d4-a002-63b769d8577f">
</details>

### Generate Self-Signed certificate and change default one
```
openssl genrsa -out pam-ca.key 2048
openssl req -x509 -new -nodes -key pam-ca.key -subj "/CN=indeed-pam" -days 10000 -out pam-ca.crt
openssl genrsa -out pam.key 2048
nano server.conf
```
<details><summary>server.conf</summary>
  
```
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = RU
ST = Moscow
L = Moscow
O = Oblast
OU = PamUnit
CN = pam.domain.net

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = pam.domain.com
DNS.2 = domain.com

[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=nonRepudiation,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
</details>
```
</details>

```
openssl req -new -key pam.key -out server.csr -config server.conf
openssl x509 -req -in server.csr -CA pam-ca.crt -CAkey pam-ca.key -CAcreateserial -out pam.crt -days 10000 -extensions v3_ext -extfile server.conf
cp pam-ca.crt /etc/indeed/indeed-pam/ca-certificates/
cp pam.crt /etc/indeed/indeed-pam/certs/pam.crt
cp pam.key /etc/indeed/indeed-pam/certs/pam.key
```

### Add LDAPS root CA + intermediate CA and check connection
```
cp ca1.cer /etc/indeed/indeed-pam/ca-certificates/ca1.crt #base64 (root CA)
cp ca2.cer /etc/indeed/indeed-pam/ca-certificates/ca2.crt #base64 (intermediate CA)
cat ca1.crt ca2.crt > /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
```
check with CURL ldaps connection
```
curl ldaps://dc1.domain.net --cacert /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
curl ldaps://domain.net --cacert /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
```
Curl should work both for DC and for DOMAIN. If curl for DOMAIN not work - you should create new Kerberos cert for LDAPS of your AD with 
```
[ alt_names ]
DNS.1 = dc.domain.com
DNS.2 = domain.com
```
### Change settings from LDAP to LDAPS
```
 nano /etc/indeed/indeed-pam/core/appsettings.json
 nano /etc/indeed/indeed-pam/idp/appsettings.json
```
<details><summary>appsettings.json</summary>

```
          -"Id": "ad",
          -"ConnectorType": "Ldap",
          -"LdapServerType": "ActiveDirectory",
          -"Domain": "int.kronshtadt.ru",
          -"Port": 389,
          -"AuthType": "Basic",
          -"SecureSocketLayer": false,


          +"Id": "ad",
          +"ConnectorType": "Ldap",
          +"LdapServerType": "ActiveDirectory",
          +"Domain": "int.kronshtadt.ru",
          +"Port": 689,
          +"AuthType": "Basic",
          +"SecureSocketLayer": true,

```

</details>





### Commands to STOP / START / SET permissions after CHANGES in CONFIGS
```
bash /etc/indeed/indeed-pam/scripts/stop-pam.sh
bash /etc/indeed/indeed-pam/scripts/set-permissions.sh
bash /etc/indeed/indeed-pam/scripts/run-pam.sh
```

### Add /etc/hosts entry to docker containers (if needed)
nano /etc/indeed/indeed-pam/docker-compose.management-server.yml




