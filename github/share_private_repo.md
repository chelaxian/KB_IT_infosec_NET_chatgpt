# Настройка приватного репозитория GitHub и проксирования через Nginx Proxy Manager

## 1. Создание приватного репозитория на GitHub
1. Перейдите на [GitHub](https://github.com/) и авторизуйтесь.
2. Создайте новый репозиторий со сложным, длинным и не говорящим именем, установив **Private** (Приватный).
3. Создайте сложную и вложенную структуру папок для дополнительной маскировки (например `artifact/blob` )
4. Добавьте файлы, которые хотите хранить в репозитори в папку (или подпапку) внутри `artifact/blob`.

## 2. Создание персонального токена доступа (GitHub PAT)
1. Перейдите в настройки GitHub: [Settings](https://github.com/settings/profile).
2. Перейдите в **Developer settings** → **Personal access tokens** → **Tokens (classic)**.
3. Нажмите **Generate new token (classic)**.
4. Укажите **expiration** (срок действия токена) по желанию.
5. Выберите необходимые **scopes (разрешения)**:
   - `repo` (Full control of private repositories)
6. Нажмите **Generate token**.
7. Скопируйте токен и сохраните его в надежном месте (он не будет доступен повторно).

## 3. Настройка Nginx Proxy Manager (OpenResty)
### 3.1 Установка Nginx Proxy Manager

Если у вас еще не установлен Nginx Proxy Manager (NPM), установите его через Docker:
```sh
mkdir -p ~/nginx-proxy-manager && cd ~/nginx-proxy-manager
cat <<EOF > docker-compose.yml
version: '3'
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      - '80:80'
      - '81:81'
      - '443:443'
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
EOF

docker-compose up -d
```
После запуска Nginx Proxy Manager будет доступен по адресу `http://<your-server-ip>:81`.

### 3.2 Добавление прокси-хоста для GitHub файлов
1. Перейдите в веб-интерфейс Nginx Proxy Manager (`http://<your-server-ip>:81`).
2. Авторизуйтесь (по умолчанию: `admin@example.com` / `changeme`).
3. В разделе **Hosts** выберите **Proxy Hosts** → **Add Proxy Host**.
4. Введите **Domain Name** (например, `files.yourdomain.com`).
5. В разделе **Forward Hostname/IP** укажите `raw.githubusercontent.com`.
6. В разделе **Forward Port** установите `443` (HTTPS).
7. Включите **Websockets Support**.
8. Перейдите на вкладку **Custom Locations** и добавьте:
   - **Location**: `/files/`
   - **Scheme**: `https`
   - **Forward Hostname/IP**: `raw.githubusercontent.com`
   - **Forward Port**: `443`
   - В разделе **Advanced** вставьте:
     ```nginx
     proxy_set_header Authorization "token YOUR_GITHUB_PAT";
     proxy_set_header Host raw.githubusercontent.com;
     rewrite ^/files/(.*)$ /your-username/342f768432fv84f8567f34/refs/heads/main/artifact/blob/$1 break;
     proxy_ssl_server_name on;
     proxy_ssl_protocols TLSv1.2 TLSv1.3;
     proxy_ssl_verify on;
     proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
     ```
9. Нажмите **Save**.

### 3.3 Настройка SSL
1. В разделе **SSL** выберите **Request a new SSL Certificate**.
2. Введите свой домен (например, `files.yourdomain.com`).
3. Включите **Force SSL** и **HTTP/2 Support**.
4. Выберите **Let's Encrypt**, укажите email и согласитесь с условиями.
5. Нажмите **Save**.

## 4. Проверка работы
Теперь ваш закрытый репозиторий доступен через ваш сервер. Попробуйте открыть:
```
https://files.yourdomain.com/files/path/to/file.txt
```
Замените `path/to/file.txt` на реальный путь к файлу в репозитории.

---

Теперь ваш закрытый репозиторий GitHub доступен через Nginx Proxy Manager с защитой через GitHub API Token.

