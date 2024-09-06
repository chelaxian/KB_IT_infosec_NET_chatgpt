### Usefull links

[Развёртывание Indeed PAM 2.10, базовый курс.](https://edu.indeed-company.ru/mod/page/view.php?id=68) \
[Дистрибутив Indeed PAM](https://download.indeed-company.ru/s/q8zoOXIGhxhfR2q) \
[Документация Indeed PAM](https://docs.indeed-company.ru/privileged-access-manager/2.10/intro/) \
[База знаний](https://support.indeed-company.ru/Knowledgebase/List/Index/50/indeed-privileged-access-manager) 

### Install dependensies
```bash
sudo apt-get update && sudo apt-get install openssh-server nano htop zip unzip net-tools curl wget python3 python-is-python3 sudo iptables tcpdump ldap-utils -y
```
### Install docker
#### Debian
```bash
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

### Install portainer (not essential)
<details><summary>Install portainer</summary>
  
```bash
sudo docker volume create portainer_data
sudo touch /var/run/docker.sock
sudo chmod 777 /var/run/docker.sock
```
```bash
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v "/var/run/docker.sock:/var/run/docker.sock" -v "portainer_data:/data" portainer/portainer-ce:2.21.0
```
</details>
  
### Download Installer, Copy certs and configs to folders and start Deploy
Create `ca.crt`, `cert.pfx`, Edit and Prepare `vars.yml`, `config.json` and place them into `~home` directory
```bash
cd ~
```
```bash
wget -O IndeedPAM_2.10.1_RU.zip \
"https://download.indeed-company.ru/s/q8zoOXIGhxhfR2q/download"
```
or
```bash
curl -L -o IndeedPAM_2.10.1_RU.zip \
"https://download.indeed-company.ru/s/q8zoOXIGhxhfR2q/download"
```
```bash
unzip IndeedPAM_2.10.1_RU.zip
cp ca.crt ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/ca-certificates/
cp cert.pfx ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/certs/
cp vars.yml ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/scripts/ansible/
cp config.json ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/
cd ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/
```
```bash
sudo chmod 777 *.sh
sudo bash run-deploy.sh --bench-skip -vvv
```
<details><summary>Spoiler (If you want to pass Benchmark without skipping)</summary>

### Fix Docker Bench for Security

```bash
IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark/local.docker.log
```
  
```bash
sudo -i
```

```bash
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

```bash
echo '[plugins."io.containerd.grpc.v1.cri".containerd]
  snapshotter = "overlayfs"
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2"
' > /etc/containerd/config.toml

chown root:root /etc/containerd/config.toml
chmod 644 /etc/containerd/config.toml
```

```bash
echo 'DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"' > /etc/default/docker

chown root:root /etc/default/docker
chmod 644 /etc/default/docker
```

```bash
mkdir -p /etc/sysconfig
echo '# /etc/sysconfig/docker
DOCKER_STORAGE_OPTIONS="--storage-driver=overlay2"
DOCKER_NETWORK_OPTIONS="--bip=172.17.0.1/16"
' > /etc/sysconfig/docker

chown root:root /etc/sysconfig/docker
chmod 644 /etc/sysconfig/docker
```

```bash
mkdir -p /etc/docker/certs.d
openssl req -newkey rsa:4096 -nodes -keyout /etc/docker/certs.d/server-key.pem -x509 -days 365 -out /etc/docker/certs.d/server-cert.pem -subj "/CN=localhost"
chown root:root /etc/docker/certs.d/server-key.pem /etc/docker/certs.d/server-cert.pem
chmod 400 /etc/docker/certs.d/server-key.pem
chmod 444 /etc/docker/certs.d/server-cert.pem
```
```bash
sudo apt-get install containerd runc -y
sudo autoremove
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```
```bash
sudo systemctl restart docker
exit
```
### Run Deploing script
```bash
sudo bash run-deploy.sh -vvv
```
</details>

<details><summary>Spoiler (If you have problems with permissions while Deploying)</summary>
  
### Fix permissons
```bash
sudo mkdir -p ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
sudo mkdir -p ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
sudo mkdir -p ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs
sudo mkdir -p ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark
sudo mkdir -p ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/selfsigned

sudo chmod 777 -R ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
sudo chmod 777 -R ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
sudo chmod 777 -R ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/
sudo chmod 777 -R ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/state
```
</details>

### Warnings

On Debian 12 you will have visual bug - Docker Containers may look like `Unhealthy` while fully Healthy and Running.
You may ignore that.
<details><summary>Screenshot</summary>
  <img width="875" alt="image" src="https://github.com/user-attachments/assets/16cec3c1-7745-40d4-a002-63b769d8577f">
</details>

### Generate Self-Signed certificate and change default one
```bash
openssl genrsa -out pam-ca.key 2048
openssl req -x509 -new -nodes -key pam-ca.key -subj "/CN=indeed-pam" -days 10000 -out pam-ca.crt
openssl genrsa -out pam.key 2048
nano server.conf
```
<details><summary>server.conf</summary>
  
```conf
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

```bash
openssl req -new -key pam.key -out server.csr -config server.conf
openssl x509 -req -in server.csr -CA pam-ca.crt -CAkey pam-ca.key -CAcreateserial -out pam.crt -days 10000 -extensions v3_ext -extfile server.conf
cp pam-ca.crt /etc/indeed/indeed-pam/ca-certificates/
cp pam.crt /etc/indeed/indeed-pam/certs/pam.crt
cp pam.key /etc/indeed/indeed-pam/certs/pam.key
```

### Add LDAPS root CA + intermediate CA and check connection
```bash
cp ca1.cer /etc/indeed/indeed-pam/ca-certificates/ca1.crt #base64 (root CA)
cp ca2.cer /etc/indeed/indeed-pam/ca-certificates/ca2.crt #base64 (intermediate CA)
cat ca1.crt ca2.crt > /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
```
check with CURL ldaps connection
```bash
curl ldaps://dc1.domain.net --cacert /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
curl ldaps://domain.net --cacert /etc/indeed/indeed-pam/ca-certificates/ca-pem.crt
```
Curl should work both for DC and for DOMAIN. If curl for DOMAIN not work - you should create new Kerberos cert for LDAPS of your AD with 
```conf
[ alt_names ]
DNS.1 = dc.domain.com
DNS.2 = domain.com
```
### Change settings from LDAP to LDAPS
```bash
 nano /etc/indeed/indeed-pam/core/appsettings.json
 nano /etc/indeed/indeed-pam/idp/appsettings.json
```
<details><summary>appsettings.json</summary>

```diff
"Id": "ad",
"ConnectorType": "Ldap",
"LdapServerType": "ActiveDirectory",
"Domain": "domain.net",
-"Port": 389,
+"Port": 689,
"AuthType": "Basic",
-"SecureSocketLayer": false,
+"SecureSocketLayer": true,

```

</details>

### Commands to STOP / START / SET permissions after CHANGES in CONFIGS
```bash
bash /etc/indeed/indeed-pam/scripts/stop-pam.sh
bash /etc/indeed/indeed-pam/scripts/set-permissions.sh
bash /etc/indeed/indeed-pam/scripts/run-pam.sh
```

### Add /etc/hosts entry to docker containers (if needed)
nano /etc/indeed/indeed-pam/docker-compose.management-server.yml
```diff
  core:
    [...]
+    extra_hosts:
+      - "domain.net:10.x.x.x"

  idp:
    [...]
+    extra_hosts:
+      - "domain.net:10.x.x.x"
```

### Check LOGS to MONITOR and FIX ERRORS
```bash
 cd /etc/indeed/indeed-pam/logs/
 cat /etc/indeed/indeed-pam/logs/idp/errors.log
```

### Run Indeed-Wizard docker on same VM/server

0. stop PAM ant try to run wizard
```bash
sudo bash /etc/indeed/indeed-pam/scripts/stop-pam.sh
sudo bash ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/run-wizard.sh
```
1. if it not helps - rename docker container `pam-ca-certificates` to `pam-ca-certificates1`

2. ```nano ~/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/docker-compose.web-wizard.yml```

```diff
    ports:
-      - "${HOST_IP}:80:8090"
-      - "${HOST_IP}:443:5443"
+      - "${HOST_IP}:8080:8090"
+      - "${HOST_IP}:8443:5443"
```
```diff
networks:
  default:
    name: pam-default-network
+    external: true
  web-wizard-api-network:
    name: pam-web-wizard-api-network
    driver: bridge

volumes:
  pam-ca-cert-store:
    name: pam-ca-cert-store
+    external: true
```
```bash
sudo ./run-wizard.sh -vvv
```
### Add RDS Windows Server (RemoteApp) to Linux PAM

```bash
 sudo bash /etc/indeed/indeed-pam/tools/protector.sh unprotect
```
Copy `"GatewaySecret": "XxXXXXXXXXxXXXXXXXXxXXXXXXXXXXXXXXxXxXXxXxx=",` string to
`C:\Program Files\Indeed\Indeed PAM\Gateway\ProxyApp\appsettings.json` on Windows RDS server
fill in Core and Auth(IDP) sections
<details><summary>appsettings.json</summary>
  
```json
{
  "Core": {
    "Url": "https://pam.domain.net/core",
    "RequestTimeout": "00:01:00"
  },
  "Auth": {
    "IdpUrl": "https://pam.domain.net/idp",
    "IdpRequiresHttps": true,
    "GatewaySecret": "XxXXXXXXXXxXXXXXXXXxXXXXXXXXXXXXXXxXxXXxXxx="
  },
```
</details>

Copy `"GatewaySecret": "XxXXXXXXXXxXXXXXXXXxXXXXXXXXXXXXXXxXxXXxXxx=",` string to
`C:\Program Files\Indeed\Indeed PAM\Gateway\Pam.Gateway.Service\appsettings.json` on Windows RDS server
fill in Core and Auth(IDP) sections
<details><summary>appsettings.json</summary>
  
```json
{
  "Core": {
    "Url": "https://pam.domain.net/core",
    "RequestTimeout": "00:01:00"
  },
  "Auth": {
    "IdpUrl": "https://pam.domain.net/idp",
    "IdpRequiresHttps": true,
    "GatewaySecret": "XxXXXXXXXXxXXXXXXXXxXXXXXXXXXXXXXXxXxXXxXxx="
  },
```
```json
  "GatewayService": {
    "Url": "https://win-rds.domain.net:5443/"
```
add this lines to the end of file and check json
```json
}    
}
  },
  "Kestrel": {
    "Endpoints": {
      "HttpsInlineCertStore": {
        "Url": "https://0.0.0.0:5443",
        "Certificate": {
          "Subject": "win-rds.domain.net",
          "Store": "My",
          "Location": "LocalMachine",
          "AllowInvalid": "False"
        }
      }
    }
  }
}
}
```
</details>

```bash
 nano /etc/indeed/indeed-pam/core/appsettings.json
 nano /etc/indeed/indeed-pam/gateway-service/appsettings.json
```

<details><summary>appsettings.json</summary>

```json
  "Storage": {
    "Type": "SMB",
    "Settings": {
      "Root": "\\\\IP.IP.IP.IP\\IPAMStorage",
      "Domain": "FULL.DOMAIN.NAME",
      "Login": "USER",
      "Password": "PASSWORD"
```
```bash
bash /etc/indeed/indeed-pam/scripts/stop-pam.sh
bash /etc/indeed/indeed-pam/scripts/set-permissions.sh
bash /etc/indeed/indeed-pam/scripts/run-pam.sh
```
</details>

