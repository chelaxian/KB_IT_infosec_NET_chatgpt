У тебя проблема типичная: **репозитории `Ubuntu 23.10 (Mantic Minotaur)` для `arm64` удалены (или перемещены)**, потому что это **временный релиз**, поддерживаемый всего 9 месяцев. Поддержка `Ubuntu 23.10` закончилась в **июле 2024**.

### 💥 В чём суть проблемы:

* `apt` пытается тянуть пакеты с `http://ports.ubuntu.com/ubuntu-ports`, но там **репозиторий `mantic` уже удалён или перемещён в архив**.
* Все попытки `apt update`, `apt install`, `apt upgrade` завершаются с ошибкой `404 Not Found`.

---

## 🔧 Решение (вариант 1): Использовать архивные репозитории

Ubuntu перемещает устаревшие релизы на `old-releases.ubuntu.com`.

### 1. Открываем файл источников APT:

```bash
nano /etc/apt/sources.list
```

### 2. Заменяем все строки вида:

```
http://ports.ubuntu.com/ubuntu-ports mantic ...
```

на:

```
http://old-releases.ubuntu.com/ubuntu mantic ...
```

или для arm64:

```
http://old-releases.ubuntu.com/ubuntu-ports mantic ...
```

💡 Чтобы быстро заменить всё в файле:

```bash
sed -i 's|http://ports.ubuntu.com/ubuntu-ports|http://old-releases.ubuntu.com/ubuntu-ports|g' /etc/apt/sources.list
```

---

### 3. Обновляем индекс пакетов:

```bash
apt-get update
```

---

### 4. Устанавливаем нужные пакеты:

```bash
apt-get install --fix-missing <пакеты>
```

---

## ⚠️ Решение (вариант 2): Обновиться до LTS-релиза (рекомендуется)

Ubuntu 23.10 — **нестабильный релиз**, лучше всего **обновиться до 24.04 LTS**:

### Как обновиться:

```bash
apt-get update
apt-get install update-manager-core
do-release-upgrade
```

Но LXC-контейнеры иногда не дают полноценно обновиться (из-за `systemd`, `snap`, `udev`, etc.). Лучше **создать новый контейнер на `Ubuntu 24.04`** и **перенести Nextcloud туда**.

---

## ✅ Что делать сейчас

| Цель                                  | Команда                             |                                                                              |                                                                                            |                            |
| ------------------------------------- | ----------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------- |
| Заменить источники на архивные        | \`sed -i 's                         | [http://ports.ubuntu.com/ubuntu-ports](http://ports.ubuntu.com/ubuntu-ports) | [http://old-releases.ubuntu.com/ubuntu-ports](http://old-releases.ubuntu.com/ubuntu-ports) | g' /etc/apt/sources.list\` |
| Обновить пакеты                       | `apt-get update && apt-get upgrade` |                                                                              |                                                                                            |                            |
| Установить пакеты                     | `apt-get install <имена>`           |                                                                              |                                                                                            |                            |
| Проверить версию Ubuntu               | `lsb_release -a`                    |                                                                              |                                                                                            |                            |
| Альтернатива: использовать свежий LTS | `Ubuntu 24.04`                      |                                                                              |                                                                                            |                            |

---


