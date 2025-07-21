если при доступе через reverse proxy ошибка 400: Bad Request

нужно зайти в контейнер по пути /config/configuration.yaml

и дописать туда

```
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.30.33.6     #Remote LAN / proxy ip 
    - 192.168.1.XX    #Your Home assistant IP only
  ip_ban_enabled: true
  login_attempts_threshold: 5

And it works for me!
```
