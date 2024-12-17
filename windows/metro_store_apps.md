```
Сбой установки приложения. Сообщение об ошибке: AppxManifest.xml (322, 10): ошибка 0x80070005: не удается зарегистрировать пакет AppleInc.iTunes_12134.4.3008.0_x64__nzyj5cx40ttqa, так как при регистрации расширения windows.fileTypeAssociation произошла следующая ошибка: Отказано в доступе.
. Повторите попытку и обратитесь к издателю пакета, если проблема повторится. (0x80070005)
```

Ошибка 0x80070005 обычно связана с проблемами доступа, когда операционная система не может выполнить операцию из-за недостаточных прав. В данном случае ошибка возникает при попытке регистрации расширения `windows.fileTypeAssociation` для приложения iTunes. Чтобы решить эту проблему, попробуйте следующие шаги:

### 1. Запустите установку от имени администратора
- Попробуйте запустить установку приложения iTunes с правами администратора.
  1. Найдите установочный файл iTunes.
  2. Щелкните правой кнопкой мыши по файлу и выберите **Запуск от имени администратора**.

### 2. Проверьте наличие необходимых разрешений
- Убедитесь, что у вас есть права на запись в папки, связанные с установкой приложения. Это могут быть:
  - **C:\Program Files**
  - **C:\Program Files (x86)**
  
  Если прав недостаточно, попробуйте изменить права на эти каталоги или запустить установку в другой директории.

### 3. Отключите антивирус или защитник Windows
- В некоторых случаях антивирусное ПО или Защитник Windows могут блокировать установку приложений. Попробуйте временно отключить их и повторить установку.
  1. Отключите Защитник Windows:
     - Перейдите в **Настройки** → **Обновление и безопасность** → **Безопасность Windows** → **Защита от вирусов и угроз** → **Управление настройками** → **Отключить реальное время защиты**.
  2. Отключите сторонний антивирус, если он установлен.

### 4. Проверьте системные файлы с помощью SFC и DISM
- Выполните проверку целостности системных файлов с помощью командной строки:
  1. Откройте **Командную строку от имени администратора**.
  2. Выполните команду:
     ```
     sfc /scannow
     ```
  3. После завершения сканирования и исправления ошибок, выполните команду для восстановления образа Windows:
     ```
     DISM /Online /Cleanup-Image /RestoreHealth
     ```
  4. Перезагрузите компьютер и попробуйте снова установить приложение.

### 5. Проверьте права на ключи реестра
- Иногда ошибка может быть вызвана недостаточными правами на ключи реестра, связанные с установкой приложений.
  1. Откройте редактор реестра: нажмите **Win + R**, введите `regedit` и нажмите Enter.
  2. Перейдите по пути:
     ```
     HKEY_CLASSES_ROOT\Local Settings\Software\Microsoft\Windows\CurrentVersion\Uninstall
     ```
  3. Убедитесь, что у вас есть права на редактирование в этом разделе.
  
### 6. Попробуйте использовать сторонний установщик
- В случае, если стандартный установщик продолжает выдавать ошибку, можно попробовать скачать установочный файл iTunes через официальный сайт Apple или использовать альтернативные способы установки через **Microsoft Store** или сторонние пакеты.

### 7. Переустановите Windows Store (если ошибка возникла через него)
- Иногда ошибка может быть связана с повреждением самого магазина приложений Windows.
  1. Откройте **PowerShell от имени администратора**.
  2. Выполните команду:
     ```
     Get-AppxPackage *Microsoft.WindowsStore* | Remove-AppxPackage
     ```
  3. После этого перезагрузите систему и установите магазин снова:
     ```
     Get-AppxPackage -allusers Microsoft.WindowsStore | foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}
     ```

Если проблема сохранится после выполнения этих шагов, возможно, потребуется обратиться в службу поддержки Apple или Microsoft для более глубокой диагностики.

---

Чтобы установить iTunes через PowerShell, можно воспользоваться командой для установки приложения из **Microsoft Store**, если оно доступно в нем. Вот как это сделать:

1. **Откройте PowerShell с правами администратора**:
   - Нажмите **Win + X** и выберите **Windows PowerShell (администратор)**.

2. **Введите следующую команду для установки iTunes через Microsoft Store**:
   ```powershell
   Get-AppxPackage -AllUsers | Where-Object {$_.Name -like "*iTunes*"} | Remove-AppxPackage
   ```

   Если вы хотите скачать и установить iTunes непосредственно через Microsoft Store, воспользуйтесь командой:

   ```powershell
   Get-AppxPackage *iTunes* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}
   ```

Этот способ работает, если у вас уже есть приложение iTunes в магазине Windows.

---


```cmd
C:\Users\chelaxian>powershell                                                                                           Windows PowerShell                                                                                                      Copyright (C) Microsoft Corporation. All rights reserved.                                                                                                                                                                                       Install the latest PowerShell for new features and improvements! https://aka.ms/PSWindows

PS C:\Users\chelaxian> Get-AppxPackage *Microsoft.WindowsStore* | Remove-AppxPackage
PS C:\Users\chelaxian> Get-AppxPackage -allusers Microsoft.WindowsStore | foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}
PS C:\Users\chelaxian> Get-AppxPackage -AllUsers | Where-Object {$_.Name -like "*iTunes*"} | Remove-AppxPackage
PS C:\Users\chelaxian> Get-AppxPackage *iTunes* | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register "$($_.InstallLocation)\AppXManifest.xml"}
```
