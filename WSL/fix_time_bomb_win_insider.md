
## 1️⃣ Проверка текущей сборки и состояния WSL

Открой **PowerShell от администратора** и выполни:

```powershell
# Версия Windows
winver          # откроется окно с номером сборки

# Версия WSL и ядра
wsl --version

# Статус дистрибутивов
wsl --list --verbose

# Проверка служб Hyper-V и WSL
Get-Service vmms,vmcompute,LxssManager | Select Name,Status
```

Ожидаем, что `Status` у всех трёх служб — `Running`.
Если нет, запускаем:

```powershell
Start-Service vmms,vmcompute,LxssManager
```

---

## 2️⃣ Временный «фикс» с системной датой

⚠️ Это только костыль, он не чинит просроченные сертификаты, а лишь отматывает дату для проверки подписи.

### Установка даты на несколько дней назад

Например, на 10 сентября 2025 г.:

```powershell
Set-Date -Date "2025-09-10 10:06:00"
#Set-Date -Date "YYYY-MM-DD HH:MM:SS"
```

После выполнения:

```powershell
Get-Date     # убедиться, что дата изменилась
```

Теперь можно запустить WSL:

```powershell
wsl --shutdown
wsl
```

---

## 3️⃣ Автоматизация при каждом старте (по желанию)

Если нужно, чтобы дата выставлялась автоматически при загрузке:

1. Создать файл `C:\Scripts\set-date.ps1` со строкой:

   ```powershell
   Set-Date -Date "2025-09-10 10:06:00"
   ```
2. Добавить задачу в Планировщик:

   ```powershell
   schtasks /create /tn "SetSystemDate" /tr "powershell -ExecutionPolicy Bypass -File C:\Scripts\set-date.ps1" /sc onstart /ru SYSTEM
   ```

---

## 4️⃣ Возврат текущей даты

Когда закончишь работу с WSL, верни дату обратно:

```powershell
Set-Date -Date (Get-Date)  # если часы не синхронизируются — включи NTP
```

или включи авто-синхронизацию:

```powershell
w32tm /resync
```

---

## 5️⃣ Контроль после фикса

Каждый раз можно проверить:

```powershell
wsl --status
Get-Date
```

---

### ⚠️ Важные замечания

* Этот способ нужен только как **временное решение**, пока не сделан переход на стабильную или свежую Insider-ветку.
* При любом обновлении Windows дата автоматически синхронизируется, и WSL снова перестанет стартовать — придётся повторить `Set-Date`.

---

Таким образом:

1. Проверяешь сборку (`winver`), службы и WSL.
2. Отматываешь дату `Set-Date`.
3. Работаешь с WSL.
4. При необходимости возвращаешь реальную дату `w32tm /resync`.

---

Можно реализовать требуемую автоматизацию через две задачи в планировщике: одна меняет дату до запуска WSL и сервисов, а вторая возвращает дату через 5 минут. Обе задачи должны запускаться с максимальным приоритетом раньше прочих сервисных задач.

***

### Как сделать две связанные задачи через Планировщик:

#### 1️⃣ Задача для сброса даты (запустится первой):

Сначала создайте скрипт, например, `C:\Scripts\pre-wsl-date.ps1`:
```powershell
Set-Date -Date "2025-09-10 10:06:00"
```

Создайте задачу с опережающим запуском, используя `schtasks`:
```powershell
schtasks /create /tn "PreWSLSetDate" /tr "powershell -ExecutionPolicy Bypass -File C:\Scripts\pre-wsl-date.ps1" /sc onstart /ru SYSTEM /rl HIGHEST
```
Такой запуск `/sc onstart` под SYSTEM и с уровнем привилегий Highest даст приоритет по запуску перед пользовательскими задачами и прочими задачами, стартующими после входа пользователя.[1][2]

#### 2️⃣ Задача для возврата даты (через 5 минут):

Создайте второй скрипт, например, `C:\Scripts\restore-date.ps1`:
```powershell
w32tm /resync
# или, для ручного возврата
# Set-Date -Date (Get-Date)
```
Создайте отложенную задачу ― запуск через 5 минут после загрузки:
```powershell
schtasks /create /tn "RestoreSystemDate" /tr "powershell -ExecutionPolicy Bypass -File C:\Scripts\restore-date.ps1" /sc once /st 00:05 /ru SYSTEM /rl HIGHEST /delay 0000:05
```
**ВАЖНО:** Параметр `/delay 0000:05` работает при `onstart`, либо используйте повторяемую задачу (например, по времени или запуск из самой первой задачи через `Start-Sleep 300; ...`). Альтернативно, совместите оба действия в одном скрипте с задержкой:

```powershell
# C:\Scripts\pre-wsl-date.ps1
Set-Date -Date "2025-09-10 10:06:00"
Start-Sleep -Seconds 300
w32tm /resync
```
***

### Схема работы:
- Скрипт изменяет дату, ждёт 5 минут (300 сек) и возвращает дату/выполняет ресинхронизацию.
- Задача добавляется как системная, с приоритетом HIGHEST и триггером `/sc onstart`, чтобы всегда идти первой.[2][1]

***

### Перепроверьте логику запуска:
- В расписании обеих задач задайте «Запускать с наивысшими привилегиями» (Highest).
- Задачи должны быть выше всех пользовательских (если используете SYSTEM, запускаются до входа пользователя).

***

### Пример для комплексного сценария (один скрипт):

`schtasks /create /tn "PreWSL-SetDateRestore" /tr "powershell -ExecutionPolicy Bypass -File C:\Scripts\pre-wsl-date.ps1" /sc onstart /ru SYSTEM /rl HIGHEST`

***

### Итог:

- Первая задача всегда самая ранняя по запуску — SYSTEM, onstart, highest.
- Возврат даты через 5 минут обеспечивается либо второй задачей с отложенным запуском, либо через задержку в первом скрипте.[1][2]
- Запускать такие задачи только под администратором (SYSTEM), иначе не будет прав на смену времени.

***

**Обратите внимание:** изменение системной даты Повлияет на все процессы, запущенные после старта, пока не будет выполнен возврат или ресинхронизация времени.

Вот корректный скрипт PowerShell, который сначала откатывает дату, затем запускает службы WslInstaller и WSLService, а через 5 минут возвращает/синхронизирует системное время:

```powershell
# Откат времени на нужную дату
Set-Date -Date "2025-09-10 10:06:00"

# Настройка и запуск службы WslInstaller
sc.exe config WslInstaller start= auto
sc.exe start WslInstaller

# Настройка и запуск службы WSLService
sc.exe config WSLService start= auto
sc.exe start WSLService

# Ждём 5 минут (300 секунд), чтобы службы и WSL успели корректно стартовать
Start-Sleep -Seconds 300

# Возврат актуальной даты/синхронизация
w32tm /resync
# или, если отключён NTP:
# Set-Date -Date (Get-Date)
```

Этот скрипт выполняет:
- Откат даты перед запуском служб
- Настройку и старт нужных сервисов
- Задержку (5 минут)
- Возврат или синхронизацию даты после старта всех сервисов и WSL.[1][2]

[1](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc725744(v=ws.11))
[2](https://blog.netwrix.com/how-to-automate-powershell-scripts-with-task-scheduler)
[17](https://www.reddit.com/r/PowerShell/comments/z5f0x6/is_there_any_way_to_run_script_run_after_each/)
[18](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/increase-scheduling-priority)
[19](https://www.reddit.com/r/sysadmin/comments/17ana7v/how_to_set_priority_on_windows_scheduled_task/)
[20](https://www.blackfog.com/knowledge-base/how-to-run-powershell-scripts-at-startup/)
