
# **Полная инструкция WireGuard + wgcf (ARM64) с нуля**

## **1️⃣ Устанавливаем зависимости**

```bash
sudo apt update
sudo apt install wireguard openresolv iproute2 iptables curl -y
```

* `wireguard` — VPN.
* `openresolv` — корректная работа `resolvconf`.
* `iproute2` — маршруты.
* `iptables` — NAT / LXC.
* `curl` — проверка IP.

---

## **2️⃣ Скачиваем и устанавливаем wgcf для ARM64**

```bash
# Скачиваем wgcf (ARM64)
wget https://github.com/ViRb3/wgcf/releases/download/v2.2.29/wgcf_2.2.29_linux_arm64 -O wgcf

# Делаем исполняемым
chmod +x wgcf

# Перемещаем в системный путь
sudo mv wgcf /usr/local/bin/
```

Проверяем версию:

```bash
wgcf --version
# должно показать: v2.2.29
```

Если не сработало, добавь `/usr/local/bin` в PATH:

```bash
export PATH=$PATH:/usr/local/bin
```

---

## **3️⃣ Регистрируемся и генерируем профиль**

```bash
# Регистрация в Cloudflare Warp
wgcf register

# Генерация конфигурации WireGuard
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

> ⚠️ Файл **с правами 600**, иначе `wg-quick` не сможет использовать.

---

## **5️⃣ Настройка resolv.conf для LXC / Debian**

В LXC `/etc/resolv.conf` обычно обычный файл, создаём симлинк:

```bash
sudo mv /run/resolv.conf /etc/resolv.conf.backup
sudo ln -s /run/resolvconf/resolv.conf /etc/resolv.conf
```

---

## **6️⃣ Настройка DNS вручную (опционально)**

Создаём базовый конфиг для resolvconf:

```bash
sudo mkdir /etc/resolvconf/
sudo nano /run/resolvconf/resolv.conf
```

Вставляем:

```
nameserver 1.1.1.1
nameserver 1.0.0.1
search one.one.one.one
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

## **7️⃣ Запуск wgcf и автозапуск**

```bash
sudo systemctl enable wg-quick@wgcf
sudo systemctl start wg-quick@wgcf
systemctl status wg-quick@wgcf
```

Проверяем внешний IP:

```bash
curl ifconfig.io
# должен отличаться от IP хоста
```

---

На хосте proxmox
```bash
iptables -t nat -A POSTROUTING -j MASQUERADE
iptables -t nat -L -n -v
```

