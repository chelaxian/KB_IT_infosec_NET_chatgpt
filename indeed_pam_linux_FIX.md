### Fix Docker Bench for Security
IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark/local.docker.log

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
mkdir /etc/sysconfig
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
sudo systemctl restart docker
```

### Fix permissons (danger!)

```
mkdir /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
mkdir /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
mkdir /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs
mkdir /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/cis-benchmark
mkdir /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state/selfsigned

sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/temp
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/backups
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/logs/
sudo chmod 777 -R /home/$(whoami)/IndeedPAM_2.10.1_RU/indeed-pam-linux/state
```
