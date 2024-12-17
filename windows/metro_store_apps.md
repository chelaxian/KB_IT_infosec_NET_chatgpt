```
Сбой установки приложения. Сообщение об ошибке: AppxManifest.xml (322, 10): ошибка 0x80070005: не удается зарегистрировать пакет AppleInc.iTunes_12134.4.3008.0_x64__nzyj5cx40ttqa, так как при регистрации расширения windows.fileTypeAssociation произошла следующая ошибка: Отказано в доступе.
. Повторите попытку и обратитесь к издателю пакета, если проблема повторится. (0x80070005)
```

Ошибка 0x80070005 обычно связана с проблемами доступа, когда операционная система не может выполнить операцию из-за недостаточных прав. В данном случае ошибка возникает при попытке регистрации расширения `windows.fileTypeAssociation` для приложения iTunes. Чтобы решить эту проблему, попробуйте следующие шаги:
  
### 1. Попробуйте использовать сторонний установщик
- В случае, если стандартный установщик продолжает выдавать ошибку, можно попробовать скачать установочный файл iTunes через официальный сайт Apple или использовать альтернативные способы установки через **Microsoft Store** или сторонние пакеты.

### 2. Переустановите Windows Store (если ошибка возникла через него)
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
