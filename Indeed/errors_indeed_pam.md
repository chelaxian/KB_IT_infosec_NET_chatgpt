## Ошибки на этапе Start PAM and healthcheck

Ошибки на этапе `90#Start PAM and healthcheck` означают, что компоненты успешно установлены, но не удалось выполнить проверку работоспособности компонентов по какой-либо из причин.

Диагностика:

1. Выполняем попытку перехода в консоль администратора (`https://fqdn_management_server/mc`).

2. Если консоль не открывается или появляется форма аутентификации в PAM выполняем следующую команду на сервере управления:

```

sudo docker ps -a

```

Команда выведет состояние всех контейнеров на хосте. Проверяем у каких контейнеров установлен статус `Exited` (`pam-ca-certificates` - сервисный контейнер, должен быть в статусе `Exited`) - проверяем логи данных компонентов в директории.

---

## Проблемы с LDAPS соединением с доменом

Все проверки выполняются с Linux серверов.



Curl 
Команда для проверки:

```

username - Имя учетной записи для чтения каталога

local.test - Имя домена

curl ldaps://local.test --cacert /etc/indeed/indeed-pam/ca-certificates/ca.crt -u username@local.test

```

Если при выполнении команды, есть ошибки, то попробовать выполнить запрос на конкретный контроллер домена:

```

dc.1.local.test - FQDN имя контроллера домена

curl ldaps://dc.1.local.test --cacert /etc/indeed/indeed-pam/ca-certificates/ca.crt -u username@local.test

```

Если выполнение проверки, к конкретным контроллерам выполняется успешно, а по общему имени ошибка, это значит, что сертификат используемый для LDAPS не содержит общего имени домена.



LDAPSearch 
Команда для проверки:

```

env LDAPTLS_CACERT=/etc/indeed/indeed-pam/ca-certificates/ca.crt ldapsearch -x -LLL -H ldaps://local.test  -D pamread@local.test  -W  -b "dc=local,dc=test"

```

Openssl
Команда для проверки c сервера управления:

```

local.test - Имя домена

openssl s_client -connect local.test:636 -CAfile /etc/indeed/indeed-pam/ca-certificates/ca.crt

```

---

## LogServer remote server returned an error (500)

В логах ошибка следующего содержания:

```

2025-07-02 20:04:50.2903|1|FATAL|Indeed.LogServer.Program|Stopped program because of exception System.Security.Cryptography.CryptographicException: The key {[ключ шифрования]} was not found in the key ring. For more information go to https://aka.ms/aspnet/dataprotectionwarning

```

В консоли администратора:

<img width="286" height="188" alt="image" src="https://github.com/user-attachments/assets/ac81bd53-3657-47a7-a96a-d0c5414acbf2" />



Не удаётся расшифровать только конфигурационный файл LogServer.



Алгоритм решения:

1. Выполнить расшифровку конфигурационных файлов командой:

```

.\Pam.Tools.Configuration.Protector.exe unprotect

```

   Будет ошибка следующего характера:

```

Error: The key {protector_key} was not found in the key ring. For more information go to https://aka.ms/aspnet/dataprotectionwarning

```

2. Заменить зашифрованное значение в конфигурационном файле LogServer, на строку подключения к БД:

   `C:\inetpub\wwwroot\ls\targetConfigs\Pam.DbTarget.config`

   Пример:

```

Server=[FQDNorIPaddressBD];Database=[NameBD];User Id=[Username];Password=[Password];TrustServerCertificate=False

```

   Заполненную строку можно взять из конфигурационных файлов Core или Idp, но заменить наименование БД на используемое для компонента LogServer (по умолчанию в мастере конфигурации значение ILS)

3. Выполнить повторное шифрование конфигурационных файлов:

```

.\Pam.Tools.Configuration.Protector.exe protect

```

4. Перезапустить IIS чтобы изменения вступили в силу.
<img width="378" height="278" alt="image" src="https://github.com/user-attachments/assets/28afee4d-317f-4856-84b2-d4c387456996" />

---

## Name or service not known (ls 5080)

При переходе на вкладку "События" отображается ошибка:

Can not read scheme config from server

	Name or service not known (ls:5080)

		Name or service not known (ls:5080)

			Name or service not known



Проверьте логи компонента LogServer:

- Linux:

  /etc/indeed/indeed-pam/logs/ls/

- Windows:

  C:\inetpub\wwwroot\ls\Logs\



Ошибка:

  Exception data:

    Severity: FATAL

    SqlState: 28000

    MessageText: no pg_hba.conf entry for host "192.168.213.204", user "IPAMSQLReadOps", database "LS", no encryption

    File: auth.c

    Line: 540

    Routine: ClientAuthentication



Решение:

Проверить файл pg_hba.conf, внести необходимые правки и выполнить применение изменений.

---

## The supplied credential is invalid.

В логах ошибка:

/etc/indeed/indeed-pam/logs/idp/
C:\inetpub\wwwroot\idp\logs\
```

2025-07-16 16:22:31.7353|65|ERROR|Microsoft.AspNetCore.Diagnostics.ExceptionHandlerMiddleware|An unhandled exception has occurred while executing the request.|Indeed.UserCatalog.Interfaces.UserCatalogException: Failed to get users  

---> System.DirectoryServices.Protocols.LdapException: The supplied credential is invalid.

```

Ошибка означает, что учетные данные для чтения каталога пользователей не корректны.

Выполните расшифровку конфигурационных файлов командой:

```

sudo bash /etc/indeed/indeed-pam/tools/protector.sh unprotect

```

Перейдите в конфигурационный файл idp:

```

/etc/indeed/indeed-pam/idp/appsettings.json

```

Найдите секцию **UserCatalog** и проверьте логин и пароль учетной записи для чтения каталога пользователей (логин должен быть в UPN формате, пример: username@domain.local).

После внесения и сохранения изменений проверьте секцию **UserCatalog** в конфигурационном файле Core:

```

/etc/indeed/indeed-pam/core/appsettings.json

```

По завершению редактирования конфигурационных файлов выполните шифрование:

```

sudo bash /etc/indeed/indeed-pam/tools/protector.sh protect

```

И перезагрузите контейнеры сервера управления:

```

sudo bash /etc/idneed/indeed-pam/scripts/run-pam.sh

```

Выполните повторную попытку входа в консоль администратора.

---

## Исключение при вызове .ctor с 1 аргументами

Диагностика:

В логе Deploy ошибка следующего содержания:

```

stderr: |-

    Write-BaseLog : 2025-06-23 10:03:36 |

    *************************************************************************************

    *  Failed: Deployment error occurred: Исключение при вызове ".ctor" с "1" аргументами: "Invalid parameter "

    *************************************************************************************

    At C:\Users\vkrotov\AppData\Local\Temp\win-deploy\scripts\logger.psm1:41 char:5

    +     Write-BaseLog -inputMessage $logMessage -isError $true

    +     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        + CategoryInfo          : NotSpecified: (улыбаюсь [Write-Error], WriteErrorException

        + FullyQualifiedErrorId : Microsoft.PowerShell.Commands.WriteErrorException,Write-BaseLog

```

При выполнении команды в PowerShell от имени администратора:

`Get-RDSessionCollection`

ошибка воспроизводится.



Решение:

В файле `C:\Windows\System32\WindowsPowerShell\v1.0\Modules\RemoteDesktop\SessionDesktopCollection.psm1` заменить значение 520 строки с:

```

$scope = New-Object System.Management.ManagementScope("\\" + $ConnectionBroker + "\" + $wmiNamespace, $connectionOptions)

```

На:

```

$msuri = "\\" + $ConnectionBroker + "\" + $wmiNamespace

$scope = New-Object System.Management.ManagementScope($msuri, $connectionOptions)

```

Запустить deploy повторно.



Подготовка к редактированию:

1. Щёлкните правой кнопкой мыши на файле SessionDesktopCollection.psm1.  

2. Выберите Свойства → вкладка Безопасность.  

3. В разделе Security выберите Advanced (Дополнительно).  

4. Временно измените владельца файла на вашего пользователя.  

5. Нажмите Change permissions (Изменить разрешения).  

6. Выдайте права на изменение файла локальным администраторам.



Действия после редактирования файла:

1. Уберите выданные права на изменения файла.  

2. Верните прежнего владельца файла (NT SERVICE\TrustedInstaller).

---

## Отсутствие пути в реестре.

При запуске установки компонентов PAM на Windows Server возникает ошибка:

```

  attempts: 1

  cmd: powershell -ExecutionPolicy bypass -File .\\run-win-deploy.ps1 -Roles "role" -ServerFQDN "FQDN_server" -pfxPassword "PFX_password" -LogVerbose 3 -Clean true

  delta: '0:00:12.718705'

  end: '2025-06-20 12:43:30.616095'

  failed_when_result: true

  msg: non-zero return code

  rc: 1

  start: '2025-06-20 12:43:17.897389'

  stderr: |-

    Write-BaseLog : 2025-06-20 05:43:30 |

    *************************************************************************************

    *  Failed: Deployment error occurred: 2025-06-20 05:43:30 |

    *************************************************************************************

    *  Failed: Registry path is NOT found: HKLM:\SOFTWARE\Classes\Installer\Products

    *************************************************************************************

    *************************************************************************************

    At C:\Users\fedor\AppData\Local\Temp\win-deploy\scripts\logger.psm1:41 char:5

    +     Write-BaseLog -inputMessage $logMessage -isError $true

    +     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        + CategoryInfo          : NotSpecified: (улыбаюсь [Write-Error], WriteErrorException

        + FullyQualifiedErrorId : Microsoft.PowerShell.Commands.WriteErrorException,Write-BaseLog

  stderr_lines: <omitted>

  stdout: |-

```

Варианты решения:

1. Выполнить инсталляцию любого msi файла;

2. Создать данный путь (`HKLM:\SOFTWARE\Classes\Installer\Products`) в реестре самостоятельно.

