### Как создать файл или скрипт для проверки подключения к LDAP/LDAPS

Чтобы проверить работоспособность подключения к LDAP/LDAPS с вашими учетными данными, можно создать скрипт на PowerShell. Простой скрипт для этой цели может выглядеть следующим образом:

#### Шаг 1: Создание скрипта для проверки подключения

Создайте файл `Check-LDAPConnection.ps1` с таким содержимым:

```powershell
# Загрузка необходимой сборки
Add-Type -AssemblyName System.DirectoryServices.Protocols

# Запрос типа подключения (LDAP или LDAPS)
$connectionType = Read-Host "Введите тип подключения (LDAP или LDAPS)"

# Преобразование типа подключения в URL
if ($connectionType -eq "LDAP") {
    $server = Read-Host "Введите адрес LDAP сервера (например, yourdomain.com)"
    $port = 389 # стандартный порт для LDAP
} elseif ($connectionType -eq "LDAPS") {
    $server = Read-Host "Введите адрес LDAPS сервера (например, yourdomain.com)"
    $port = 636 # стандартный порт для LDAPS
} else {
    Write-Host "Неверный тип подключения. Пожалуйста, введите 'LDAP' или 'LDAPS'."
    exit
}

# Запрос имени пользователя
$username = Read-Host "Введите ваше имя пользователя (например, user@domain.com)"

# Запрос пароля с защитой ввода
$password = Read-Host "Введите ваш пароль" -AsSecureString

# Преобразование пароля в обычный текст (для использования в подключении)
$passwordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# Настройка подключения
try {
    # Импортируем библиотеку System.DirectoryServices.Protocols
    $ldapConnection = New-Object System.DirectoryServices.Protocols.LdapConnection("${server}:${port}")
    $ldapConnection.Credential = New-Object System.Net.NetworkCredential($username, $passwordPlain)
    $ldapConnection.AuthType = [System.DirectoryServices.Protocols.AuthType]::Basic

    # Проверяем подключение
    $ldapConnection.Bind()
    Write-Host "Соединение с $connectionType сервером $server успешно установлено."
} catch {
    Write-Host "Ошибка подключения к ${connectionType}: $_"
}

```

#### Шаг 2: Запуск скрипта

1. Сохраните этот файл на вашем компьютере (например, в `C:\Scripts\Check-LDAPConnection.ps1`).
2. Откройте PowerShell.
3. Перейдите в директорию, где сохранен скрипт, и запустите его:

   ```powershell
   cd C:\Scripts
   .\Check-LDAPConnection.ps1
   ```

Скрипт попытается подключиться к указанному серверу LDAP или LDAPS и выведет результат на экран.

### Заключение

Используйте приведенные команды и скрипт для проверки ваших учетных данных и соединения с LDAP/LDAPS сервером. Если у вас есть дополнительные вопросы или нужно внести изменения в скрипт, сообщите.


