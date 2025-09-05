Полная инструкция **с нуля для ARM, с `wgcf`, регистрацией, генерацией профиля, настройкой DNS и автозапуском**. 

---

# **Полная инструкция для WireGuard + wgcf на ARM**

## **1️⃣ Устанавливаем зависимости**

```bash
sudo apt update
sudo apt install wireguard openresolv iproute2 iptables curl -y
```

* `wireguard` — сам VPN.
* `openresolv` — для корректной работы `resolvconf`.
* `iproute2` — маршруты.
* `iptables` — для NAT / LXC.
* `curl` — проверка IP.

---

## **2️⃣ Устанавливаем wgcf для ARM64**

```bash
# Скачиваем последнюю версию wgcf
wget https://github.com/ViRb3/wgcf/releases/download/v2.2.29/wgcf_2.2.29_linux_arm64 -O wgcf
chmod +x wgcf
sudo mv wgcf /usr/local/bin/
```

Проверяем:

```bash
wgcf --version
# должно показать v2.2.29
```

---

## **3️⃣ Регистрируемся и генерируем профиль**

```bash
# Регистрируемся в Cloudflare Warp
wgcf register

# Генерируем конфигурацию WireGuard
wgcf generate
```

После генерации появится файл `wgcf-profile.conf`.

---

## **4️⃣ Копируем профиль в /etc/wireguard**

```bash
sudo mkdir -p /etc/wireguard
sudo cp wgcf-profile.conf /etc/wireguard/wgcf.conf
sudo chmod 600 /etc/wireguard/wgcf.conf
```

* Файл **обязательно с правами 600**, иначе `wg-quick` ругается.

---

## **5️⃣ Настраиваем симлинк для resolv.conf**

В LXC `/etc/resolv.conf` часто обычный файл, нужно заменить на симлинк:

```bash
sudo mv /etc/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/resolvconf/resolv.conf /etc/resolv.conf
```

---

## **6️⃣ Настройка DNS вручную (если нужно)**

Создаём файл `/etc/resolvconf/resolv.conf.d/base`:

```bash
sudo nano /etc/resolvconf/resolv.conf.d/base
```

Содержимое:

```
nameserver 1.1.1.1
nameserver 1.0.0.1
search one.one.one.one
```

Применяем:

```bash
sudo resolvconf -u
```

Проверяем:

```bash
cat /etc/resolv.conf
# должно быть:
# nameserver 1.1.1.1
# nameserver 1.0.0.1
# search one.one.one.one
```

---

## **7️⃣ Запуск wgcf и проверка**

```bash
sudo systemctl enable wg-quick@wgcf
sudo systemctl start wg-quick@wgcf
systemctl status wg-quick@wgcf
```

Проверяем внешний IP:

```bash
curl ifconfig.io
# должен отличаться от IP хоста, трафик идёт через Warp
```

---

## **8️⃣ Проверка маршрутов и интерфейса**

```bash
ip a show wgcf
ip route show
```

* Интерфейс `wgcf` должен быть `up`.
* IP-адреса совпадают с теми, что в `wgcf.conf`.

---

