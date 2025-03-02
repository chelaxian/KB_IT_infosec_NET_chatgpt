# Автоматическая загрузка файла file.txt в репозиторий GitHub каждые 60 секунд

Данное руководство описывает процесс настройки автоматической загрузки файла `file.txt` в ваш репозиторий GitHub с использованием скрипта Bash и таймера systemd, который будет запускаться каждые 60 секунд.

## Предварительные требования

1. **Операционная система:** Linux с поддержкой systemd.
2. **Установленные утилиты:**
   - `curl` — для HTTP-запросов.
   - `jq` — для обработки JSON (установить можно командой `sudo apt-get install jq` на системах, основанных на Debian).
   - `base64` — для кодирования файлов в Base64 (обычно предустановлен).
3. **Персональный токен доступа (PAT) GitHub** с правами `repo` или `public_repo` (в зависимости от типа репозитория) для аутентификации при загрузке файлов. Создать токен можно в настройках вашего аккаунта GitHub.

## Шаг 1: Создание скрипта для загрузки файла в GitHub

Создайте Bash-скрипт, который будет выполнять следующие действия:

1. Проверять наличие файла `file.txt`.
2. Кодировать содержимое файла в формат Base64.
3. Получать текущий SHA файла из репозитория (требуется для обновления существующего файла).
4. Отправлять PUT-запрос к API GitHub для загрузки (или обновления) файла в репозитории.

**Пример скрипта:**

```bash
#!/bin/bash

# Путь к файлу file.txt
FILE_PATH=/path/to/your/file.txt

# Удаление старых куки
rm -rf "$FILE_PATH"

# (опционально) Выполнение команды yt-dlp с использованием cookies
# yt-dlp --cookies "$FILE_PATH" --cookies-from-browser chromium

# Github Acsess Token
YOUR_NEW_TOKEN=github_pat_1121YGGUYguyUI___THIS_IS_YOUR_TOKEN___723624783fgfjkdfg

# Проверка существования файла file.txt
if [[ -f "$FILE_PATH" ]]; then
    # Кодирование содержимого файла в base64
    CONTENT=$(base64 -w 0 "$FILE_PATH")

    # Получение текущего SHA файла из репозитория
    RESPONSE=$(curl -s -H "Authorization: token $YOUR_NEW_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/chelaxian/REPONAME/path/to/your/file.txt")
    SHA=$(echo "$RESPONSE" | jq -r .sha)

    # Подготовка данных для запроса
    read -r -d '' DATA <<EOF
{
  "message": "Обновление file.txt",
  "content": "$CONTENT",
  "sha": "$SHA"
}
EOF

    # Загрузка файла в GitHub
    curl -X PUT \
        -H "Authorization: token $YOUR_NEW_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$DATA" \
        "https://api.github.com/repos/chelaxian/REPONAME/path/to/your/file.txt"
else
    echo "Файл $FILE_PATH не найден."
fi

```

**Примечания:**

- Замените `ваш_персональный_токен_доступа` на ваш действительный PAT.
- Убедитесь, что переменные `REPO_OWNER`, `REPO_NAME` и `FILE_PATH` правильно указывают на ваш репозиторий и путь к файлу.
- Скрипт предполагает, что файл `file.txt` уже существует по указанному пути.

Сохраните этот скрипт, например, как `/usr/local/bin/update_files.sh`, и сделайте его исполняемым:

```bash
chmod +x /usr/local/bin/update_files.sh
```

## Шаг 2: Создание службы systemd

Создайте unit-файл службы systemd, который будет запускать ваш скрипт.

**Пример файла службы:**

Создайте файл `/etc/systemd/system/update_files.service` со следующим содержимым:

```ini
[Unit]
Description=Обновление file.txt и загрузка в GitHub

[Service]
Type=oneshot
ExecStart=/usr/local/bin/update_files.sh
```

**Примечания:**

- `Type=oneshot` указывает, что служба выполняет однократное действие и завершается.
- Убедитесь, что путь в `ExecStart` соответствует расположению вашего скрипта.

## Шаг 3: Создание таймера systemd

Создайте unit-файл таймера systemd, который будет запускать созданную службу каждые 60 секунд.

**Пример файла таймера:**

Создайте файл `/etc/systemd/system/update_files.timer` со следующим содержимым:

```ini
[Unit]
Description=Таймер для обновления file.txt каждые 60 секунд

[Timer]
OnBootSec=60
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
```

**Примечания:**

- `OnBootSec=60` означает, что первый запуск произойдет через 60 секунд после загрузки системы.
- `OnUnitActiveSec=60` устанавливает интервал в 60 секунд между запусками.

## Шаг 4: Активация и запуск таймера

После создания файлов службы и таймера необходимо перезагрузить конфигурацию systemd, активировать и запустить таймер:

```bash
# Перезагрузка конфигурации systemd
sudo systemctl daemon-reload

# Активация таймера при старте системы
sudo systemctl enable update_files.timer

# Немедленный запуск таймера
sudo systemctl start update_files.timer
```



 
