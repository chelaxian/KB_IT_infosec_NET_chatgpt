Вот инструкция по установке **Nextcloud с поддержкой символических ссылок** в формате `Markdown`, полностью на русском языке.

---

## 📦 Установка Nextcloud с Docker, `.env`, `docker-compose.yml`, поддержкой симлинков и сканированием

### 🔧 1. Подготовка окружения

```bash
sudo mkdir -p ~/nextcloud
cd ~/nextcloud
```

Создай необходимые каталоги:

```bash
mkdir config data db
chmod 770 config data db
sudo chown -R 33:33 config data db
```

---

### 📁 2. Создание `.env`

Создай `.env` файл:

```env
MYSQL_ROOT_PASSWORD="СЛОЖНЫЙ_ПАРОЛЬ"
MYSQL_USER=nextcloud
MYSQL_PASSWORD="СЛОЖНЫЙ_ПАРОЛЬ"
MYSQL_DATABASE=nextcloud
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD="СЛОЖНЫЙ_ПАРОЛЬ"
NEXTCLOUD_TRUSTED_DOMAINS="localhost,nextcloud.example.local"
```

---

### ⚙️ 3. `docker-compose.yml`

Создай файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: mariadb:10.6
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - ./db:/var/lib/mysql
    networks:
      - nextcloud-net
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 3s
      retries: 10

  app:
    image: nextcloud
    restart: always
    ports:
      - 8080:80
    environment:
      MYSQL_HOST: db
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      NEXTCLOUD_ADMIN_USER: ${NEXTCLOUD_ADMIN_USER}
      NEXTCLOUD_ADMIN_PASSWORD: ${NEXTCLOUD_ADMIN_PASSWORD}
      NEXTCLOUD_TRUSTED_DOMAINS: ${NEXTCLOUD_TRUSTED_DOMAINS}
    volumes:
      - ./config:/var/www/html/config
      - ./data:/var/www/html/data
    depends_on:
      db:
        condition: service_healthy
    networks:
      - nextcloud-net

networks:
  nextcloud-net:
    driver: bridge
```

---

### 🔗 4. Символическая ссылка и каталог

Создай внешний каталог, например, на отдельном разделе:

```bash
sudo mkdir -p /mnt/vps_shared/chelaxian_files
sudo chown -R 33:33 /mnt/vps_shared/chelaxian_files
sudo chmod 770 /mnt/vps_shared/chelaxian_files
```

Создай симлинк внутри `./data/chelaxian/files/`:

```bash
mkdir -p ./data/chelaxian/files
ln -s /mnt/vps_shared/chelaxian_files ./data/chelaxian/files/GlusterFS
```

---

### 🚀 5. Запуск контейнеров

```bash
docker compose up -d
```

---

### 🛠 6. Включение поддержки символических ссылок

После первого запуска **отредактируй `config/config.php`**:

```php
<?php
$CONFIG = array (
  ...
  'installed' => true,
  'localstorage.allowsymlinks' => true,
);
```

⚠️ Проверь, что параметр добавлен внутри массива `$CONFIG`.

Перезапусти контейнер:

```bash
docker compose restart app
```

---

### 🔍 7. Сканирование файлов вручную

Для пользователя `chelaxian`:

```bash
docker exec -u www-data -it nextcloud_app_1 php occ files:scan --path="chelaxian/files/GlusterFS"
```

Полное сканирование:

```bash
docker exec -u www-data -it nextcloud_app_1 php occ files:scan --all
```

---

### ✅ Проверка

Файлы в `/mnt/vps_shared/chelaxian_files` должны появиться в веб-интерфейсе Nextcloud в папке `GlusterFS`.

Если не видно — убедись, что:

* права на каталог `770`, владелец `www-data:www-data`
* `config.php` содержит `'localstorage.allowsymlinks' => true`
* `occ files:scan` завершился без ошибок

---

