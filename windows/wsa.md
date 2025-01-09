## 1. Install WSA 

prepare WSA distro from https://github.com/LSPosed/MagiskOnWSALocal

## 2. Install WSA 

run install script

```powershell
PS I:\WSA_VHD\MagiskOnWSALocal\output\WSA_2303.40000.5.0_x64_Release-Nightly-with-magisk-26.1(26100)-stable-MindTheGapps-13.0> .\Run.bat
```

## 3. Remove WSA 

If you want to remove WSA run

```powershell
Get-AppxPackage *Android* | Select-Object Name, PackageFullName
Get-AppxPackage *Android* | Remove-AppxPackage
```
или
```powershell
Get-AppxPackage MicrosoftCorporationII.WindowsSubsystemForAndroid | Remove-AppxPackage
```

## 4. Location of WSA files

`userdata.vhdx`
`C:\Users\chelaxian\AppData\Local\Packages\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalCache`

## 5. Resize WSA disk

1. Полностью завершить WSA
2. В powershell с правами администратора выполнить:
```powershell
Resize-VHD -Path "C:\Users\[юзер]\AppData\Local\Packages\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalCache\userdata.vhdx" -SizeBytes [нужный размер]
```
или
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All -NoRestart
```
```powershell
Resize-VHD -Path "C:\Users\chelaxian\AppData\Local\Packages\MicrosoftCorporationII.WindowsSubsystemForAndroid_8wekyb3d8bbwe\LocalCache\userdata.2.vhdx" -SizeBytes 34359738368
```

## 6. Create symbol link to WSA disk

Use software `Link Shell Extension`
https://windowstips.ru/link-shell-extension-utilita-dlya-bystrogo-sozdaniya-zhestkix-i-simvolnyx-ssylok-v-windows
