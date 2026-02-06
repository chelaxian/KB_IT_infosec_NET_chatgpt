# 🧯 RUNBOOK

## Восстановление PostgreSQL HA (etcd + Patroni + SSL)

### Унификация (везде ниже)

* IP (пример): `100.100.100.100`
* Cluster: `pg-ha-cluster`
* PostgreSQL: `16`
* DCS: `etcd v3`
* Patroni: systemd
* PostgreSQL user (superuser): `pgsqluser`
* Replication user: `repl`
* Пароль (везде): `PASSWORD`
* SSL: **обязателен, non-SSL запрещён**

---

## ❗ КРИТИЧЕСКИЙ КОНТЕКСТ (почему кластер не вставал)

Система была сломана **не PostgreSQL и не SSL**, а тем, что:

* etcd был жив
* Patroni был жив
* НО в etcd **остались stale-ключи Patroni**:

  * `leader`
  * `members/*`
  * `history`
  * `config`
* Patroni видел «существующий кластер»,
  но **не имел права выбрать лидера**

👉 **Пока эти ключи не удалены — лидер НЕ появится НИКОГДА**

---

# 0️⃣ ПРЕДПОСЫЛКИ

Перед началом:

* quorum etcd есть
* либо данные не нужны, либо есть хотя бы один актуальный лидер
* snakeoil **не используется**
* используются **свои сертификаты**

---

# 1️⃣ ВОССТАНОВЛЕНИЕ CA / SSL (если трогали snakeoil)

## 1.1. Восстановление базовой CA-системы

```bash
rm -f /etc/ssl/certs/ssl-cert-snakeoil.pem
rm -f /etc/ssl/private/ssl-cert-snakeoil.key

apt-get install --reinstall ssl-cert
update-ca-certificates --fresh
```

---

## 1.2. Добавление собственного CA

```bash
nano /etc/ssl/certs/utm-DC-CA.crt
update-ca-certificates
```

---

## 1.3. Сертификат PostgreSQL

```bash
nano /etc/ssl/certs/pg-server.crt
nano /etc/ssl/private/pg-server.key

chown postgres:postgres /etc/ssl/private/pg-server.key
chmod 600 /etc/ssl/private/pg-server.key
```

---

# 2️⃣ ПРОВЕРКА etcd (ДО ЛЮБЫХ ДЕЙСТВИЙ С Patroni)

```bash
export ETCDCTL_API=3
etcdctl endpoint status --write-out=table
etcdctl member list
```

Требования:

* **ровно один leader**
* все members `started`

❌ Пока этого нет — **Patroni не трогаем**

---

# 3️⃣ ❗❗❗ КЛЮЧЕВОЙ ШАГ

## ПОЛНОЕ УДАЛЕНИЕ МЕТОК Patroni В etcd

Этот шаг **обязателен**, если:

* все узлы `Replica`
* `no good candidates`
* `cluster unlocked`
* `state unknown`

---

## 3.1. Остановить Patroni НА ВСЕХ узлах

```bash
systemctl stop patroni
```

---

## 3.2. ЖЁСТКАЯ очистка DCS

```bash
export ETCDCTL_API=3
etcdctl del --prefix /service/pg-ha-cluster/
```

---

## 3.3. Контроль (ОБЯЗАТЕЛЬНО)

```bash
etcdctl get /service/pg-ha-cluster/ --prefix
```

✅ **Вывод пустой**
❌ Если не пустой — кластер не восстановится

---

# 4️⃣ КОНФИГУРАЦИЯ Patroni (ОБЩАЯ ЛОГИКА)

## 4.1. Пользователи

| Назначение  | Пользователь | Пароль   |
| ----------- | ------------ | -------- |
| superuser   | pgsqluser    | PASSWORD |
| replication | repl         | PASSWORD |

---

## 4.2. pg_hba.conf (СТРОГО)

```yaml
pg_hba:
  - local all all trust
  - hostssl replication repl all scram-sha-256
  - hostssl all pgsqluser all scram-sha-256
  - hostssl all postgres all scram-sha-256
```

❌ никакого `md5`
❌ никакого non-SSL

---

## 4.3. SSL-параметры PostgreSQL

```yaml
postgresql:
  parameters:
    ssl: on
    ssl_cert_file: /etc/ssl/certs/pg-server.crt
    ssl_key_file: /etc/ssl/private/pg-server.key
    ssl_ca_file: /etc/ssl/certs/utm-DC-CA.crt
```

---

# 5️⃣ BOOTSTRAP КЛАСТЕРА (САМЫЙ ВАЖНЫЙ МОМЕНТ)

## 5.1. Условие

> В момент bootstrap **работает ТОЛЬКО ОДИН Patroni**

---

## 5.2. Старт лидера

На выбранном узле (будущий лидер):

```bash
systemctl start patroni
sleep 5
patronictl -c /etc/patroni.yml list
```

🎯 Ожидаемо:

```
pgXX | Leader | running
```

Если лидера нет:

* DCS очищен не полностью
* Patroni не видит etcd
* PostgreSQL не стартует из-за SSL

---

# 6️⃣ ПОДКЛЮЧЕНИЕ РЕПЛИКИ

## 6.1. Подготовка data_dir

```bash
systemctl stop patroni
rm -rf /var/lib/postgresql/16/main/*
```

---

## 6.2. SSL для basebackup

```bash
export PGSSLMODE=require
```

---

## 6.3. Запуск Patroni

```bash
systemctl start patroni
journalctl -u patroni -f
```

Ожидаемо:

```
pg_basebackup started
pg_basebackup completed
replica initialized
```

---

# 7️⃣ ФИНАЛЬНАЯ ПРОВЕРКА

```bash
patronictl -c /etc/patroni.yml list
```

Идеал:

```
pg02 | Leader  | running
pg01 | Replica | running | Lag 0
```

---

# 8️⃣ ПРОВЕРКА SSL

```bash
sudo -u postgres psql -c "show ssl;"
sudo -u postgres psql -c "show ssl_cert_file;"
```

---

# 9️⃣ ПРОВЕРКА РЕПЛИКАЦИИ

На реплике:

```bash
sudo -u postgres psql -c "select status, ssl from pg_stat_wal_receiver;"
```

Должно быть:

* `status = streaming`
* `ssl = true`

---

# 🔐 10️⃣ БЭКАП СЕРТИФИКАТОВ

```bash
tar czf /root/pg_ssl_backup_$(date +%F).tgz \
  /etc/ssl/certs/pg-server.crt \
  /etc/ssl/private/pg-server.key \
  /etc/ssl/certs/utm-DC-CA.crt
```

---

# 🚨 АНТИ-ПАТТЕРНЫ (ЗАПРЕЩЕНО)

❌ править snakeoil
❌ надеяться на `server.crt` по умолчанию
❌ `host replication … md5`
❌ запускать два Patroni при пустом DCS
❌ `reinit`, если нет лидера
❌ чинить Patroni без очистки `/service/<cluster>`

---

# 🧠 ФИНАЛЬНЫЙ ВЫВОД

**Корневая причина**: stale-ключи Patroni в etcd
**Лечение**:

1. stop Patroni
2. `etcdctl del --prefix /service/pg-ha-cluster/`
3. bootstrap одного узла



— говори.
