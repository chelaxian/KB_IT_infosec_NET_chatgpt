## PTAF AGENT в качестве балансировщика (перед PTAF PRO)

Вот такой базовый конфиг можно использовать для настройки **PTAF AGENT** в качестве балансировщика (перед **PTAF**)

```nginx
master_process on;
# Количество рабочих процессов необходимо подбирать с учетом аппаратной конфигурации сервера: числа процессоров, количества ядер и потоков (hyper threading).
# Не указывайте больше восьми процессов во избежание потери событий безопасности.
worker_processes 1;
# Запуск nginx в режиме демона. Для внешнего агента необходимо значение on, для пода Kubernetes или контейнера — off
daemon on;

worker_rlimit_nofile 1048576;

# (Начало) Путь установки PT AF
load_module /opt/ptaf/lib/ngx_wrapper.so;
# (Конец) Путь установки PT AF

# Уровень журналирования nginx. Возможные значения: debug, info, notice, warn, error, crit, alert, emerg
error_log stderr error;

# (Начало) Переменные окружения модуля ptaf-core. Возможны изменения/добавления при необходимости
env PTAF_LOG_LEVEL=INFO;
env DEBUG=false;
env POD_IP=127.0.0.1;
env HOSTNAME=localhost;
# (Конец) Переменные окружения модуля ptaf-core. Возможны изменения/добавления при необходимости

events {
  worker_connections 64000;
  accept_mutex off;
}

http {
  # (Начало) Строка для подключения агента к PT AF
  #ptaf_config tcp://<example_config_string>;
  # (Конец) Строка для подключения агента к PT AF

  real_ip_header X-Forwarded-For;
  set_real_ip_from 0.0.0.0/0; # Разрешаем извлечение IP из любого источника
  real_ip_recursive on;       # Для обработки цепочки прокси

  include mime.types;
  default_type application/octet-stream;
  client_max_body_size 1g;
  sendfile on;
  gzip on;
  log_not_found off;
  proxy_pass_header Server;
  server_names_hash_bucket_size 512;
  access_log off;
  # (Начало) Определение поведения сервера при ошибках обработки трафика. Значение по умолчанию — pass
  ptaf_fallback 503;
  # (Конец) Определение поведения сервера при ошибках обработки трафика
  server_tokens off;
  proxy_read_timeout 60s;
  proxy_send_timeout 60s;
  send_timeout 60s;
  keepalive_timeout 75s;
  keepalive_requests 1000;
  proxy_buffer_size 8k;
  proxy_buffers 8 8k;
  proxy_busy_buffers_size 16k;
  proxy_connect_timeout 60s;

  geo $dollar {
    default "$";
  }

  # (Начало) Настройка HTTP Upgrade для протокола WSS (WebSockets)
  map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
  }
  # (Конец) Настройка HTTP Upgrade для протокола WSS (WebSockets)

  # (Начало) Защищаемые серверы
  upstream backend_app_1 {
    server 192.168.0.1:30001 weight=1 max_fails=1;
    keepalive_timeout 60s;
    keepalive 32;
    transparent ntlm;
  }
  upstream backend_app_2 {
    server 192.168.0.1:30002 weight=1 max_fails=1;
    keepalive_timeout 60s;
    keepalive 32;
    transparent ntlm;
  }
  # (Конец) Защищаемые серверы

  # (Начало) Принятие незащищенных соединений
  server {
    listen 192.168.0.2:80 backlog=65536;
    server_name _;

    # Редирект с HTTP на HTTPS
    return 301 https://$host$request_uri;
  }
  # (Конец) Принятие незащищенных соединений

  # (Начало) Принятие защищенных соединений
  server {
    listen 192.168.0.2:443 ssl backlog=65536;
    server_name 
        example1.local
        example2.local
        example3.local;

    ssl_certificate /certs/fullchain_example.pem;
    ssl_certificate_key /certs/private_example.key;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_protocols TLSv1.2;

    location / {
        set $upstream_name "";

        if ($host = "example1.local") { set $upstream_name backend_app_1; }
        if ($host = "example2.local") { set $upstream_name backend_app_2; }

        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_pass https://$upstream_name;

        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Connection "";
        proxy_set_header Upgrade $http_upgrade;
        proxy_pass_header Date;
        proxy_pass_header Server;
        proxy_ssl_server_name on;
        proxy_ssl_name $ssl_server_name;
        proxy_ssl_protocols TLSv1.2 TLSv1.3;
        proxy_ssl_ciphers ALL:@SECLEVEL=0;
        proxy_ssl_verify on;
        proxy_ssl_verify_depth 1;
        proxy_ssl_trusted_certificate /certs/root+intermediate_example.crt;
    }
  }

  # Блок для health-check
  server {
      listen 8080;
      server_name 192.168.0.2;

      location /health/1 {
          proxy_pass http://192.168.0.1:31001/healthz;
          proxy_set_header Host $host;
      }
      location /health/2 {
          proxy_pass http://192.168.0.1:31002/healthz;
          proxy_set_header Host $host;
      }
  }
  # (Конец) Принятие защищенных соединений
}
```
[скрипт для упрощенного масштабирования и тиражирования бэкендов в конфиг NGINX](https://github.com/chelaxian/KB_IT_infosec_NET_chatgpt/blob/main/PT/PTAF/update_nginx_conf.py)
