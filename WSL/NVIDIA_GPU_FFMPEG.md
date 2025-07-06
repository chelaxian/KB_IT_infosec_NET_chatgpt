# Настройка NVIDIA GPU для FFmpeg в WSL2

## 1. Предварительные требования

### Windows
1. Убедитесь, что у вас установлен WSL2
2. Скачайте и установите [NVIDIA Driver (Studio)](https://www.nvidia.com/download-center/)
   - Выберите опцию "Studio Driver" вместо "Game Ready Driver"
   - Studio драйверы лучше оптимизированы для работы с видео

### Конфигурация WSL2
1. Создайте/отредактируйте файл `C:\Users\YourUsername\.wslconfig`:
```ini
[wsl2]
memory=24GB
processors=12
swap=32GB
swapFile=L:\\wsl-swap.vhdx
localhostForwarding=true
gpuSupport=true
debugConsole=true
nestedVirtualization=true
```

2. Перезапустите WSL в PowerShell:
```powershell
wsl --shutdown
wsl
```

## 2. Установка CUDA и FFmpeg в WSL2

1. Удалите старые конфигурации NVIDIA (если есть):
```bash
sudo rm /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

2. Установите CUDA toolkit и FFmpeg:
```bash
sudo apt update && sudo apt install -y nvidia-cuda-toolkit ffmpeg
```
# Установка дополнительных утилит (опционально)
```bash
sudo apt install -y pciutils
```

## 3. Проверка установки

### Проверка системных ресурсов
```bash
# Проверка памяти
free -h

# Проверка количества процессоров
nproc

# Проверка swap
swapon --show
```

### Проверка GPU
```bash
nvidia-smi
```

Пример вывода:
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.51.03              Driver Version: 576.28         CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 3080        On  |   00000000:01:00.0  On |                  N/A |
|  0%   51C    P0             59W /  340W |    2575MiB /  10240MiB |      2%      Default |
```

### Проверка поддержки NVENC в FFmpeg
```bash
ffmpeg -encoders | grep -i nvidia
```

Должны быть доступны следующие энкодеры:
- `h264_nvenc` - для H.264
- `hevc_nvenc` - для H.265
- `av1_nvenc` - для AV1

## 4. Тестирование GPU-ускорения

Тестовое кодирование:
```bash
ffmpeg -f lavfi -i nullsrc=s=1920x1080:d=5 -c:v h264_nvenc -preset p1 -rc vbr -cq 23 -b:v 20M -maxrate 25M -bufsize 25M -profile:v high test_nvenc_high.mp4
```

## 5. Преимущества использования NVENC

1. Значительно более быстрое кодирование (в 2-6 раз быстрее CPU)
2. Меньшая нагрузка на CPU
3. Лучший контроль качества при заданном битрейте
4. Аппаратное ускорение для форматов:
   - H.264 (AVC)
   - H.265 (HEVC)
   - AV1

## 6. Проверка работы

При запуске FFmpeg с GPU-ускорением в логах должны появиться строки:
```
[h264_nvenc @ 0x...] Preset: p1
[h264_nvenc @ 0x...] GPU: NVIDIA GeForce RTX 3080
[h264_nvenc @ 0x...] Using NVENC hardware acceleration
```

## 7. Возможные проблемы

1. Если `nvidia-smi` не видит GPU:
   - Проверьте `gpuSupport=true` в `.wslconfig`
   - Перезапустите WSL
   - Убедитесь, что установлен правильный драйвер NVIDIA

2. Если FFmpeg не видит NVENC:
   - Проверьте установку `nvidia-cuda-toolkit`
   - Убедитесь, что FFmpeg собран с поддержкой NVENC 
