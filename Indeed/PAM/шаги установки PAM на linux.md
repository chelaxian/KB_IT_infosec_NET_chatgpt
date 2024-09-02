### Install dependensies
```
sudo apt-get update && sudo apt-get install openssh-server nano htop zip unzip net-tools curl wget python3 python-is-python3 sudo iptables tcpdump -y
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
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v "/var/run/docker.sock:/var/run/docker.sock" -v "portainer_data:/data" portainer/portainer-ce:2.21.0
```

### Copy certs and configs to folders and start deploy
```
cd /home/$(whoami)/
unzip IndeedPAM_2.10.1_RU.zip
#cp ca.crt /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/ca-certificates/
#cp cert.pfx /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/certs/
cp vars.yml /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/scripts/ansible/
cp config.json /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/
cd /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/
```
```
sudo chmod 777 *.sh
sudo mkdir -p /mnt/storage
sudo chmod -R 777 /mnt/storage
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

