Ок, давай соберём пошаговую **чистую инструкцию**, как полностью решить проблему с ошибкой

**"To make SSL VPN connection work, please turn off IE Security Configuration"** в **FortiClient VPN** на Windows Server.

---

## 📌 Почему возникает ошибка

* FortiClient SSL VPN на Windows Server использует компоненты **Internet Explorer / WinHTTP**.
* На серверных ОС (2012R2/2016/2019/2022) включён режим **IE Enhanced Security Configuration (IE ESC)**.
* Этот режим блокирует подключение FortiClient, поэтому нужно его отключить.

---

## 🛠 Решение пошагово

### 1. Проверить версию FortiClient

* Если стоит **FortiClient ZTNA/Zero Trust Agent** — оставляем только модуль **VPN (Standalone)**.
* Скачивание: [официальный Fortinet сайт](https://www.fortinet.com/support/product-downloads).

---

### 2. Отключить IE ESC через PowerShell

Создай файл `ie_sec_off.ps1` со следующим содержимым:

```powershell
<# 
Disable IE Enhanced Security Configuration (IE ESC)
for Administrators and Users on Windows Server
#>

# Проверка на права администратора
If (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "Запусти PowerShell от имени администратора!"
    exit 1
}

Write-Host "Отключаю IE Enhanced Security Configuration (IE ESC)..." -ForegroundColor Cyan

# Выключить ESC для администраторов
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}" -Name IsInstalled -Value 0

# Выключить ESC для пользователей
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}" -Name IsInstalled -Value 0

Write-Host "IE ESC отключен. Перезапусти FortiClient VPN." -ForegroundColor Green
```

Запусти PowerShell **от имени администратора** и выполни:

```powershell
.\ie_sec_off.ps1
```

---

### 3. Проверить, что IE ESC отключён

Выполни команды:

```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}" | Select-Object IsInstalled
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}" | Select-Object IsInstalled
```

Оба значения должны быть `0`.

---

### 4. Перезайти в систему (или просто перезапустить FortiClient)

После этого подключение VPN должно работать без ошибки.

---

## 🔄 (Опционально) Включить IE ESC обратно

Если понадобится вернуть настройки безопасности:

```powershell
# Включить ESC для администраторов
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}" -Name IsInstalled -Value 1

# Включить ESC для пользователей
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}" -Name IsInstalled -Value 1
```

---

## ✅ Итог

1. Устанавливаем **FortiClient VPN Standalone**.
2. Через PowerShell отключаем **IE Enhanced Security Configuration** (ключи Active Setup `{A509B1A7}` и `{A509B1A8}`).
3. Проверяем значения `IsInstalled=0`.
4. Перезапускаем FortiClient и подключаемся к VPN — ошибка исчезает.

---

Хочешь, я соберу это в один готовый `.ps1`, который умеет и отключать, и включать ESC по параметру (`-Disable` / `-Enable`)?
