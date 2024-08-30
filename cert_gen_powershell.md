Для создания самоподписанного сертификата на веб-сайт с указанными DNS-именами в Windows с помощью PowerShell, нужно выполнить следующие команды:

### Шаг 1: Определение переменных

Определим переменные, чтобы сделать команду более читаемой:

```powershell
$certName = "mdgkd-pam-test"
$dnsNames = @(
    "mdgkd-pam-test-linux.int.kronshtadt.ru",
    "mdgkd-pam-test.int.kronshtadt.ru",
    "mdgkd-pam-test-linux",
    "mdgkd-pam-test",
    "int.kronshtadt.ru",
    "*.int.kronshtadt.ru"
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
    -NotAfter (Get-Date).AddYears(1) `
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

Если нужно что-то еще уточнить или дополнить, дай знать!
