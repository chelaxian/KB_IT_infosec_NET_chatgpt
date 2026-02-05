# Portable OpenSSH Server на Windows (Win64 ZIP, без установки, без админки)

Инструкция показывает, как поднять **OpenSSH-сервер (sshd)** из `OpenSSH-Win64.zip` “портативно”: всё лежит в одной папке, запускается вручную (не службой), ключи/конфиг — рядом. Также есть шаги по генерации ключей, исправлению прав на приватный ключ в Windows и подключению с другого ПК.

> Важно: по умолчанию `sshd` на Windows пытается брать конфиг/файлы из `%ProgramData%\ssh`, но мы будем запускать его с ключом `-f` и хранить всё в своей папке, чтобы не упираться в права. [web:57]

---

## 0) Требования

- Windows 10/11/Server (x64).
- На “серверной” машине у вас должен быть доступ к порту SSH (обычно 22) и он не должен быть занят.
- Админ-права **не требуются** для описанного portable-варианта, но политики организации могут завершать процессы при `Logoff` из RDP.

---

## 1) Скачать и распаковать Win32-OpenSSH

1. Открой [страницу релизов PowerShell/Win32-OpenSSH](https://github.com/powershell/win32-openssh/releases) и скачай `OpenSSH-Win64.zip`. [web:16]
2. Распакуй в папку, например:

```text
C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64
```

---

## 2) Подготовить конфиг `sshd_config` рядом с файлами

В каталоге OpenSSH выполни:

```bat
cd /d "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64"
copy /Y sshd_config_default sshd_config
```

Теперь отредактируй конфиг:

```bat
notepad "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\sshd_config"
```

### Минимальные правки в `sshd_config`

Добавь (или замени существующие) строки:

```text
# Хост-ключи будем хранить рядом с программой (portable)
HostKey C:/Users/YOUR-WIN-USER/Downloads/OpenSSH-Win64/ssh_host_ed25519_key
HostKey C:/Users/YOUR-WIN-USER/Downloads/OpenSSH-Win64/ssh_host_rsa_key
HostKey C:/Users/YOUR-WIN-USER/Downloads/OpenSSH-Win64/ssh_host_ecdsa_key

# PID-файл тоже рядом, чтобы не писать в ProgramData
PidFile C:/Users/YOUR-WIN-USER/Downloads/OpenSSH-Win64/sshd.pid

# Для ключевой аутентификации обычного пользователя
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

Про `AuthorizedKeysFile` и настройку OpenSSH на Windows см. документацию Microsoft. [web:57]  
Скрипты/стандартная логика Win32-OpenSSH часто завязаны на `%ProgramData%\ssh`, поэтому мы уводим критичные файлы в свою папку. [web:37]

---

## 3) Сгенерировать host keys (ключи сервера) в папке OpenSSH

В каталоге OpenSSH:

```bat
cd /d "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64"

.\ssh-keygen.exe -t ed25519 -N "" -f .\ssh_host_ed25519_key
.\ssh-keygen.exe -t rsa -b 3072 -N "" -f .\ssh_host_rsa_key
.\ssh-keygen.exe -t ecdsa -b 256 -N "" -f .\ssh_host_ecdsa_key
```

---

## 4) Запустить sshd вручную (portable)

### Вариант A: запуск в окне (удобно для отладки)

```bat
cd /d "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64"
.\sshd.exe -e -f "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\sshd_config"
```

Если нужно посмотреть подробный лог:

```bat
.\sshd.exe -ddd -e -f "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\sshd_config"
```

---

## 5) Настроить вход по ключу (без пароля)

### 5.1 На клиентском ПК (второй компьютер) сгенерировать ключ пользователя

На клиенте:

```bat
ssh-keygen -t ed25519
```

Появятся файлы:

```text
C:\Users\<you>\.ssh\id_ed25519
C:\Users\<you>\.ssh\id_ed25519.pub
```

Общий принцип работы `authorized_keys` стандартный для OpenSSH. [web:128]

### 5.2 На сервере добавить публичный ключ в `authorized_keys`

На сервере (под тем пользователем, под которым будет вход):

```bat
mkdir C:\Users\YOUR-WIN-USER\.ssh
type C:\Users\YOUR-WIN-USER\.ssh\id_ed25519.pub >> C:\Users\YOUR-WIN-USER\.ssh\authorized_keys
```

Если публичный ключ лежит на клиенте — просто скопируй содержимое `id_ed25519.pub` и вставь его в файл:

```text
C:\Users\YOUR-WIN-USER\.ssh\authorized_keys
```

---

## 6) Исправить права на приватный ключ на Windows (если ругается “too open”)

Если при подключении видишь:

```text
WARNING: UNPROTECTED PRIVATE KEY FILE!
Permissions ... are too open
```

Это связано с ACL/правами Windows на файл ключа. Типичный путь решения — ограничить доступ к приватному ключу (только текущий пользователь). [web:175]

### Вариант A: через скрипт Win32-OpenSSH (если он доступен)

В распакованном OpenSSH есть утилитные скрипты для фикса прав. [web:182]

Пример запуска (на клиенте, где лежит ключ):

```powershell
cd "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64"
powershell -NoProfile -ExecutionPolicy Bypass -File .\FixUserFilePermissions.ps1 -Confirm:$false
```

### Вариант B: вручную (через свойства файла)

1. ПКМ по `id_ed25519` → **Свойства** → **Безопасность**.
2. Убери доступ “всем/пользователям/группам”, оставь только своего пользователя (минимум чтение).
3. Повтори подключение.

---

## 7) Подключиться с другого ПК

Команда:

```bat
ssh -i "C:\Users\YOUR-WIN-USER\.ssh\id_ed25519" YOUR-WIN-USER@your.win-pc.ssh
```

---

## 8) Ярлык для подключения (клиент)

Создай ярлык на Windows и укажи в “Расположение объекта”:

```text
C:\Windows\System32\cmd.exe /k ssh -i "C:\Users\YOUR-WIN-USER\.ssh\id_ed25519" YOUR-WIN-USER@your.win-pc.ssh
```

`cmd /k` оставляет окно открытым, чтобы видеть ошибки. [web:209]

---

## 9) Ярлык для запуска sshd “в фоне” (сервер)

### 9.1 CMD-файл (без окна позже)

Создай:

`C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\run-sshd-bg.cmd`

```bat
@echo off
cd /d "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64"
"C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\sshd.exe" -e -f "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\sshd_config"
```

### 9.2 VBS-файл (запуск скрыто)

Создай:

`C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\run-sshd-bg.vbs`

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run Chr(34) & "C:\Users\YOUR-WIN-USER\Downloads\OpenSSH-Win64\run-sshd-bg.cmd" & Chr(34), 0, False
Set WshShell = Nothing
```

Параметр `0` запускает скрыто, `False` — не ждать завершения. [web:169]

Сделай ярлык на `run-sshd-bg.vbs` и запускай его.

> Важно про RDP: если у вас “выход из RDP” = `Logoff`, процессы пользователя могут быть завершены политикой. Для гарантированной работы “всегда” обычно нужна служба или задача планировщика с запуском вне интерактивной сессии (часто требует админа). [web:170][web:172]

---

## 10) Быстрая проверка

На сервере:

```bat
ssh 127.0.0.1
```

Или с клиента:

```bat
ssh -vvv -i "C:\Users\YOUR-WIN-USER\.ssh\id_ed25519" YOUR-WIN-USER@your.win-pc.ssh
```

Verbose-режим помогает диагностировать, на чём именно ломается подключение. [web:103]
