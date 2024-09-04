Открыть powershell, вставить команды:

```powershell
$credential = Get-Credential
#ввести логин/пароль

$credential | Export-Clixml -Path "C:\Users\$env:USERNAME\Desktop\$env:USERNAME.xml"
```

Сохранить команды ниже как скрипт powershell `*.ps1`:
```powershell
# Импорт учетных данных из файла
$credential = Import-Clixml -Path "C:\Users\$env:USERNAME\Desktop\$env:USERNAME.xml"

# Запуск нового процесса PowerShell с заданными учетными данными
Start-Process -FilePath "powershell.exe" -Credential $credential -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-NoExit", "-Command", "cd C:\" -WindowStyle Normal

# Закрытие текущего окна PowerShell после запуска нового процесса
Stop-Process -Id $PID
```
Открыть powershell, перетащить в него файл `*.ps1`
