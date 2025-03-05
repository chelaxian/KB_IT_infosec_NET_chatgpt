Чтобы pipx запускался из любого места без перезагрузки Windows, нужно добавить в переменную PATH директорию, в которую установлены его скрипты. В вашем случае это:

```
C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts
```

Ниже привожу пошаговые рекомендации:

1. **Обновление PATH для текущей сессии командной строки**  
   Выполните в командной строке команду:
   ```batch
   set PATH=%PATH%;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts
   ```
   Это добавит путь в переменную PATH только для текущего окна командной строки. После этого команда `pipx` будет доступна до закрытия сессии.

2. **Постоянное добавление пути**  
   Если вы хотите, чтобы данный путь сохранялся и в новых сеансах командной строки, можно воспользоваться командой:
   ```batch
   setx PATH "%PATH%;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts"
   ```
   Обратите внимание, что команда `setx` не обновляет переменную PATH в уже открытых окнах. Новые окна будут уже с обновлённым значением.

3. **Обновление PATH в текущей сессии без перезагрузки**  
   Если вы изменили переменную PATH с помощью `setx` и хотите, чтобы изменения вступили в силу в текущей сессии, можно использовать утилиту `refreshenv`, которая входит в состав [Chocolatey](https://chocolatey.org/) (или аналогичный скрипт). Для этого:
   - Установите Chocolatey (если ещё не установлен).
   - После выполнения `setx` запустите команду:
     ```batch
     refreshenv
     ```
     Это обновит переменные окружения в текущей командной строке без необходимости её закрывать и открывать заново.

---

```cmd
C:\Users\Administrator>setx PATH "%PATH%;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts"

WARNING: The data being saved is truncated to 1024 characters.

SUCCESS: Specified value was saved.
```

---

Ниже приведу пошаговую инструкцию по очистке переменной PATH, чтобы оставить только необходимые каталоги для корректного запуска pipx (и, возможно, Python):

> **Важно!** Перед изменениями обязательно сохраните текущий PATH, чтобы в случае ошибок можно было его восстановить.

### 1. Определите минимальный набор путей
Для работы pipx (и корректного функционирования Windows) обычно достаточно следующих директорий:
- **Системные каталоги Windows:**
  - `C:\Windows\system32`
  - `C:\Windows`
  - `C:\Windows\System32\Wbem`
  - `C:\Windows\System32\WindowsPowerShell\v1.0\`
  - (опционально) `C:\Windows\System32\OpenSSH\` – если вы используете SSH-клиент
- **Каталог с pipx:**
  - `C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts`

Если вы активно пользуетесь Python (например, запускаете другие скрипты или утилиты), возможно, вам понадобится оставить и:
- `C:\Python310\Scripts`
- `C:\Python310\`

### 2. Сформируйте новый минимальный PATH

Пример минимального PATH для pipx (без учёта Python, если он не нужен):
```
C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts
```

Если Python вам нужен, добавьте его:
```
C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Python310\Scripts;C:\Python310\;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts
```

### 3. Обновление PATH в текущей сессии
Откройте командную строку и выполните:
```batch
set PATH=C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts
```
Это изменение действует только в текущем окне.

### 4. Постоянное изменение PATH
Чтобы обновлённый PATH сохранился в новых сеансах, можно использовать команду `setx`. Поскольку новый PATH не превышает 1024 символов, ограничение не будет проблемой:
```batch
setx PATH "C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Users\Administrator\AppData\Roaming\Python\Python310\Scripts"
```
После выполнения этой команды, чтобы изменения вступили в силу в текущей сессии, выполните:
```batch
refreshenv
```
Если у вас установлены Chocolatey или аналогичный инструмент.

### 5. Проверка работоспособности
После обновления PATH выполните команду:
```batch
pipx --version
```
Если pipx запускается – значит, изменения применились корректно.

---

Если вы сомневаетесь, какие именно каталоги вам нужны, или если какие-то программы стали недоступны после очистки PATH, можно дополнительно добавить их в переменную через диалог «Переменные среды Windows»:

1. Нажмите **Win+R**, введите `SystemPropertiesAdvanced` и нажмите Enter.
2. Нажмите кнопку **Переменные среды**.
3. В разделе «Переменные пользователя» выберите переменную PATH и нажмите **Изменить**.
4. Удалите ненужные записи, оставив только проверенные (как указано выше).
5. Сохраните изменения.

---


