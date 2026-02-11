```
#!/bin/bash
# Полная генерация self-signed RDS cert с нуля в /tmp (пароль:1)

cd /tmp

# 1. Генерация CA key/cert (self-signed root)
openssl genrsa -out ca.key 4096
openssl req -new -x509 -key ca.key -out ca.crt -days 3650 -subj "/C=RU/ST=Moscow/L=Moscow/O=STEP/OU=IT/CN=IndeedPAM CA" -sha256

# 2. Server key
openssl genrsa -out rds.key 2048

# 3. SAN config
cat > san.conf << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=RU
ST=Moscow
L=Moscow
O=STEP
OU=IT
CN=rds.indeed.step

[v3_req]
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names

[alt_names]
DNS.1=*.indeed.step
DNS.2=indeed.step
DNS.3=rds.indeed.step
DNS.4=ad.indeed.step
DNS.5=sql.indeed.step
DNS.6=mgmt.indeed.step
DNS.7=acs.indeed.step
DNS.8=ha.indeed.step
EOF

# 4. CSR + sign
openssl req -new -key rds.key -out rds.csr -config san.conf -sha256
openssl x509 -req -in rds.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out rds.crt -days 3650 -sha256 -extensions v3_req -extfile san.conf

# 5. PFX
openssl pkcs12 -export -in rds.crt -inkey rds.key -out rds-rds.pfx -passout pass:1 -certfile ca.crt -name "rds.indeed.step"

# 6. Проверка
echo "=== CERT INFO ==="
openssl x509 -in rds.crt -text -noout | grep -A5 -E "(Subject Alternative Name|EKU|Subject:|Issuer:)"

echo "=== FILES ==="
ls -la *.key *.crt *.pfx *.csr

echo "=== COPY TO ANSIBLE ==="
cp rds-rds.pfx /home/step/IndeedPAM_3.3_RU/indeed-pam/workdir/target/certs/rds.indeed.step/rds.indeed.step.pfx

echo "ГОТОВО! ansible-playbook site.yml -e Clean=false"
```

```
# Твои файлы в /tmp (сгенерированные скриптом):
ls -la /tmp/*.pfx /tmp/*.key /tmp/*.crt /tmp/*.csr

# Собрать PFX (пароль:1) — уже готов rds-rds.pfx
# Проверь содержимое:
openssl pkcs12 -in /tmp/rds-rds.pfx -info -noout -passin pass:1

# Копировать ВСЕ нужные в Ansible (заменит старые):
cp /tmp/rds-rds.pfx /home/step/IndeedPAM_3.3_RU/indeed-pam/workdir/target/certs/rds.indeed.step/rds.indeed.step.pfx
cp /tmp/ca.crt /home/step/IndeedPAM_3.3_RU/indeed-pam/workdir/target/ca-certificates/ca.crt  # root CA

# Backup старого PFX:
mv /home/step/IndeedPAM_3.3_RU/indeed-pam/workdir/target/certs/rds.indeed.step/pam.pfx /home/step/IndeedPAM_3.3_RU/indeed-pam/workdir/target/certs/rds.indeed.step/pam.pfx.old

# Проверка SAN/EKU нового:
openssl x509 -in /tmp/rds.crt -text -noout | grep -A10 "Subject Alternative Name\|X509v3 Extended Key Usage"

# Запуск Ansible (без clean, чтобы не удалить MSI):
# cd /home/step/IndeedPAM_3.3_RU/indeed-pam
# ansible-playbook site.yml -e "Clean=false LogVerbose=3"

```
