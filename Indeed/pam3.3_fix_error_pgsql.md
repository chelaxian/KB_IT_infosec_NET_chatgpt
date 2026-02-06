# Развёртывание PostgreSQL для Indeed PAM (Core + IdP) и интеграция

## Предварительные условия

* Хост: `pam.indeed.domain`
* IP хоста: `100.100.100.100`
* PAM 3.3.0 в Docker, каталог: `/etc/indeed/indeed-pam/`
* PostgreSQL 16, data dir: `/var/lib/pgsql/data`
* Сервис СУБД: `postgresql.service`
* Пользователь БД: `pgsqluser`
* Пароль БД: `<PAM_DB_PASSWORD>` (вместо реального)

---

## 1. Установка и инициализация PostgreSQL

> На новой машине делай это один раз.

```bash
# 1. Установить PostgreSQL и утилиты
sudo dnf install -y postgresql-server postgresql

# 2. Инициализация кластера
sudo postgresql-setup --initdb

# 3. Включить автозапуск и запустить
sudo systemctl enable --now postgresql

# 4. Проверить статус
systemctl status postgresql
```

---

## 2. Настройка `postgresql.conf` (порт и интерфейсы)

Файл: `/var/lib/pgsql/data/postgresql.conf`

```bash
sudo nano /var/lib/pgsql/data/postgresql.conf
```

Минимальные правки:

```conf
listen_addresses = '*'        # разрешаем слушать на всех интерфейсах
port = 5432                   # стандартный порт PostgreSQL
```

После правок:

```bash
sudo systemctl restart postgresql
systemctl status postgresql
```

Проверка, что порт слушается:

```bash
netstat -plnt | grep 5432
# или
ss -tulpn | grep 5432
```

---

## 3. Настройка `pg_hba.conf` (сетевой доступ)

Файл: `/var/lib/pgsql/data/pg_hba.conf`

```bash
sudo nano /var/lib/pgsql/data/pg_hba.conf
```

Добавь / приведи к примерно такому (главное — эти строки **выше** всяких `ident`/`peer`):

```conf
# Доступ для PAM-сервера (10.170.102.0/24)
host    all             all             10.170.102.0/24        md5

# Доступ для внутренних сетей (если нужно)
host    all             all             172.16.0.0/12          md5

# Локальный доступ
host    all             pgsqluser            127.0.0.1/32           md5
host    all             all             127.0.0.1/32           md5
host    all             all             ::1/128                md5

# (опционально, если надо вообще всем)
# host  all             all             0.0.0.0/0              md5
# host  all             all             ::/0                   md5
```

Можно убрать/закомментировать дефолтные `ident`/`peer`, чтобы не путаться, но в твоём кейсе они идут ниже, так что не мешали.

Применить:

```bash
sudo systemctl restart postgresql
sudo -u postgres psql -c "SELECT * FROM pg_hba_file_rules;"
```

---

## 4. Создание пользователя и баз PAM

### 4.1. Зайти под postgres

```bash
sudo -u postgres psql
```

### 4.2. Создать роль пользователя

```sql
CREATE ROLE pgsqluser WITH LOGIN PASSWORD '<PAM_DB_PASSWORD>';

ALTER ROLE pgsqluser SET client_encoding TO 'UTF8';
ALTER ROLE pgsqluser SET default_transaction_isolation TO 'read committed';
ALTER ROLE pgsqluser SET timezone TO 'UTC';
```

### 4.3. Создать базы для PAM

```sql
CREATE DATABASE "Core"    OWNER pgsqluser;
CREATE DATABASE "CoreJobs" OWNER pgsqluser;
CREATE DATABASE "Idp"     OWNER pgsqluser;
CREATE DATABASE "IdpJobs" OWNER pgsqluser;
\q
```
сделать пользователя владельцем баз данных
```
ALTER DATABASE "Core" OWNER TO pgsqluser;
ALTER DATABASE "CoreJobs" OWNER TO pgsqluser;
ALTER DATABASE "Idp" OWNER TO pgsqluser;
ALTER DATABASE "IdpJobs" OWNER TO pgsqluser;
\q
```
---

## 5. Проверка подключений к БД

### 5.1. Локально с хоста

```bash
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 127.0.0.1 -U pgsqluser -d Core    -c "SELECT 1;"
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 127.0.0.1 -U pgsqluser -d Idp     -c "SELECT 1;"
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 127.0.0.1 -U pgsqluser -d CoreJobs -c "SELECT 1;"
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 127.0.0.1 -U pgsqluser -d IdpJobs  -c "SELECT 1;"
```

### 5.2. По IP хоста (как будут ходить контейнеры PAM)

```bash
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 100.100.100.100 -U pgsqluser -d Core -c "SELECT 1;"
PGPASSWORD='<PAM_DB_PASSWORD>' psql -h 100.100.100.100 -U pgsqluser -d Idp  -c "SELECT 1;"
```

Если тут всё ОК — сеть и `pg_hba.conf` настроены.

---

## 6. Установка расширения `uuid-ossp` (важно!)

Без него `pam-core` падает с:

> `расширение "uuid-ossp" отсутствует`

Ставим в **Core** и **Idp**:

```bash
sudo -u postgres psql -d Core -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
sudo -u postgres psql -d Idp  -c 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

# Проверка
sudo -u postgres psql -d Core -c '\dx'
sudo -u postgres psql -d Idp  -c '\dx'
```

Ожидаем увидеть:

```text
uuid-ossp | 1.1 | public | generate universally unique identifiers (UUIDs)
```

---

## 7. Отключение SQL-proxy в Docker (конфликт портов)

По умолчанию контейнер `pam-sql-proxy` слушает тот же порт 5432 на `100.100.100.100`, что и твой PostgreSQL на хосте.

### 7.1. Посмотреть, кто держит 5432/55432

```bash
netstat -plnt | egrep '5432|55432'
# или
ss -tulpn | egrep '5432|55432'
```

Типичная картина, которую ты видел:

```text
tcp  0 0 100.100.100.100:5432   0.0.0.0:* LISTEN 2239836/docker-proxy
tcp  0 0 100.100.100.100:55432  0.0.0.0:* LISTEN 2239851/docker-proxy
```

### 7.2. Остановить sql-proxy контейнер

```bash
docker ps | grep pam-sql-proxy
docker stop pam-sql-proxy
```

После этого порт 5432 за хостовым PostgreSQL, конфликт исчезает.

> На новой инсталляции: либо **вообще не поднимать** `pam-sql-proxy` (убрать из docker-compose/скриптов), либо оставлять остановленным.

---

## 8. Настройка `appsettings.json` для Core

Каталог Core:

`/etc/indeed/indeed-pam/core/appsettings.json`

### 8.1. Расшифровать конфиг

```bash
cd /etc/indeed/indeed-pam
sudo bash tools/protector.sh unprotect
```

### 8.2. Правка `core/appsettings.json`

Открываем:

```bash
nano core/appsettings.json
```

Блок `ConnectionStrings` и `Database` должен быть приведён к PostgreSQL:

```jsonc
"ConnectionStrings": {
  "PamCore":  "Host=100.100.100.100;Port=5432;Database=Core;Username=pgsqluser;Password=<PAM_DB_PASSWORD>;",
  "JobsQueue": "Host=100.100.100.100;Port=5432;Database=CoreJobs;Username=pgsqluser;Password=<PAM_DB_PASSWORD>;"
},
"Database": {
  "Provider": "PgSql",
  "CommandTimeout": "00:00:30"
}
```

> У тебя реально стоял вариант вида `Server=100.100.100.100;Database=Core;User Id=pgsqluser;Password=...;TrustServerCertificate=True` — он тоже работает с Npgsql, но canonical синтаксис для PostgreSQL — через `Host`/`Port`/`Username`.

Остальные секции (`Auth`, `Idp`, `Hangfire` и т.п.) оставляем как есть.

### 8.3. Обратно зашифровать конфиг

```bash
sudo bash tools/protector.sh protect
```

---

## 9. Настройка `appsettings.json` для IdP + отключение SSL

Каталог IdP:

`/etc/indeed/indeed-pam/idp/appsettings.json`

### 9.1. Расшифровать

```bash
cd /etc/indeed/indeed-pam/idp
sudo bash ../tools/protector.sh unprotect
```

### 9.2. Правка `ConnectionStrings`

```bash
nano /etc/indeed/indeed-pam/idp/appsettings.json
```

Привести к PostgreSQL и сразу **отключить SSL**, чтобы не ловить:

> `Npgsql.PostgresException: 08000: SSL is required`

Пример:

```jsonc
"ConnectionStrings": {
  "DefaultConnection": "Host=100.100.100.100;Port=5432;Database=Idp;Username=pgsqluser;Password=<PAM_DB_PASSWORD>;SslMode=Disable;",
  "JobsQueue":        "Host=100.100.100.100;Port=5432;Database=IdpJobs;Username=pgsqluser;Password=<PAM_DB_PASSWORD>;SslMode=Disable;"
},
"Database": {
  "Provider": "PgSql"
}
```

> Ключевой момент: `SslMode=Disable;` — именно это убирает требование SSL, из-за которого `pam-idp` у тебя падал.

Остальное (IdentitySettings, UserCatalog, NLog, Radius, LDAP-доступ и т.п.) оставляем, просто не светим реальные пароли.

### 9.3. Обратно зашифровать конфиг

```bash
sudo bash ../tools/protector.sh protect
```

---

## 10. Запуск/перезапуск контейнеров PAM

### 10.1. Перезапустить PostgreSQL (если что менялось в конфиге)

```bash
sudo systemctl restart postgresql
systemctl status postgresql
```

### 10.2. Перезапустить PAM-компоненты

Вендорский скрипт (как ты уже делал):

```bash
cd /etc/indeed/indeed-pam/scripts

# Перезапуск Core
sudo bash restart-pam.sh core

# Перезапуск IdP (если есть отдельная цель — зависит от скрипта)
# sudo bash restart-pam.sh idp

# При необходимости — перезапустить весь стек (смотри help скрипта)
```

Проверка:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs pam-core --tail=100
# и когда pam-idp будет как отдельный контейнер:
# docker logs pam-idp --tail=100
```

Для Core ты уже видел картину:

* сначала падал с `расширение "uuid-ossp" отсутствует`;
* после `CREATE EXTENSION` — контейнер стал `healthy` и миграциями создал таблицы (`\dt` в `Core` показал 50+ таблиц).

---

## 11. Проверка health-эндпойнтов

После того как всё поднято:

```bash
curl -k https://pam.indeed.domain/core/health
curl -k https://pam.indeed.domain/idp/health
curl -k https://pam.indeed.domain/mc/health
curl -k https://pam.indeed.domain/uc/health
```

Ожидаем:

* `/core/health` — JSON вида:

  ```json
  {
    "Status": "Healthy",
    "Entries": {
      "core-main-db": { "Status": "Healthy" },
      "core-jobs-db": { "Status": "Healthy" }
    }
  }
  ```

* `/idp/health` — аналогично (после успешных миграций IdP).

* `/mc/health` и `/uc/health` фактически SPA-странички (HTML Angular/React), как ты уже видел.

---

## 12. База после миграций (контрольная проверка)

Проверить, что таблицы созданы:

```bash
sudo -u postgres psql -d Core -c '\dt'
sudo -u postgres psql -d CoreJobs -c '\dt'
sudo -u postgres psql -d Idp -c '\dt'
sudo -u postgres psql -d IdpJobs -c '\dt'
```

Для Core ты уже видел список:

* `Accounts`, `Applications`, `Policies`, `Resources`, `Sessions`, `Users`, `__EFMigrationsHistory` и т.д.

Для Idp после запуска соответствующего контейнера будет аналогично — своя схема.

---

## 13. Быстрый чек-лист «на новой инсталляции»

Чтобы вообще без мыслей:

1. **Поставить PostgreSQL, инициализировать, включить сервис.**
2. В `postgresql.conf`: `listen_addresses='*'`, `port=5432`.
3. В `pg_hba.conf`: добавить `host all all 10.170.102.0/24 md5`, `172.16.0.0/12 md5`, `127.0.0.1/32 md5`, `::1/128 md5`.
4. Перезапустить PostgreSQL.
5. Создать роль `pgsqluser` с паролем `<PAM_DB_PASSWORD>`.
6. Создать базы: `Core`, `CoreJobs`, `Idp`, `IdpJobs` (OWNER `pgsqluser`).
7. Установить расширение `"uuid-ossp"` в `Core` и `Idp`.
8. Проверить psql-подключение к `Core`/`Idp` по `127.0.0.1` и `100.100.100.100`.
9. Остановить `pam-sql-proxy`, чтобы избавиться от конфликта портов.
10. `protector.sh unprotect` → правка `core/appsettings.json` на PostgreSQL-строку, `Provider=PgSql` → `protect`.
11. `protector.sh unprotect` → правка `idp/appsettings.json` на PostgreSQL-строку, `Provider=PgSql`, добавить `SslMode=Disable` → `protect`.
12. Перезапустить `postgresql.service`.
13. Перезапустить PAM-контейнеры (`restart-pam.sh core` + при необходимости IdP).
14. Проверить `docker ps`, логи `pam-core`/`pam-idp`, убедиться, что нет ошибок Npgsql.
15. Проверить `curl -k https://pam.indeed.domain/core/health` и `/idp/health` + доступ к `mc` и `uc`.

основе этого сделать ещё короткую «шпаргалку в один экран» или `.md` в стиле «operations runbook», чтобы просто скопировать на сервер в `/root/README-pam-postgres.md`.
