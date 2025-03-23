Чтобы переделать указанную команду и использовать локальный файл вместо скачивания скрипта с GitHub, нужно выполнить несколько шагов. Оригинальная команда:

```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/cosmos.sh)"
```

скачивает скрипт `cosmos.sh` с GitHub и выполняет его. Вы хотите, чтобы вместо этого использовался локальный файл, содержимое которого вы предоставили. Однако в этом скрипте есть строка `source <(curl -s https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func)`, которая также загружает файл `build.func` с GitHub. Чтобы полностью исключить зависимость от GitHub, нужно использовать локальные версии обоих файлов. Вот пошаговая инструкция:

---

### Шаг 1: Сохраните скрипт `cosmos.sh` локально
Возьмите предоставленный вами скрипт и сохраните его в локальный файл, например, `/root/cosmos.sh`. Убедитесь, что содержимое выглядит так:

```bash
#!/usr/bin/env bash
source <(curl -s https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func)
# Copyright (c) 2021-2025 community-scripts ORG
# Author: Michel Roegl-Brunner (michelroegl-brunner)
# License: MIT | https://github.com/community-scripts/ProxmoxVE/raw/main/LICENSE
# Source: https://https://cosmos-cloud.io/

APP="cosmos"
var_tags="os,docker"
var_cpu="2"
var_ram="2048"
var_disk="8"
var_os="debian"
var_version="12"
var_unprivileged="1"

header_info "$APP"
variables
color
catch_errors

function update_script() {
  header_info
  check_container_storage
  check_container_resources
  if [[ ! -d /opt/cosmos ]]; then
    msg_error "No ${APP} Installation Found!"
    exit
  fi
  msg_ok "${APP} updates itself automatically!"
}

start
build_container
description

msg_ok "Completed Successfully!\n"
echo -e "${CREATING}${GN}${APP} setup has been successfully initialized!${CL}"
echo -e "${INFO}${YW} Access it using the following URL:${CL}"
echo -e "${TAB}${GATEWAY}${BGN}http://${IP}${CL}"
```

---

### Шаг 2: Скачайте и сохраните `build.func` локально
Скрипт `cosmos.sh` использует функции из файла `build.func`, который сейчас загружается с GitHub. Чтобы использовать локальную версию, скачайте этот файл с помощью команды:

```bash
wget https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func -O /root/build.func
```

Это сохранит файл `build.func` в `/root/build.func`. Убедитесь, что файл успешно загружен.

---

### Шаг 3: Измените `cosmos.sh` для использования локального `build.func`
Откройте файл `/root/cosmos.sh` в текстовом редакторе (например, `nano /root/cosmos.sh`) и найдите строку:

```bash
source <(curl -s https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func)
```

Замените её на:

```bash
source /root/build.func
```

После этого скрипт будет использовать локальный файл `build.func` вместо загрузки с GitHub.

---

### Шаг 4: Сделайте скрипт исполняемым (опционально)
Чтобы скрипт можно было запускать напрямую, выполните команду:

```bash
chmod +x /root/cosmos.sh
```

---

### Шаг 5: Запустите локальный скрипт
Теперь вместо оригинальной команды используйте следующую:

```bash
bash /root/cosmos.sh
```

Эта команда выполнит ваш локальный скрипт `cosmos.sh`, который, в свою очередь, будет использовать локальный файл `build.func`.

---

### Итоговый результат
Вместо:

```bash
bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/cosmos.sh)"
```

выполните следующие действия:
1. Сохраните предоставленный скрипт как `/root/cosmos.sh`.
2. Скачайте `build.func`:
   ```bash
   wget https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/misc/build.func -O /root/build.func
   ```
3. Отредактируйте `/root/cosmos.sh`, заменив `source <(curl -s ...)` на `source /root/build.func`.
4. Запустите скрипт:
   ```bash
   bash /root/cosmos.sh
   ```

---

### Примечания
- Убедитесь, что оба файла (`/root/cosmos.sh` и `/root/build.func`) находятся в указанных путях. Если вы хотите использовать другие пути, измените их в командах и в скрипте соответственно.
- Если в `build.func` есть дополнительные зависимости от GitHub, их тоже нужно будет скачать и настроить локально.
- После выполнения скрипт установит Cosmos, используя только локальные файлы, без обращения к GitHub.

Теперь ваш запрос полностью выполнен!
