# README

## 1) Требования

* Ubuntu/Debian
* Node.js **v22** (через nvm)
* `yt-dlp` свежий бинарник в `/usr/local/bin/yt-dlp`
* `deno` в PATH (`/root/.deno/bin`)
* Домены:

  * `mytube.example.com` — UI
  * `rickroll.example.com` — backend + раздача `/videos` и `/subtitles` (медиа)
* Порты:

  * backend: `5551`
  * frontend: `5556`

---

## 2) Переменные окружения (как у тебя)

### `backend/.env`

```env
PORT=5551
UPLOAD_DIR=uploads
VIDEO_DIR=uploads/videos
IMAGE_DIR=uploads/images
SUBTITLES_DIR=uploads/subtitles
DATA_DIR=data
MAX_FILE_SIZE=500000000
```

### `frontend/.env`

```env
VITE_API_URL=/api
VITE_BACKEND_URL=https://rickroll.example.com
API_HOST=rickroll.example.com
API_PORT=443
```

---

## 3) Vite config (важно для доменов)

`frontend/vite.config.js` — разрешаем нужные хосты:

```js
server: {
  host: "0.0.0.0",
  port: 5556,
  allowedHosts: ["rickroll.example.com", "mytube.example.com", "swe.example.com", "se.example.com", "123.123.123.123"],
  watch: { usePolling: true, interval: 2000, ignored: ['/node_modules/'] },
}
```

---

## 4) Команда запуска (ЕДИНАЯ, из корня)

```bash
cd /root/mytube
export PATH="/root/.deno/bin:$PATH"
npm run start -- --host 0.0.0.0
```

> Запускает и backend, и frontend одновременно (concurrently).
> Важно: `deno` должен быть в PATH.

---

# Nginx Proxy Manager (твоя схема)

## Proxy Host (один, сразу для двух доменов)

**Domain Names:** `mytube.example.com` и `rickroll.example.com` (в одном Proxy Host)
**Scheme:** `http`
**Forward Hostname / IP:** `123.123.123.123` (внешний IP сервера MyTube)
**Forward Port:** `5556`
**Websockets Support:** ON
**Force SSL:** ON
Сертификат: `example.com, *.example.com`

---

## Custom Locations

### `/api` → backend (5551)

* location: `/api`
* scheme: `http`
* forward hostname/ip: `123.123.123.123/api` **(как у тебя)**
* port: `5551`

Внутренний конфиг (как на скрине, ок):

```nginx
location ^~ /api/ {
  proxy_pass http://123.123.123.123:5551/api/;
  proxy_http_version 1.1;

  proxy_request_buffering off;
  proxy_buffering off;

  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;

  proxy_set_header Range $http_range;
  proxy_set_header If-Range $http_if_range;

  proxy_read_timeout 3600;
  proxy_send_timeout 3600;
}
```

### `/videos/` → backend (5551) + Range + no 304

location: `/videos/`
forward: `123.123.123.123` port `5551`

```nginx
location ^~ /videos/ {
  proxy_pass http://123.123.123.123:5551;
  proxy_http_version 1.1;

  proxy_request_buffering off;
  proxy_buffering off;

  proxy_read_timeout 3600;
  proxy_send_timeout 3600;
  send_timeout 3600;

  proxy_set_header Host $host;
  proxy_set_header Range $http_range;
  proxy_set_header If-Range $http_if_range;

  proxy_set_header If-None-Match "";
  proxy_set_header If-Modified-Since "";

  add_header Cache-Control "no-store" always;
}
```

### `/subtitles/` → backend (5551) + no 304

location: `/subtitles/`
forward: `123.123.123.123` port `5551`

```nginx
location ^~ /subtitles/ {
  proxy_pass http://123.123.123.123:5551;
  proxy_http_version 1.1;

  proxy_request_buffering off;
  proxy_buffering off;

  proxy_set_header Host $host;
  proxy_set_header If-None-Match "";
  proxy_set_header If-Modified-Since "";

  add_header Cache-Control "no-store" always;
}
```

---

## Advanced (вкладка Advanced) — только Range/таймауты (как у тебя)

Это можно оставить:

```nginx
proxy_request_buffering off;
proxy_buffering off;

client_max_body_size 0;

proxy_read_timeout 3600;
proxy_send_timeout 3600;
send_timeout 3600;

proxy_set_header Range $http_range;
proxy_set_header If-Range $http_if_range;
```

> Примечание NPM про add_header — норм, потому что `add_header` ты делаешь правильно в Custom Locations.

---

# systemd сервис для автозапуска MyTube

Ты запускаешь как root из `/root/mytube`, значит service будет тоже под root.
**Важно:** systemd не читает твой `.bashrc`, поэтому нужно явно добавить PATH для deno и node (nvm).

У nvm node лежит примерно тут:
`/root/.nvm/versions/node/v22.21.1/bin`
(версия может отличаться)

## 1) Узнай реальные пути node/npm

```bash
which node
which npm
```

Например получишь:

* `/root/.nvm/versions/node/v22.21.1/bin/node`
* `/root/.nvm/versions/node/v22.21.1/bin/npm`

## 2) Создай unit-файл

`/etc/systemd/system/mytube.service`

```ini
[Unit]
Description=MyTube (frontend+backend) via npm start
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mytube

# IMPORTANT: systemd does not load .bashrc, set PATH explicitly:
Environment=PATH=/root/.nvm/versions/node/v22.21.1/bin:/root/.deno/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=NODE_ENV=production

# Optional: increase file limits for downloads
LimitNOFILE=1048576

# Start MyTube (both services)
ExecStart=/root/.nvm/versions/node/v22.21.1/bin/npm run start -- --host 0.0.0.0

Restart=always
RestartSec=3

# Logs to journald
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

⚠️ Заменить `v22.21.1` на то, что реально у тебя в `which node/npm`.

## 3) Применить и запустить

```bash
systemctl daemon-reload
systemctl enable --now mytube.service
systemctl status mytube.service -l
```

## 4) Логи

```bash
journalctl -u mytube.service -f
```

## 5) Рестарт/стоп

```bash
systemctl restart mytube.service
systemctl stop mytube.service
```

---

# Быстрые проверки

```bash
ss -lntp | egrep ':(5551|5556)\s'
curl -I http://127.0.0.1:5556/ | head
curl -I http://127.0.0.1:5551/api/health 2>/dev/null || true
```

