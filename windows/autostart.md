
📌 **Запланированная задача (`schtasks`)**

---

### 🔧 **Шаги для создания запланированной задачи**
Выполните в `PowerShell` (запустите с правами администратора):

```powershell
$taskAction = New-ScheduledTaskAction -Execute "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Scripts\start-wsl.ps1"
$taskTrigger = New-ScheduledTaskTrigger -AtStartup
$taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DontStopOnIdleEnd
Register-ScheduledTask -TaskName "StartWSL" -Description "Запуск WSL при старте системы" -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -User "SYSTEM" -RunLevel Highest
```

### ✅ **Проверка**
После выполнения команды откройте `Планировщик заданий`:
1. **Win + R** → введите `taskschd.msc` и нажмите `Enter`
2. В левой панели откройте **Библиотека планировщика заданий**.
3. Найдите задачу **StartWSL**.
4. Убедитесь, что триггер стоит **При запуске**.
5. Вручную запустите задачу правым кликом → **Выполнить**.

После перезагрузки скрипт будет автоматически выполняться.

💡 **Выбор метода:**
- `New-Service` не сработает, так как требует `.exe`.
- `schtasks` более гибкий и подходит для таких задач.

---

## 🔹 **2. Автозапуск EXE-файла с параметрами через сервис Windows**
Если требуется запуск `.exe` с параметрами, то можно задать `binPath` напрямую.

### **📌 Шаги**:
Допустим, нам нужно запускать `C:\Program Files\SomeApp\app.exe` с параметрами `--config C:\config.json --log C:\logfile.log`.

1. Выполните команду в `cmd.exe` от имени администратора:
   ```cmd
   sc create MyAppService binPath= "\"C:\Program Files\SomeApp\app.exe\" --config C:\config.json --log C:\logfile.log" start= auto
   sc description MyAppService "Запуск MyApp с параметрами"
   sc start MyAppService
   ```

2. **Проверка**:
   ```cmd
   sc query MyAppService
   ```

✅ Теперь при загрузке Windows будет автоматически запускаться `app.exe` с заданными параметрами.

---

* служба Windows требует работающий процесс в фоне. `cmd.exe` не работает в таком режиме, поэтому для BAT-скриптов используется **утилита NSSM** (Non-Sucking Service Manager), которая позволяет запускать скрипты как службы.

---

## 🔥 **Решение через NSSM (РЕКОМЕНДУЕТСЯ)**  
### 📌 **1. Установка NSSM**
1. Скачай `nssm.exe` с официального сайта:  
   👉 [https://nssm.cc/download](https://nssm.cc/download)
2. Разархивируй и скопируй `nssm.exe` в `C:\Windows\System32` **(или добавь его путь в `PATH`)**.

---

### 📌 **2. Создание службы через NSSM**
Запусти `cmd.exe` от **администратора** и выполни:

```cmd
nssm install StartWSL
```

Появится графическое окно конфигурации:
- **Path**: `C:\Windows\System32\cmd.exe`
- **Arguments**: `/c C:\Scripts\start-wsl.bat`
- **Startup type**: `Automatic`

Нажми **"Install service"**.

---

### 📌 **3. Запуск службы**
```cmd
sc start StartWSL
```

Теперь служба `StartWSL` будет автоматически запускаться при загрузке Windows.

### 📌 **4. Проверка службы**
```cmd
sc query StartWSL
```
---

## 🚀 **Преимущества NSSM**
✅ **Работает стабильно** (не падает с ошибкой `1053`).  
✅ **Логирует ошибки** (в `Event Viewer`).  
✅ **Поддерживает автоматический рестарт** в случае падения.  

