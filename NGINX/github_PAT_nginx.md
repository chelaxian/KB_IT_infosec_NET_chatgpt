### Краткая пошаговая инструкция по настройке реверс-прокси для доступа к приватным raw-файлам на GitHub через **Nginx Proxy Manager (NPM)**

---

### Часть 1. Настройка GitHub для получения Personal Access Token (PAT)

1. **Войдите в аккаунт GitHub**:
   - Перейдите на [GitHub](https://github.com) и выполните вход.

2. **Откройте настройки токена**:
   - Перейдите в **Settings** (нажмите на аватарку в правом верхнем углу).
   - Внизу бокового меню выберите **Developer settings** > **Personal Access Tokens** > **Fine-grained tokens**.

3. **Создайте новый токен**:
   - Нажмите **Generate new token**.
   - Укажите название токена, например, `PrivateRepoAccess`.
   - Установите срок действия (например, 90 дней или без ограничений).
   - Выберите репозиторий, для которого нужен доступ:
     - В разделе **Repository access** выберите `Only select repositories` и укажите нужный приватный репозиторий.
   - В разделе **Permissions** выберите:
     - **Contents: Read-only** (для доступа к файлам).

4. **Сохраните токен**:
   - Нажмите **Generate token**.
   - Скопируйте токен (формат: `github_pat_xxxxxxxxxxxxxxxxxxxxxx`). Вы его больше не увидите, если не сохраните.

5. **Проверьте доступ**:
```cmd
curl -H "Authorization: token github_pat_1111111111111111111111_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
https://raw.githubusercontent.com/chelaxian/xxxxxxxxxxx/refs/heads/main/README.md
```

---

### Часть 2. Настройка Nginx Proxy Manager (NPM)

#### 1. **Добавьте новый Proxy Host**:
1. Войдите в веб-интерфейс **Nginx Proxy Manager**.
2. Нажмите **Add Proxy Host**.
3. Заполните поля:
   - **Domain Names**: Введите домен, например, `redirect.ratu.sh`.
   - **Forward Hostname/IP**: Укажите `raw.githubusercontent.com`.
   - **Forward Port**: Укажите `443` (HTTPS).
   - Включите **Websockets Support** и **Block Common Exploits**.
   - Установите галочку **Force SSL**.

4. Перейдите на вкладку **SSL**:
   - Выберите **Request a new SSL certificate**.
   - Установите галочки для **Force SSL** и **HTTP/2 Support**.
   - Нажмите **Save**.

---

#### 2. **Добавьте Custom Nginx Configuration**:
1. Откройте созданный Proxy Host и перейдите в **Advanced > Custom Nginx Configuration**.
2. Вставьте следующую конфигурацию:

```nginx
location /github {
    proxy_set_header Authorization "token github_pat_xxxxxxxxxxxxxxxxxxxxxx";
    proxy_set_header Host raw.githubusercontent.com;

    # Прокидывает путь после /github в запрос к GitHub
    rewrite ^/github/(.*)$ /chelaxian/KB_IT_infosec_NET_chatgpt/main/$1 break;

    proxy_pass https://raw.githubusercontent.com;
    proxy_ssl_server_name on;
    proxy_ssl_protocols TLSv1.2 TLSv1.3;
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
}

```

или в более простом варианте

```nginx
location /xxxxxx {
    proxy_set_header Authorization "token github_pat_1111111111111111111111_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
    proxy_set_header Host raw.githubusercontent.com;

    proxy_pass https://raw.githubusercontent.com/chelaxian/xxxxxxxxxxx/refs/heads/main/README.md;

    proxy_ssl_server_name on;
    proxy_ssl_protocols TLSv1.2 TLSv1.3;
    proxy_ssl_verify on;
    proxy_ssl_trusted_certificate /etc/ssl/certs/ca-certificates.crt;
}
```

---

### Часть 3. Тестирование
1. Перезапустите контейнер NPM:
   ```bash
   docker restart <npm_container_name>
   ```
2. Проверьте доступ:
   - Откройте в браузере: `https://redirect.ratu.sh/github/README.md`.
   - Вы должны увидеть содержимое файла `README.md` из приватного репозитория.

---

### Часть 4. Важные замечания
1. **Безопасность**:
   - Токен остаётся скрытым, так как используется только в заголовке `Authorization`.
2. **Обновление токена**:
   - При истечении срока действия токена замените его в конфигурации.
3. **Динамические файлы**:
   - Путь `/github/<FILENAME>` можно использовать для доступа к любому файлу в репозитории.

Теперь ваш реверс-прокси настроен и готов к работе! Если что-то не получится — напишите!
