Давайте разберём по шагам, как понять, какой из трёх nginx отдаёт эту «502 Bad Gateway», и как добавить в ответ информацию-идентификатор инстанса.

---

### 1. Диагностика: кто именно отвечает?

1.1. Добавить HTTP‑заголовок с именем хоста в каждом nginx:

```nginx
http {
    # …ваши общие настройки…

    # в любой зоне (http, server или location):
    add_header X-Nginx-Instance $hostname always;
}
```

1.2. Перезапустить nginx и выполнить:

```bash
curl -I https://ваш-домен/secure/CreateIssue.jspa
```

– вы увидите в ответе что-то вроде:

```
HTTP/1.1 502 Bad Gateway
Server: nginx
X-Nginx-Instance: frontend-01
…
```

Так сразу станет ясно, какой именно сервер ответил.

---

### 2. Кастомизация страницы 502 и вкрапление информации

Есть несколько способов:

| Метод                                   | Конфиг                                                                                                                                                                                                                                                                                                      | Примечание                                                                    |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **1. Простое `return` с переменной**    | `nginx<br>error_page 502  =502  /@502; <br>location = /@502 { <br>  internal; <br>  default_type text/html; <br>  return 502 "<!DOCTYPE html><html><body><h1>502 Bad Gateway</h1><p>Instance: $hostname</p></body></html>";<br>} `                                                                          | Не требует внешних файлов, переменные разворачиваются прямо в теле.           |
                                                                                                                                                                      

---

Делаем встроенную 502‑шаблонку с нужными вам полями. Предположим, вы редактируете `server {…}` для вашего сайта:

```nginx
server {
    listen       80;
    server_name  example.com;

    # 1) Перехват 502 и редирект во внутренний location
    error_page 502 =502 /@502;

    # …ваши остальные location и proxy_pass…

    # 2) Внутренний обработчик 502  
    location = /@502 {
        internal;
        default_type text/html;

        # 3) Возвращаем страницу с Agent, IP и временем
        return 502
        "<!DOCTYPE html>
        <html>
          <head>
            <meta charset=\"utf-8\">
            <title>502 Bad Gateway</title>
          </head>
          <body style=\"font-family:Arial,sans-serif;\">
            <h1 style=\"color:#cc0000;\">502 Bad Gateway</h1>
            <ul>
              <li><strong>Agent:</strong> ptaf-agent</li>
              <li><strong>Server IP:</strong> $server_addr</li>
              <li><strong>Time:</strong> $time_local</li>
            </ul>
          </body>
        </html>";
    }
}
```

### Пояснения (по шагам)

1. **`error_page 502 =502 /@502;`**
   Перехватывает ответ от `proxy_pass`, меняет код на 502 и отдаёт запрос в ваш внутренний endpoint `/@502`.

2. **`location = /@502 { internal; … }`**
   — `internal` запрещает прямой доступ извне.
   — `default_type text/html` выставляет `Content-Type: text/html`.
   — `return 502 "<…>";` возвращает нужный код и тело страницы.

3. **Переменные nginx**

   * `$server_addr` — IP‑адрес интерфейса, который принял соединение.
   * `$time_local` — локальная дата и время в формате `16/Jul/2025:12:34:56 +0000`.
   * Текст `ptaf-agent` вставлен как Literal в шаблон.

### Дальнейшие шаги

1. Проверить синтаксис:

   ```bash
   sudo nginx -t
   ```
2. Перезагрузить конфиг:

   ```bash
   sudo systemctl reload nginx
   ```
3. Протестировать:

   ```bash
   curl -i http://example.com/your-broken-url
   ```

   — в теле вы увидите HTML со списком Agent, Server IP и Time.

---

## Шаг 4. Применение конфига (reload)

Поскольку у вас специфичный бинари `ptaf-nginx`, перезагрузим его «без даунтайма»:

```bash
sudo ptaf-nginx -s reload
```

Или, если предпочитаете systemd‑подход:

```bash
sudo systemctl reload ptaf-nginx
```

---

## Шаг 5. Проверка в реальном запросе

1. Вызываем URL, который раньше давал 502:

   ```bash
   curl -i http://<ваш_DNS_или_IP>/secure/CreateIssue.jspa
   ```

2. В заголовках вы увидите стандартный `Server: nginx`, но в теле (ниже строк `\r\n\r\n`) должно быть что-то вроде:

   ```html
   <!DOCTYPE html>
   <html>
     <head><meta charset="utf-8"><title>502 Bad Gateway</title></head>
     <body style="font-family:Arial,sans-serif;">
       <h1 style="color:#cc0000;">502 Bad Gateway</h1>
       <ul>
         <li><strong>Agent:</strong> ptaf-agent</li>
         <li><strong>Server IP:</strong> 10.20.30.40</li>
         <li><strong>Time:</strong> 17/Jul/2025:13:20:15 +0300</li>
       </ul>
     </body>
   </html>
   ```

   Где:

   * **Agent:** строка `ptaf-agent`
   * **Server IP:** результат переменной `$server_addr`
   * **Time:** результат `$time_local`

---

## Шаг 6. Если не отображается

1. Убедитесь, что вы редактировали именно тот файл, который загружается (в вашем выводе это `/opt/ptaf/conf/nginx.conf`).

2. Проверьте, что внутри того же `server { … }` нет другого `error_page 502`, перекрывающего ваш.

3. Попробуйте закэшированию помешать добавлением заголовка:

   ```nginx
   add_header Cache-Control no-store always;
   ```

   прямо внутри `location = /@502`.

4. Ещё раз перезапустите и смешайте:

   ```bash
   curl -H "Cache-Control: no-cache" -i http://<ваш_домен>/broken-path
   ```

---


