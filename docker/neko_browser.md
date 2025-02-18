# n.eko - Запуск Chromium в режиме киоска с изоляцией сайта (опционально)

Этот проект настраивает и запускает n.eko - веб-приложение для удалённого доступа к браузеру Chromium. Контейнер запускает Chromium в режиме киоска, изолируя доступ только к заданному веб-сайту (опционально).

## 📌 Установка и запуск

### 1️⃣ Клонирование репозитория
```bash
mkdir -p ~/Browser/neko
cd ~/Browser/neko
git clone https://github.com/m1k1o/neko
```

### 2️⃣ Создание необходимых файлов
#### `docker-compose.yaml`
```yaml
services:
  neko:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    shm_size: 2gb
    ports:
      - "8080:8080"
      - "52000-52100:52000-52100/udp"
    cap_add:
      - SYS_ADMIN
    environment:
      NEKO_SCREEN: "1920x1080@30"
      NEKO_PASSWORD: 'neko'
      NEKO_PASSWORD_ADMIN: 'admin'
      NEKO_EPR: "52000-52100"
      NEKO_IMPLICIT_CONTROL: "true"
      #NEKO_NAT1TO1: 158.180.231.91
      NEKO_LOCKS: file_transfer
      NEKO_IPFETCH: "http://checkip.amazonaws.com"
      NEKO_FILE_TRANSFER_ENABLED: "false"
      #NEKO_CMD: "chromium-browser --kiosk --app=https://chatgpt.com --noerrdialogs --disable-session-crashed-bubble --disable-infobars"
      ENV_USER: "neko"
      ENV_DISPLAY: ":0"
    volumes:
      - ./preferences.json:/tmp/preferences.json
      - ./policies.json:/tmp/policies.json
      #- ./supervisord.conf:/tmp/supervisord.conf
      - ./policies.json:/etc/chromium/policies/managed/policies.json
      - ./preferences.json:/etc/chromium/policies/managed/preferences.json
      #- ./supervisord.conf:/etc/supervisor/supervisord.conf
```

#### `Dockerfile`
```dockerfile
FROM ghcr.io/m1k1o/neko/arm-chromium:latest

# Устанавливаем Xvfb (если он не включён в базовый образ)
RUN apt-get update && \
    apt-get install -y xvfb && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Копируем локальные файлы конфигураций во временную директорию
COPY ./preferences.json /tmp/preferences.json
COPY ./policies.json /tmp/policies.json

# Создаем скрипт для копирования файлов в целевые директории
# Если файлы отличаются, они будут скопированы; затем запускается supervisord
RUN echo '#!/bin/bash\n\
if ! cmp -s /tmp/preferences.json /etc/chromium/policies/managed/preferences.json; then\n\
  cp /tmp/preferences.json /etc/chromium/policies/managed/preferences.json;\n\
fi\n\
if ! cmp -s /tmp/policies.json /etc/chromium/policies/managed/policies.json; then\n\
  cp /tmp/policies.json /etc/chromium/policies/managed/policies.json;\n\
fi\n\
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf' > /docker-entrypoint.sh

# Делаем скрипт исполняемым
RUN chmod +x /docker-entrypoint.sh

# Задаем точку входа
ENTRYPOINT ["/docker-entrypoint.sh"]
```

#### `policies.json`
```json
{
  "AutofillAddressEnabled": false,
  "AutofillCreditCardEnabled": false,
  "BrowserSignin": 0,
  "DefaultNotificationsSetting": 2,
  "DeveloperToolsAvailability": 2,
  "EditBookmarksEnabled": false,
  "FullscreenAllowed": true,
  "IncognitoModeAvailability": 1,
  "SyncDisabled": true,
  "AutoplayAllowed": true,
  "BrowserAddPersonEnabled": false,
  "BrowserGuestModeEnabled": false,
  "DefaultPopupsSetting": 2,
  "DownloadRestrictions": 3,
  "VideoCaptureAllowed": true,
  "AllowFileSelectionDialogs": false,
  "PromptForDownloadLocation": false,
  "BookmarkBarEnabled": false,
  "PasswordManagerEnabled": false,
  "BrowserLabsEnabled": false,
  "URLAllowlist": [
    "file:///home/neko/Downloads"
  ],
  "URLBlocklist": [
      "file://*",
      "chrome://policy"
  ],
  "ExtensionInstallForcelist": [
      "hlkenndednhfkekhgcdicdfddnkalmdm;https://clients2.google.com/service/update2/crx",
      "cjpalhdlnbpafiamejdnhcphjbkeiagm;https://clients2.google.com/service/update2/crx",
      "mnjggcdmjocbbbhaepdhchncahnbgone;https://clients2.google.com/service/update2/crx"
  ],
  "ExtensionInstallAllowlist": [
      "hlkenndednhfkekhgcdicdfddnkalmdm",
      "cjpalhdlnbpafiamejdnhcphjbkeiagm",
      "mnjggcdmjocbbbhaepdhchncahnbgone"
  ],
  "ExtensionInstallBlocklist": [
      "*"
  ]
}
```

#### `preferences.json`
```json
{
  "homepage": "http://www.google.com",
  "homepage_is_newtabpage": false,
  "first_run_tabs": [
    "https://www.google.com/_/chrome/newtab?ie=UTF-8"
  ],
  "custom_links": {
    "initialized": true,
    "list": [
      {
        "title": "YouTube",
        "url": "https://www.youtube.com/"
      },
      {
        "title": "Netflix",
        "url": "https://netflix.com"
      },
      {
        "title": "Hulu",
        "url": "https://www.hulu.com/"
      },
      {
        "title": "9Anime",
        "url": "https://9anime.to/"
      },
      {
        "title": "Crunchy Roll",
        "url": "https://www.crunchyroll.com/"
      },
      {
        "title": "Funimation",
        "url": "https://www.funimation.com/"
      },
      {
        "title": "Disney+",
        "url": "https://www.disneyplus.com/"
      },
      {
        "title": "HBO Now",
        "url": "https://play.hbonow.com/"
      },
      {
        "title": "Amazon Video",
        "url": "https://www.amazon.com/Amazon-Video/b?node=2858778011"
      },
      {
        "title": "VRV",
        "url": "https://vrv.co/"
      },
      {
        "title": "Twitch",
        "url": "https://www.twitch.tv/"
      },
      {
        "title": "Mixer",
        "url": "https://mixer.com/"
      }
    ]
  },
  "browser": {
    "custom_chrome_frame": false,
    "show_home_button": true,
    "window_placement": {
      "maximized": true
    }
  },
  "bookmark_bar": {
    "show_on_all_tabs": false
  },
  "sync_promo": {
    "show_on_first_run_allowed": false
  },
  "distribution": {
    "import_bookmarks_from_file": "bookmarks.html",
    "import_bookmarks": true,
    "import_history": true,
    "import_home_page": true,
    "import_search_engine": true,
    "ping_delay": 60,
    "do_not_create_desktop_shortcut": true,
    "do_not_create_quick_launch_shortcut": true,
    "do_not_create_taskbar_shortcut": true,
    "do_not_launch_chrome": true,
    "do_not_register_for_update_launch": true,
    "make_chrome_default": true,
    "make_chrome_default_for_user": true,
    "system_level": false,
    "verbose_logging": false
  },
  "profile": {
    "avatar_index": 19,
    "default_content_setting_values": {
      "clipboard": 2,
      "cookies": 4,
      "geolocation": 2,
      "media_stream_camera": 2,
      "media_stream_mic": 2,
      "midi_sysex": 2,
      "payment_handler": 2,
      "usb_guard": 2
    },
    "name": "neko",
    "using_default_avatar": false,
    "using_default_name": false,
    "using_gaia_avatar": false
  },
  "signin": {
    "allowed": false
  }
}
```

### 3️⃣ Запуск контейнера
```bash
cd ~/Browser/neko
docker compose up --build -d
```

## 🔧 Описание конфигурации
- (опционально) **Chromium запускается в режиме киоска**, доступен только сайт `https://chatgpt.com`
- **Запрещён выход в другие вкладки и настройки браузера**
- **Запрещено использование расширений**, кроме заранее разрешённых
- **Отключена возможность скачивания файлов**

## 🛑 Остановка контейнера
```bash
docker compose down
```

## 🔄 Обновление и перезапуск
```bash
docker compose pull
docker compose up --build -d
```

(опционально) Теперь n.eko работает в режиме киоска с доступом только к `https://chatgpt.com`. 🚀

