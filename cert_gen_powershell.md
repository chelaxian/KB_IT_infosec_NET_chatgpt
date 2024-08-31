Для создания самоподписанного сертификата на веб-сайт, который будет использоваться для проверки подлинности сервера (SSL Server Authentication) и для проверки клиента (Client Authentication), с несколькими указанными DNS-именами в Windows с помощью PowerShell, нужно выполнить следующие команды:

### Шаг 1: Определение переменных

Определим переменные, чтобы сделать команду более читаемой:

```powershell
$certName = "WEB.DOMAIN.NET"
$dnsNames = @(
    "WEB.DOMAIN.NET",
    "*.DOMAIN.NET",
    "DOMAIN.NET"
)
```

### Шаг 2: Создание сертификата с помощью `New-SelfSignedCertificate`

Создадим самоподписанный сертификат с нужными DNS-именами:

```powershell
$cert = New-SelfSignedCertificate `
    -DnsName $dnsNames `
    -CertStoreLocation "Cert:\LocalMachine\My" `
    -FriendlyName $certName `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(10) `
    -Type SSLServerAuthentication
```

### Шаг 3: Экспорт сертификата в файл

Чтобы экспортировать созданный сертификат в формате PFX (PKCS#12) для дальнейшего использования, выполним команду:

```powershell
$pfxPassword = ConvertTo-SecureString -String "YourPasswordHere" -Force -AsPlainText

Export-PfxCertificate -Cert $cert -FilePath "C:\path\to\your\certificate.pfx" -Password $pfxPassword
```

Не забудьте заменить `"YourPasswordHere"` на надежный пароль и указать нужный путь для сохранения файла.

### Объяснение команд:

1. **New-SelfSignedCertificate** — Создает новый самоподписанный сертификат с заданными параметрами.
   - `-DnsName` — Список DNS-имен, для которых будет действовать сертификат.
   - `-CertStoreLocation` — Место хранения сертификата в системном хранилище.
   - `-FriendlyName` — Удобочитаемое имя сертификата.
   - `-KeyAlgorithm`, `-KeyLength`, `-HashAlgorithm` — Параметры алгоритма ключа и хэширования.
   - `-NotAfter` — Дата истечения срока действия сертификата.
   - `-Type` — Указывает, что сертификат предназначен для аутентификации SSL-сервера.

2. **Export-PfxCertificate** — Экспортирует созданный сертификат в файл PFX.
   - `-Cert` — Ссылка на сертификат, созданный в предыдущем шаге.
   - `-FilePath` — Путь, где будет сохранен файл PFX.
   - `-Password` — Пароль для защиты экспортированного сертификата.


---


Для создания самоподписанного сертификата, который будет использоваться только для проверки подлинности сервера (SSL Server Authentication) и не будет включать проверку клиента (Client Authentication), необходимо изменить параметр `-Type` в команде `New-SelfSignedCertificate`.

По умолчанию, `-Type` включает как `SSLServerAuthentication`, так и `ClientAuthentication`. Чтобы исключить проверку клиента, укажем только `SSLServerAuthentication`.

### Команды для создания сертификата только с проверкой подлинности сервера

```powershell
$certName = "WEB.DOMAIN.NET"
$dnsNames = @(
    "WEB.DOMAIN.NET",
    "*.DOMAIN.NET",
    "DOMAIN.NET"
)

# Шаг 2: Создание сертификата только для аутентификации сервера
$cert = New-SelfSignedCertificate `
    -DnsName $dnsNames `
    -CertStoreLocation "Cert:\LocalMachine\My" `
    -FriendlyName $certName `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -NotAfter (Get-Date).AddYears(10) `
    -Type SSLServerAuthentication
```

### Экспорт сертификата в файл

Экспорт сертификата в формате PFX (PKCS#12) для использования:

```powershell
$pfxPassword = ConvertTo-SecureString -String "YourPasswordHere" -Force -AsPlainText

Export-PfxCertificate -Cert $cert -FilePath "C:\path\to\your\certificate.pfx" -Password $pfxPassword
```

например:
```powershell
$pfxPassword = ConvertTo-SecureString -String "1" -Force -AsPlainText

Export-PfxCertificate -Cert $cert -FilePath "C:\certificate.pfx" -Password $pfxPassword
```

### Объяснение изменений:

- **`-Type SSLServerAuthentication`** — Указывает, что сертификат предназначен только для аутентификации SSL-сервера, и не будет использоваться для проверки подлинности клиента.

Теперь этот сертификат будет действовать только для проверки подлинности сервера без клиентской проверки. 

Если есть еще вопросы или нужны дополнительные пояснения, сообщи!
