## 🎯 Цель

На RED OS 8 (RHEL8-совместимая) полностью:

1. Убрать старый Docker / containerd / runc.
2. Отключить docker-пакеты из репозиториев RedOS.
3. Поставить **чистый Docker CE** из официального Docker-репозитория.
4. Проверить, что userns/remap и rootless **выключены**.
5. Убедиться, что IndeedPAM Wizard нормально стартует.

---

## 0. Предпосылки

Работаем под `root`:

```bash
sudo -i
```

---

## 1️⃣ Полное удаление старого контейнерного стека

Сносим всё, что хотя бы отдалённо похоже на Docker / containerd / runc / moby:

```bash
dnf remove -y docker \
  docker-ce \
  docker-ce-cli \
  docker-ce-rootless-extras \
  docker-buildx-plugin \
  docker-compose-plugin \
  containerd \
  containerd.io \
  moby-engine \
  moby-cli \
  runc \
  crun \
  docker-ce-cli-doc
```

Чистим данные и конфиги:

```bash
rm -rf /var/lib/docker /var/lib/containerd /etc/docker
```

Проверяем, что пакетов действительно нет:

```bash
rpm -qa | grep -i -E "docker|containerd|runc|moby"
# Должно ничего не вывести
```

Чистим кэш dnf:

```bash
dnf clean all
rm -rf /var/cache/dnf
```

---

## 2️⃣ Отключение docker-пакетов из репозиториев RedOS

Иначе dnf будет снова пытаться тащить `docker-ce-cli-*.red80` и `runc` из redos-репозиториев, что ломает установку Docker CE.

### 2.1. Смотрим, какие репозитории есть

```bash
ls /etc/yum.repos.d/
```

Типично там будут файлы типа:

* `redos.repo`
* `redos-base.repo`
* `redos-updates.repo`
* `redos-appstream.repo` и т.п.

### 2.2. Вариант А (ручной, аккуратный) — правим `.repo` файлы

Открываем, например:

```bash
nano /etc/yum.repos.d/redos.repo
```

В каждом нужном блоке (например `[redos-base]`, `[redos-updates]`) добавляем строку:

```ini
exclude=docker* containerd* runc*
```

Пример блока:

```ini
[redos-base]
name=RedOS Base
baseurl=...
enabled=1
gpgcheck=1
exclude=docker* containerd* runc*
```

То же самое делаем в остальных `redos-*.repo`, где скачиваются обновления.

После правки можно проверить:

```bash
grep -R "exclude=.*docker" /etc/yum.repos.d
```

Ожидаем что-то вида:

```text
/etc/yum.repos.d/redos.repo:exclude=docker* containerd* runc*
...
```

### 2.3. Вариант B (быстрый, но грубый) — через sed

Если не хочешь руками лазить по каждому файлу:

```bash
sed -i '/^\[redos/{
  :a
  n
  /^\[/{ba}
  /exclude=/!s/^enabled=1/&\nexclude=docker* containerd* runc*/
}' /etc/yum.repos.d/redos*.repo
```

После этого тоже проверяем:

```bash
grep -R "exclude=.*docker" /etc/yum.repos.d
```

---

## 3️⃣ Снова чистим dnf и добавляем Docker CE repo

На всякий случай ещё раз очищаем кэш (после правки exclude):

```bash
dnf clean all
rm -rf /var/cache/dnf
```

Добавляем официальный Docker-репозиторий для RHEL:

```bash
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
```

---

## 4️⃣ Установка Docker CE + containerd.io (EL8)

Теперь можно ставить **только** пакеты из Docker-репо, без red80-мешанины:

```bash
dnf install -y docker-ce docker-ce-cli docker-compose-plugin containerd.io --nobest
```

Нормальная успешная транзакция установит примерно:

* `containerd.io-2.2.1-1.el8.x86_64`
* `docker-ce-29.1.5-1.el8.x86_64`
* `docker-ce-cli-29.1.5-1.el8.x86_64`
* `docker-buildx-plugin-0.30.1-1.el8.x86_64`
* `docker-compose-plugin-5.0.2-1.el8.x86_64`
* плюс `fuse-overlayfs`, `passt`, `passt-selinux`

Проверка:

```bash
rpm -qa | grep -E "docker|containerd" | sort
```

---

## 5️⃣ Запуск и базовая проверка Docker

Запускаем и добавляем в автозапуск:

```bash
systemctl enable --now docker
systemctl status docker
```

Ожидаем:

```text
Active: active (running)
...
/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

Проверяем простейший контейнер:

```bash
docker run --rm hello-world
```

Если вывелась классическая портянка `Hello from Docker!` – всё ок.

---

## 6️⃣ Проверка, что userns/remap и rootless ОТКЛЮЧЕНЫ

Это критично для Indeed PAM Wizard: раньше у тебя ansible внутри контейнера пытался работать от `nobody` (uid 65534), из-за чего был:

```text
chown failed: Operation not permitted: ... owner: nobody, gid: 65534
```

Теперь проверяем:

```bash
docker info | grep -i userns
docker info | grep -i rootless
```

Если всё хорошо — обе команды ничего не выводят.

Если вдруг в `/etc/docker/daemon.json` остались старые настройки (например, `userns-remap`), просто удаляем конфиг:

```bash
rm -f /etc/docker/daemon.json
systemctl restart docker
```

И повторяем проверки `docker info | grep -i userns`.

---

## 7️⃣ Проверка storage driver

На всякий случай:

```bash
docker info | grep -i "Storage Driver"
```

Ожидаем:

```text
Storage Driver: overlayfs
```

или `overlay2` — это нормально для RED OS 8.

---

## 8️⃣ Запуск Indeed PAM Web Wizard

Переходим в каталог дистрибутива:

```bash
cd /opt/IndeedPAM_3.3_RU/indeed-pam
```

(или куда ты его положил — у тебя это был `/opt/IndeedPAM_3.3_RU/indeed-pam`)

Запускаем:

```bash
sudo bash run-wizard.sh -vvv
```

Теперь:

* шаг `TASK [Create common directories if not exist]` должен пройти без ошибок;
* не должно быть `chown failed: Operation not permitted` и `owner: nobody`;
* wizard поднимет контейнер с API/UI и выведет, что слушает `WEB_WIZARD_PORT=9443`.

Дальше заходишь в браузер:

```text
https://<acs.indeed.step>:9443
```

(по твоему FQDN/IP) — и работаешь с web-wizard.

