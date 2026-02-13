```bash
#!/bin/bash
# Генерация self-signed CA + RDS server cert (RSA) + PFX, пароль: 1

set -euo pipefail

CN="rds.indeed.step"
PASS="1"
WORKDIR="/tmp/rds-cert"
DAYS_CA=3650
DAYS_SRV=825   # можно 3650, но 825 чаще “без сюрпризов” в Windows политиках

mkdir -p "$WORKDIR"
cd "$WORKDIR"

# 1) Root CA (с правильными CA extensions)
cat > ca.conf <<'EOF'
[ req ]
prompt = no
distinguished_name = dn
x509_extensions = v3_ca

[ dn ]
C=RU
ST=Moscow
L=Moscow
O=STEP
OU=IT
CN=IndeedPAM CA

[ v3_ca ]
basicConstraints = critical, CA:TRUE
keyUsage = critical, keyCertSign, cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
EOF

openssl genrsa -out ca.key 4096
openssl req -new -x509 -key ca.key -out ca.crt -days "$DAYS_CA" -sha256 -config ca.conf

# 2) Server key
openssl genrsa -out rds.key 2048

# 3) CSR + server cert extensions (SAN + EKU под RDS)
cat > san.conf <<EOF
[ req ]
prompt = no
distinguished_name = dn
req_extensions = v3_req

[ dn ]
C=RU
ST=Moscow
L=Moscow
O=STEP
OU=IT
CN=${CN}

[ v3_req ]
basicConstraints = critical, CA:FALSE
keyUsage = critical, digitalSignature, keyEncipherment

# EKU: обычный serverAuth + Remote Desktop Authentication (OID)
extendedKeyUsage = serverAuth, 1.3.6.1.4.1.311.54.1.2

subjectAltName = @alt_names

[ alt_names ]
DNS.1 = ${CN}
DNS.2 = *.indeed.step
DNS.3 = indeed.step
DNS.4 = ad.indeed.step
DNS.5 = sql.indeed.step
DNS.6 = mgmt.indeed.step
DNS.7 = acs.indeed.step
DNS.8 = ha.indeed.step
EOF

openssl req -new -key rds.key -out rds.csr -sha256 -config san.conf

# Важно: копируем extensions из san.conf при подписи
openssl x509 -req \
  -in rds.csr \
  -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out rds.crt \
  -days "$DAYS_SRV" -sha256 \
  -extensions v3_req -extfile san.conf

# 4) PFX (включаем цепочку до CA)
openssl pkcs12 -export \
  -in rds.crt -inkey rds.key \
  -certfile ca.crt \
  -name "${CN}" \
  -out "${CN}.pfx" \
  -passout "pass:${PASS}"

# 5) Проверки
echo "=== SERVER CERT (SAN/EKU) ==="
openssl x509 -in rds.crt -text -noout | grep -A12 -E "Subject:|Issuer:|X509v3 Subject Alternative Name|X509v3 Extended Key Usage|X509v3 Key Usage|Basic Constraints"

echo "=== PFX CONTENTS ==="
openssl pkcs12 -in "${CN}.pfx" -info -noout -passin "pass:${PASS}"

echo "=== FILES ==="
ls -la

```
