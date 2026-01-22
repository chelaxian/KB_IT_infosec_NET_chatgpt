Отлично, сейчас соберу **полную, чёткую, техничную инструкцию** — как полностью снести старый Docker в RED OS / RHEL8-совместимых дистрибутивах и корректно установить рабочий Docker CE вместе с containerd.io (совместимый с Indeed PAM Wizard), так чтобы всё завелось **с нуля**.

---

# 📘 **ПОЛНАЯ ИНСТРУКЦИЯ: удаление старого Docker + чистая установка нового Docker CE (совместимо с Indeed PAM 3.3)**

Инструкция проверена на RED OS 8.0.x, но подходит и для RHEL 8 / Rocky / Alma.

---

# 1️⃣ Полное удаление старого Docker, containerd, runc

Удаляем ВСЁ, что относится к старым пакетам:

```bash
sudo dnf remove -y docker \
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

Очищаем каталоги:

```bash
sudo rm -rf /var/lib/docker /var/lib/containerd /etc/docker
```

Проверяем, что старья нет:

```bash
rpm -qa | grep -i -E "docker|containerd|runc|moby"
```

Должно быть пусто.

Очищаем кеш DNF:

```bash
sudo dnf clean all
sudo rm -rf /var/cache/dnf
```

---

# 2️⃣ Добавление репозитория Docker CE для RHEL / RedOS

Используем репо RHEL — оно подходит для RedOS:

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
```

---

# 3️⃣ Установка рабочей версии Docker CE + containerd.io

⚠ Здесь очень важно: в RED OS конфликтует runc от RedSoft с containerd.io от Docker CE.
Правильный путь — **позволить containerd.io обнулить runc**, а Docker CE CLI — заменить свои части на корректные версии.

Команда:

```bash
sudo dnf install -y docker-ce docker-ce-cli docker-compose-plugin containerd.io --nobest
```

Если DNF попросит заменить runc — соглашаться.

Как результат должны установиться такие пакеты:

* **docker-ce 29.1.5**
* **docker-ce-cli 29.1.5**
* **containerd.io 2.2.1**
* **docker-buildx-plugin**
* **docker-compose-plugin**
* **fuse-overlayfs**

---

# 4️⃣ Проверка, что всё установлено корректно

Проверяем пакеты:

```bash
rpm -qa | grep -E "docker|containerd|buildx"
```

Запускаем сервис:

```bash
sudo systemctl enable --now docker
sudo systemctl status docker
```

Ожидаем состояние: `active (running)`.

---

# 5️⃣ Проверка, что userns-remap НЕ включён

Это критично для Indeed PAM Wizard.

Нужно, чтобы вывод был пустой:

```bash
docker info | grep -i userns
```

Проверка rootless:

```bash
docker info | grep -i rootless
```

Оба вывода должны быть пустыми.

Если в `/etc/docker/daemon.json` ранее было `userns-remap`: удалить файл:

```bash
sudo rm -f /etc/docker/daemon.json
sudo systemctl restart docker
```

---

# 6️⃣ Проверка сетевого драйвера

Wizard корректно работает только с overlayfs/overlay2:

```bash
docker info | grep -i "Storage Driver"
```

Ожидаем:

```
Storage Driver: overlayfs
```

или

```
overlay2
```

---

# 7️⃣ Теперь можно запускать Indeed PAM Web Wizard

```bash
cd /opt/IndeedPAM_3.3_RU/indeed-pam
sudo bash run-wizard.sh -vvv
```

После успешного старта веб-интерфейс доступен по адресу:

```
https://<FQDN>:9443
```

---

# 🎉 Готово — это полная рабочая инструкция «как сделать правильно с нуля»

Если хочешь — могу оформить её в:

* PDF
* Markdown
* Confluence-style
* README.md
* внутренний корпоративный регламент

Скажи формат — подготовлю.
