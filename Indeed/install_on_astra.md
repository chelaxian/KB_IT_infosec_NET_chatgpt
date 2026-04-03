**dpkg конфликт docker-compose**. Исправьте + доп. пакеты.
**Исправленные команды для Astra Linux 1.8**
## 0. Fix dpkg (удалить старый compose)
```bash
sudo apt --fix-broken install -y
sudo dpkg --remove --force-remove-reinstreq docker-compose docker-compose-v2
sudo apt autoremove -y
sudo apt install -y docker-compose-v2
docker compose version
```

## 1. Базовые + сеть/диагностика
```bash
sudo apt update && sudo apt install -y \
  curl wget vim nano htop iotop-c net-tools iproute2 iptables-persistent \
  sysstat lsof strace tcpdump dnsutils nmap \
  jq tree unzip zip rsync git \
  openssh-server openssh-client \
  docker.io docker-compose-v2
```

## 2. Docker Compose v2 (если нет)
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker compose version
```

## 3. Базы + PAM
```bash
sudo apt install -y \
  libpam0g-dev libpam-modules \
  postgresql-client mariadb-client redis-tools \
  ldap-utils ldb-tools smbclient \
  apparmor-utils auditd rsyslog \
  apache2-utils #nginx \
  socat ncdu testssl.sh 
```

## 4. Python/Ansible (Astra pip)
```bash
sudo apt install -y python3-pip python3-venv python3-dev python3-cryptography
python3 -m venv venv
source venv/bin/activate
pip3 install --user --upgrade pip ansible yq pyOpenSSL cryptography
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
ansible --version
deactivate
```

## 5. Чек + очистка
```bash
ansible --version && docker compose version && pamtester --version || sudo apt install libpam-tester
sudo docker system prune -a -f
```

**Всё установлено!** `sudo bash run-wizard.sh -vvv` → https://10.x.x.x:9443. Готово к оффлайн-deploy PAM.





