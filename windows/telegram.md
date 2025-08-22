Судя по логам, проблема в том, что Telegram Desktop не может открыть каталог
<img width="1257" height="714" alt="image" src="https://github.com/user-attachments/assets/6ff93bfd-a0b7-4690-9635-9cd6ca32eb3f" />

C:/Users/chelaXian/AppData/Roaming/Telegram Desktop/tdata/working

для записи. Ошибка:
FATAL: Could not open … for writing!

Это типичная проблема прав доступа или повреждения профиля tdata.

---

при попытке удалить файл working - ошибка
<img width="329" height="202" alt="image" src="https://github.com/user-attachments/assets/dee3233f-0ed8-4412-bc96-cef75e48c0b5" />

---

лечение:

```powershell
Stop-Process -Name DTShellHlp -Force
ren "C:\Users\chelaXian\AppData\Roaming\Telegram Desktop\tdata\working" working_old
```
