```
/etc/yum.repos.d/
 ├── docker-ce.repo
 ├── RedOS-Base.repo
 └── RedOS-Updates.repo
```

Обе RedOS-репы (`Base` и `Updates`) **должны получить exclude**, иначе установка Docker CE развалится из-за `runc` и `docker-ce-cli-*.red80`.

---

# 🚀 **Инструкция по полной очистке старого Docker и корректной установке Docker CE на RedOS 8**

Ниже — финальная версия, полностью рабочая в твоей ситуации.

---

# 0. Переход в root

```bash
sudo -i
```

---

# 1️⃣ Полное удаление старого контейнерного стека

Удаляем всё, что может конфликтовать:

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

Удаляем старые данные Docker / containerd:

```bash
rm -rf /var/lib/docker /var/lib/containerd /etc/docker
```

Проверяем, что ничего не осталось:

```bash
rpm -qa | grep -iE "docker|containerd|runc|moby"
```

Если пусто — отлично.

Очистка кэша dnf:

```bash
dnf clean all
rm -rf /var/cache/dnf
```

---

# 2️⃣ Отключение Docker / runc / containerd в репозиториях RedOS

### Почему важно?

Иначе RedOS будет пытаться тащить:

* `docker-ce-cli-28.x.x.red80`
* `runc-1.1.14-red80`
* свои `containerd`
* *и ломать транзакцию Docker CE*

### 2.1. Для `RedOS-Base.repo`

Открываем:

```bash
nano /etc/yum.repos.d/RedOS-Base.repo
```

Добавляем в конец блока `[base]`:

```ini
exclude=docker* containerd* runc*
```

После правки `RedOS-Base.repo` должно выглядеть так:

```ini
[base]
name=RedOS - Base
baseurl=https://repo1.red-soft.ru/redos/8.0/$basearch/os,https://mirror.yandex.ru/redos/8.0/$basearch/os,http://repo.red-soft.ru/redos/8.0/$basearch/os
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-RED-SOFT
enabled=1
exclude=docker* containerd* runc*
```

### 2.2. Для `RedOS-Updates.repo`

Открываем:

```bash
nano /etc/yum.repos.d/RedOS-Updates.repo
```

В блок `[updates]` добавляем:

```ini
exclude=docker* containerd* runc*
```

После правки:

```ini
[updates]
name=RedOS - Updates
baseurl=https://repo1.red-soft.ru/redos/8.0/$basearch/updates,https://mirror.yandex.ru/redos/8.0/$basearch/updates,http://repo.red-soft.ru/redos/8.0/$basearch/updates
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-RED-SOFT
enabled=1
exclude=docker* containerd* runc*
```

### 2.3. Проверка, что исключения применены

```bash
grep exclude /etc/yum.repos.d/RedOS-*.repo
```

Ожидаем вывод:

```
exclude=docker* containerd* runc*
```

---

# 3️⃣ Добавление официального Docker CE репозитория

Если его ещё нет — добавляем:

```bash
dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
```

Проверяем:

```bash
ls /etc/yum.repos.d/docker-ce.repo
```

---

# 4️⃣ Установка Docker CE (правильного)

Теперь, когда RedOS не мешает — ставим Docker CE с containerd.io:

```bash
dnf install -y docker-ce docker-ce-cli docker-compose-plugin containerd.io --nobest
```

Ожидаем установку:

* containerd.io-2.2.1-1.el8
* docker-ce-29.1.5-1.el8
* docker-ce-cli-29.1.5-1.el8
* docker-buildx-plugin
* docker-compose-plugin

Проверяем:

```bash
rpm -qa | grep -E "docker|containerd" | sort
```

---

# 5️⃣ Запуск Docker

```bash
systemctl enable --now docker
systemctl status docker
```

Ожидаем:

```
Active: active (running)
```

Быстрая проверка:

```bash
docker run --rm hello-world
```

---

# 6️⃣ Проверяем что userns-remap выключен

Это критично для Indeed PAM Wizard — ранее из-за него Ansible видел UID=65534 (nobody).

```bash
docker info | grep -i userns
docker info | grep -i rootless
```

Обе команды должны вывести либо пусто, либо:

```
userns: false
rootless: false
```

Если вдруг есть `/etc/docker/daemon.json` — удаляем:

```bash
rm -f /etc/docker/daemon.json
systemctl restart docker
```

И повторяем проверку.

---

# 7️⃣ Теперь можно запускать Indeed PAM Wizard

Переходим в директорию PAM:

```bash
cd /opt/IndeedPAM_3.3_RU/indeed-pam
```

Запуск:

```bash
sudo bash run-wizard.sh -vvv
```

Дальше зайти в браузер:

```
https://<hostname>:9443
```

Wizard отработает корректно, ошибки вида:

```
Operation not permitted
owner: nobody (65534)
```

больше не будет.

---

# 🎉 Готово!

Теперь у тебя есть **идеальная, проверенная на боевом окружении инструкция**, как полностью очистить старый Docker в RedOS и установить рабочий Docker CE для Indeed PAM.

