### 🔧 Что нужно изменить в настройках CasaOS

#### ✅ Шаг 1: Проброс устройства iGPU

- Найди блок **"Устройства"** (внизу на втором скрине).
- Нажми `+ Добавить`.
- В поле укажи:
  ```
  /dev/dri/renderD128
  ```
- После добавления ты должен увидеть строку с устройством `/dev/dri/renderD128`.

> 💡 **Опционально**: если будет требоваться — добавь и `/dev/dri/card0`

---

#### ✅ Шаг 2: Сделай контейнер привилегированным

- В том же блоке ниже есть переключатель **"Привилегированный"** — включи его (переведи в активное положение).
- Это даст контейнеру дополнительные права и устранит часть проблем с доступом к GPU.

---

#### ✅ Шаг 3: Установка переменной окружения (если понадобится)

**Если после всех изменений `vainfo` внутри контейнера продолжит падать с `va_openDriver() = -1`**, добавь переменную окружения:

- Нажми `+ Добавить` в разделе **"Переменные окружения"**
- Ключ:
  ```
  LIBVA_DRIVER_NAME
  ```
- Значение:
  ```
  radeonsi
  ```

---

#### ✅ Шаг 4: Сохранить и перезапустить контейнер

- Нажми **Сохранить** внизу страницы.
- CasaOS пересоздаст контейнер (может спросить, сохранить или нет текущие тома — согласись).
- Проверь через интерфейс Jellyfin → `Playback` → `Hardware Acceleration`, что VAAPI доступна и включена.

---

### 📋 Проверь в самом Jellyfin

После запуска:

1. Перейди в Web UI Jellyfin: `http://casaos.local:8096`
2. Войди в настройки администратора
3. Открой: **Playback → Hardware Acceleration**
4. Включи:
   - [x] **Hardware acceleration**
   - [x] VAAPI
   - Укажи путь к устройству:
     ```
     /dev/dri
     #/dev/dri/card0
     #/dev/dri/renderD128
     ```

1. **Пробросить полный каталог `/sys/class/drm` из хоста в контейнер.**

   В настройках CasaOS для контейнера Jellyfin нужно добавить том (volume), который будет монтировать каталог `/sys/class/drm` с хоста в контейнер (рекомендуется в режиме «только для чтения»). Это обеспечит, что драйвер (radeonsi или amdgpu) сможет прочитать всю информацию о подключённых устройствах и их статус.

2. **Убедиться, что контейнер запущен в привилегированном режиме.**

   Многие функции DRM требуют полного доступа к sysfs и cgroup. Если контейнер не привилегированный, даже проброшенный sysfs может быть недостаточным.

     
5. Сохрани и перезапусти Jellyfin (можно прямо в интерфейсе).

---

### ✅ Проверка, что работает

После включения и воспроизведения любого видео:
- Зайди в **Dashboard → Activity → Playback**, проверь, что **транскодирование активно**.
- Также в `Logs` можно найти записи об использовании VAAPI (например: `VAAPI: Using device /dev/dri/renderD128`).

---

Ты всё сделал абсолютно правильно — на скриншотах видно, что Jellyfin распознал устройство `/dev/dri/renderD128` и включена поддержка VAAPI. Ниже — финальный чеклист, что всё настроено корректно, а также как **убедиться, что transcoding действительно происходит через iGPU**.

---

## ✅ Проверка и финальная донастройка Jellyfin

### 1. 🔧 Что ты уже правильно настроил:

- **Аппаратное ускорение:** VAAPI выбрано.
- **Устройство VAAPI:** указано `/dev/dri/renderD128` — ✅ правильно.
- **Декодеры включены:** H.264, HEVC 10bit и VC1 — ✅ подходящие профили для большинства видео.
- **Аппаратное кодирование включено:** опция активна — ✅
- **Путь к ffmpeg указан:** `/usr/lib/jellyfin-ffmpeg/ffmpeg` — ✅ стандартный путь для Jellyfin на базе `linuxserver/jellyfin`

---

## 🧪 Проверка, что Jellyfin действительно использует iGPU

### Способ 1: Логи Jellyfin

1. Перейди в **Панель управления → События или Журнал сервера**.
2. Запусти воспроизведение файла, требующего перекодирования (например, H.264 в HEVC).
3. В логах ищи строчки типа:
   ```
   [FFmpeg] Using VAAPI device /dev/dri/renderD128
   [VAAPI] Hardware decode/encode started
   ```
   Это — железобетонное подтверждение, что используется аппаратное ускорение.

---

### Способ 2: Прямой замер через терминал (если всё-таки нужно)

Если у тебя открыт root-доступ в CasaOS:

```bash
watch -n 1 cat /sys/kernel/debug/dri/0/amdgpu_pm_info
```

Там можно увидеть загрузку VCN (видео-ядра AMD), что доказывает, что iGPU задействован.

---

### 4. ⛔ Контейнер всё ещё не "видит" полноценный GPU стек

Если после всего вышеуказанного `vainfo` всё ещё возвращает `va_openDriver() = -1`, возможно, контейнеру не хватает:

- либо **привилегий** (`--privileged` не включен),
- либо **udev-правил/CGROUP доступа**.

📌 **Решение**: в CasaOS включи:

- переключатель **"Привилегированный контейнер"**
- проброси **и `/dev/dri/card0`, и `/dev/dri/renderD128`** в разделе **"Устройства"**

---

## ✅ Что делать прямо сейчас (шаги)

1. Внутри контейнера выполни:

```bash
chgrp video /dev/dri/renderD128
chmod 660 /dev/dri/renderD128
usermod -aG video jellyfin
#
apt update && apt upgrade -y
apt install -y mesa-va-drivers libva-drm2 libdrm-amdgpu1 libdrm2 vainfo xvfb
#
Xvfb :0 &
export DISPLAY=:0
export LIBVA_NO_DISPLAY=1
export LIBVA_DRIVER_NAME=radeonsi
export LIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
export XDG_RUNTIME_DIR=/tmp/xdg
mkdir -p $XDG_RUNTIME_DIR && chmod 700 $XDG_RUNTIME_DIR
vainfo --display drm --device /dev/dri/renderD128
ls -l /dev/dri
```

2. Проверь вывод. Если `vainfo` начнёт показывать поддерживаемые профили (H264, HEVC...), всё заработало.
```
root@46a3c8bc9414:/# vainfo --display drm --device /dev/dri/renderD128
libva info: VA-API version 1.20.0
libva info: User environment variable requested driver 'radeonsi'
libva info: Trying to open /usr/lib/x86_64-linux-gnu/dri/radeonsi_drv_video.so
libva info: Found init function __vaDriverInit_1_20
libva info: va_openDriver() returns 0
vainfo: VA-API version: 1.20 (libva 2.12.0)
vainfo: Driver version: Mesa Gallium driver 24.2.8-1ubuntu1~24.04.1 for AMD Radeon 660M (radeonsi, rembrandt, LLVM 19.1.1, DRM 3.57, 6.8.12-4-pve)
vainfo: Supported profile and entrypoints
      VAProfileH264ConstrainedBaseline: VAEntrypointVLD
      VAProfileH264ConstrainedBaseline: VAEntrypointEncSlice
      VAProfileH264Main               : VAEntrypointVLD
      VAProfileH264Main               : VAEntrypointEncSlice
      VAProfileH264High               : VAEntrypointVLD
      VAProfileH264High               : VAEntrypointEncSlice
      VAProfileHEVCMain               : VAEntrypointVLD
      VAProfileHEVCMain               : VAEntrypointEncSlice
      VAProfileHEVCMain10             : VAEntrypointVLD
      VAProfileHEVCMain10             : VAEntrypointEncSlice
      VAProfileJPEGBaseline           : VAEntrypointVLD
      VAProfileVP9Profile0            : VAEntrypointVLD
      VAProfileVP9Profile2            : VAEntrypointVLD
      VAProfileAV1Profile0            : VAEntrypointVLD
      VAProfileNone                   : VAEntrypointVideoProc
root@46a3c8bc9414:/# ls -l /dev/dri
total 0
crw-rw---- 1 root video 226,   0 Mar 24 00:31 card0
crw-rw---- 1 root video 226, 128 Mar 24 00:31 renderD128
```

3. Если всё равно `va_openDriver = -1` — проверь:

- Проброшены ли оба устройства в CasaOS
- Включён ли флаг "привилегированный контейнер"
- Назначена ли переменная окружения `PGID=44` (группа `video`) — чтобы пользователь Jellyfin мог получить доступ

---



