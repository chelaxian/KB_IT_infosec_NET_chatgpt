В Windows можно обновить переменную окружения **PATH** без перезагрузки ПК несколькими способами:

---

### **1. Обновление PATH в текущей сессии PowerShell**
Если ты установил **Node.js**, но команды `node`, `npm`, `npx` не работают, можно обновить PATH прямо в PowerShell:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
```
После этого **новые пути будут доступны в текущем окне PowerShell**.

Если хочешь, чтобы переменная обновилась во всех новых окнах терминала, запусти команду:
```powershell
refreshenv
```
Но эта команда работает только если установлен **Chocolatey**. Если нет, используй **способы 2 и 3**.

---

### **2. Применение нового PATH в командной строке (CMD)**
В `cmd.exe` можно выполнить:
```cmd
set PATH=%PATH%;C:\Program Files\nodejs\
```
**Недостаток**: изменения действуют только в текущем окне терминала.

Чтобы обновить PATH глобально в запущенных процессах:
```cmd
setx PATH "%PATH%;C:\Program Files\nodejs\"
```
⚠️ **Важно**: `setx` перезаписывает переменную PATH, удаляя временные изменения.

---

### **3. Применение нового PATH через Windows API**
Этот метод позволяет обновить переменные окружения во всех новых процессах **без выхода из системы**:

1. Открой **PowerShell** от имени администратора.
2. Запусти команду:
```powershell
$EnvPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
[System.Environment]::SetEnvironmentVariable("Path", $EnvPath, "Process")
```
3. Теперь новые пути должны работать во всех вновь открытых окнах терминала.

---

### **4. Принудительное обновление PATH через WMI**
Этот вариант обновляет переменные окружения во всех новых процессах **без выхода из системы**:

```powershell
$code = '[DllImport("user32.dll")] public static extern bool SendMessageTimeout(int hWnd, int Msg, int wParam, int lParam, int fuFlags, int uTimeout, out int lpdwResult);'
Add-Type -MemberDefinition $code -Name "Win32SendMessageTimeout" -Namespace "Win32Functions"
[Win32Functions.Win32SendMessageTimeout]::SendMessageTimeout(0xffff, 0x1A, 0, 0, 2, 5000, [ref]0)
```

Этот метод **применяет переменные окружения ко всем новым процессам**, но не затрагивает уже запущенные.

---

### **Вывод**
- Для текущего терминала:  
  **PowerShell:** `$env:Path = ...`  
  **CMD:** `set PATH=...`
- Для всех новых окон терминала:  
  **PowerShell:** `refreshenv` (если есть Chocolatey)
- Для всех новых процессов **без выхода из системы**:  
  **PowerShell:** `[System.Environment]::SetEnvironmentVariable(...)`
- Для принудительного обновления **без выхода из системы**:  
  **PowerShell:** `SendMessageTimeout()`

Готово! Теперь `node`, `npm`, `npx` и другие команды должны работать без полного пути. 🚀
