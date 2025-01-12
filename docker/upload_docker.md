Для загрузки существующего Docker-образа в Docker Hub выполните следующие шаги:

---

### 1. **Войдите в Docker Hub**
Убедитесь, что у вас есть учётная запись на [Docker Hub](https://hub.docker.com/). Выполните вход в командной строке:

```bash
docker login
```

Вас попросят ввести ваш **логин** и **пароль**.

---

### 2. **Проверьте существующий образ**
Узнайте имя вашего рабочего образа:

```bash
docker images
```

Вы увидите что-то вроде:

```
REPOSITORY          TAG       IMAGE ID       CREATED          SIZE
amnezia-vpn         latest    abc123def456   10 minutes ago   300MB
```

В данном примере имя образа — `amnezia-vpn`, а тег — `latest`.

---

### 3. **Переименуйте образ для Docker Hub**
Docker Hub требует, чтобы имя образа включало ваш Docker Hub логин. Переименуйте ваш образ, если это нужно:

```bash
docker tag amnezia-vpn:latest <ваш_логин>/amnezia-vpn:latest
```

Пример, если ваш логин — `myusername`:

```bash
docker tag amnezia-vpn:latest myusername/amnezia-vpn:latest
```

---

### 4. **Загрузите образ в Docker Hub**
Теперь загрузите образ в Docker Hub:

```bash
docker push <ваш_логин>/amnezia-vpn:latest
```

Пример:

```bash
docker push myusername/amnezia-vpn:latest
```

---

### 5. **Проверьте в Docker Hub**
Зайдите на сайт [Docker Hub](https://hub.docker.com/), войдите в свою учётную запись и убедитесь, что ваш образ появился в списке репозиториев.

---

### 6. **Повторная установка образа**
Теперь, если вы захотите заново установить этот образ, выполните:

```bash
docker pull <ваш_логин>/amnezia-vpn:latest
```

Пример:

```bash
docker pull myusername/amnezia-vpn:latest
```

---

Готово! Теперь ваш образ доступен для загрузки с Docker Hub.
