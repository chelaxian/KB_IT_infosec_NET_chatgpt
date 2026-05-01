## Гайд: macOS Sequoia на Proxmox (OSX‑PROXMOX) + рабочий Apple ID + быстрый доступ (NoMachine) + SSH + откат ZFS

Этот документ — воспроизводимая пошаговая инструкция по результату нашей сессии: развернуть **macOS Sequoia (15.x)** в **Proxmox VE 8.x** по `OSX‑PROXMOX`, довести до **рабочего Apple ID/iCloud** (обход VM‑детекта в Sequoia), настроить **NoMachine** для нормальной отзывчивости UI и **SSH** в macOS, а также подготовить **откат** через ZFS снапшоты.

> Источники/контекст:  
> - `OSX‑PROXMOX` — базовый установщик/шаблон VM: [`luchina-gabriel/OSX-PROXMOX`](https://github.com/luchina-gabriel/OSX-PROXMOX)  
> - Проблема Apple ID на Sequoia в Proxmox и решение через “скрыть VM”: [Proxmox forum thread](https://forum.proxmox.com/threads/macos-sequoia-cant-log-apple-id-and-its-services.154328/)  
> - RestrictEvents релиз: [RestrictEvents 1.1.6](https://github.com/acidanthera/RestrictEvents/releases/tag/1.1.6)

---

### Цели и итоговое состояние

В конце у вас должно быть:

- Proxmox VE 8.x, CPU clocksource `tsc` (важно для стабильности macOS при нескольких ядрах).
- VM с macOS Sequoia (15.x), например `VMID=116`:
  - `bios: ovmf`, `machine: q35`
  - OpenCore образ подключён как `ide0`, recovery как `ide2`
  - системный диск `virtio0` (например 80G)
  - сеть (в нашем кейсе) `vmxnet3`
  - CPU/RAM — любые разумные (у нас 8 cores / 16GB)
- Apple ID логинится (пропадает “Сбой проверки / неизвестная ошибка”).
- В macOS:
  - `sysctl kern.hv_vmm_present` возвращает **0**
  - работает NoMachine (порт 4000)
  - работает SSH (порт 22) с ключом
- На хосте Proxmox:
  - создан ZFS snapshot `@appleid-fixed` на zvol’ах VM
  - есть `/root/rollback-vm116-appleid-fixed.sh` для отката

---

## 0) Предварительные условия (перед началом)

### 0.1 Железо/BIOS
- Включите виртуализацию (SVM/VT-x), IOMMU не обязателен для этого гайда.
- Убедитесь, что `TSC` стабильный (важно для мультикорности).

### 0.2 Proxmox
- Рекомендуется свежий Proxmox VE (у нас был 8.4.x).
- Есть доступ root по SSH к Proxmox.

---

## 1) Проверка TSC на Proxmox (обязательно)

На Proxmox host:

```bash
cat /sys/devices/system/clocksource/clocksource0/current_clocksource
dmesg | grep -i -e tsc -e clocksource
```

Нужно: `tsc`. Если `hpet`/TSC unstable — сначала чините BIOS (ErP/C-states), иначе macOS может падать на нескольких ядрах.

---

## 2) Установка/создание VM через OSX‑PROXMOX

### 2.1 Запуск установщика
На Proxmox host:

```bash
/bin/bash -c "$(curl -fsSL https://install.osx-proxmox.com)"
```

Скрипт подтянет репозиторий и откроет меню.

### 2.2 Выбор версии macOS
В меню выбираете **Sequoia**.

По умолчанию `OSX‑PROXMOX`:
- создаст OpenCore образ `opencore-osx-proxmox-vm.iso` в ISO storage (`/var/lib/vz/template/iso/`)
- скачает recovery `recovery-sequoia.iso`
- создаст VM (у нас это был `VMID 116`, `HACK-SEQUOIA`)

Проверка на Proxmox:

```bash
qm list | grep -i HACK
qm config <VMID>
ls -lah /var/lib/vz/template/iso | grep -E 'opencore-osx-proxmox-vm\.iso|recovery-sequoia\.iso'
```

---

## 3) Установка macOS Sequoia

В Proxmox Web UI → VM → Console:
1) **Disk Utility** → Erase:
   - Format: **APFS**
   - Scheme: **GUID**
2) **Reinstall macOS Sequoia** → установка на созданный APFS диск.

После установки система загрузится.

---

## 4) Увеличение ресурсов VM (опционально)

Например (остановите VM перед изменениями):

```bash
qm stop <VMID> --skiplock 1 || true
qm set <VMID> --memory 16384 --cores 8 --balloon 0
qm start <VMID>
```

> Важно: “7 MB VRAM” в About this Mac — это нормальное следствие отсутствия Metal GPU в VM. RAM не превращается в VRAM. Мы компенсируем UX через NoMachine.

---

## 5) Быстрый “рабочий стол” на Windows: NoMachine (рекомендуется)

### 5.1 Узнать IP macOS VM
В macOS Terminal:

```bash
ipconfig getifaddr en0
```

Например: `10.11.0.138`.

### 5.2 Установить NoMachine
- Установить NoMachine на macOS (Server включается/поднимается).
- Установить NoMachine client на Windows.
- Подключение: `10.11.0.138:4000`.

Проверка порта на Windows:

```powershell
Test-NetConnection -ComputerName 10.11.0.138 -Port 4000
```

---

## 6) Включить SSH в macOS VM (чтобы агент мог чинить всё сам)

### 6.1 Поднять sshd (Sequoia иногда не имеет активного sshd “из коробки”)
В macOS Terminal:

```bash
sudo launchctl bootstrap system /System/Library/LaunchDaemons/ssh.plist
sudo launchctl kickstart -k system/com.openssh.sshd
sudo lsof -nP -iTCP:22 -sTCP:LISTEN
```

Должно показать LISTEN на `*:22`.

### 6.2 Добавить ключ в `authorized_keys`
Создайте `~/.ssh/authorized_keys` и задайте права:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

cat > ~/.ssh/authorized_keys <<'EOF'
<ВСТАВЬТЕ_ВАШ_PUBLIC_KEY>
EOF

chmod 600 ~/.ssh/authorized_keys
ls -la ~/.ssh ~/.ssh/authorized_keys
```

Проверка с Windows:

```bash
ssh <macos_user>@<macos_ip> "whoami; sw_vers"
```

---

## 7) Apple ID на Sequoia в Proxmox: корень проблемы и правильное решение

### 7.1 Симптом
При попытке входа Apple ID:  
**«Сбой проверки / произошла неизвестная ошибка»**.

### 7.2 Почему это происходит
На Sequoia Apple‑сервисы/демоны/проверки используют детект виртуализации. Ключевой индикатор:

```bash
sysctl kern.hv_vmm_present
```

В VM он обычно **1**. Для Apple ID на Sequoia в Proxmox это часто блокер.

### 7.3 Цель
Сделать:

```bash
sysctl kern.hv_vmm_present
# => 0
```

### 7.4 Что мы пробовали и что реально сработало
- Классические iServices фиксы (SMBIOS/en0 built‑in/NVRAM) **не помогли** в Sequoia‑VM, хотя NVRAM был рабочий и en0 built-in.
- `RestrictEvents.kext` + `revpatch=sbvmm` **сам по себе** загрузился, но `hv_vmm_present` оставался 1.
- Рабочее итоговое решение: **kernel patches в OpenCore + (опционально) RestrictEvents**, после чего `hv_vmm_present` стал 0 и Apple ID заработал.

---

## 8) Исправление OpenCore EFI на “диске EFI-PX-HACK” (правим прямо в macOS)

У `OSX‑PROXMOX` OpenCore диск в macOS виден как отдельный FAT, в нашем случае:

- `disk1s1` → `/Volumes/EFI-PX-HACK`
- OpenCore: `/Volumes/EFI-PX-HACK/EFI/OC/config.plist`

Проверка:

```bash
diskutil list
ls /Volumes
ls -la /Volumes/EFI-PX-HACK/EFI/OC
```

---

## 9) Установка RestrictEvents.kext и правка boot-args (через терминал)

### 9.1 Скачать RestrictEvents.kext
В macOS:

```bash
rm -rf /tmp/re
mkdir -p /tmp/re
cd /tmp/re

curl -L -o re.zip -fsSL \
  https://github.com/acidanthera/RestrictEvents/releases/download/1.1.6/RestrictEvents-1.1.6-RELEASE.zip

ditto -x -k re.zip .
rm -rf /Volumes/EFI-PX-HACK/EFI/OC/Kexts/RestrictEvents.kext
cp -R RestrictEvents.kext /Volumes/EFI-PX-HACK/EFI/OC/Kexts/
ls -ld /Volumes/EFI-PX-HACK/EFI/OC/Kexts/RestrictEvents.kext
```

### 9.2 Включить `revpatch=sbvmm` в boot-args
Мы добавили `revpatch=sbvmm` в:

`NVRAM -> Add -> 7C436110-AB2A-4BBB-A880-FE41995C9F82 -> boot-args`

Если у вас уже есть `PlistBuddy`-подход — используйте, но аккуратно (у нас он “сломал” Kernel/Add). Надёжнее — Python/`plistlib` (см. ниже).

---

## 10) ВАЖНО: Kernel->Add должен быть корректным массивом dict’ов (мы это чинили)

У нас `Kernel -> Add` оказался повреждён (в массиве были строки/пустые элементы), из‑за чего `PlistBuddy` ломался.

### 10.1 Проверка структуры
В macOS:

```bash
plutil -p /Volumes/EFI-PX-HACK/EFI/OC/config.plist | grep -n '"Kernel" => {' -n
plutil -p /Volumes/EFI-PX-HACK/EFI/OC/config.plist | sed -n '90,160p'
```

В рабочем виде элементы `Kernel.Add` — это dict’ы вида:

```text
"BundlePath" => "Lilu.kext"
"ExecutablePath" => "Contents/MacOS/Lilu"
...
```

### 10.2 Авто-чинилка Kernel->Add (рабочий подход)
Мы применили Python‑скрипт, который:
- выкидывает не‑dict элементы из `Kernel.Add`
- гарантирует наличие базовых kext (Lilu/VirtualSMC/WhateverGreen/AppleMCEReporterDisabler)
- добавляет `RestrictEvents.kext`

В macOS:

```bash
python3 - <<'PY'
import plistlib
from copy import deepcopy
from pathlib import Path
import time

cfg=Path('/Volumes/EFI-PX-HACK/EFI/OC/config.plist')
bak=cfg.with_name(cfg.name+f'.bak.kerneladdfix.{int(time.time())}')
bak.write_bytes(cfg.read_bytes())

pl=plistlib.loads(cfg.read_bytes())
adds=pl.get('Kernel',{}).get('Add',[])
kept=[a for a in adds if isinstance(a,dict) and str(a.get('BundlePath','')).endswith('.kext')]

needed={
  'AppleMCEReporterDisabler.kext':{
    'Arch':'Any','BundlePath':'AppleMCEReporterDisabler.kext','Comment':'AppleMCEReporterDisabler.kext','Enabled':True,
    'ExecutablePath':'','MaxKernel':'','MinKernel':'','PlistPath':'Contents/Info.plist',
  },
  'Lilu.kext':{
    'Arch':'Any','BundlePath':'Lilu.kext','Comment':'Lilu.kext','Enabled':True,
    'ExecutablePath':'Contents/MacOS/Lilu','MaxKernel':'','MinKernel':'','PlistPath':'Contents/Info.plist',
  },
  'VirtualSMC.kext':{
    'Arch':'Any','BundlePath':'VirtualSMC.kext','Comment':'VirtualSMC.kext','Enabled':True,
    'ExecutablePath':'Contents/MacOS/VirtualSMC','MaxKernel':'','MinKernel':'','PlistPath':'Contents/Info.plist',
  },
  'WhateverGreen.kext':{
    'Arch':'Any','BundlePath':'WhateverGreen.kext','Comment':'WhateverGreen.kext','Enabled':True,
    'ExecutablePath':'Contents/MacOS/WhateverGreen','MaxKernel':'','MinKernel':'','PlistPath':'Contents/Info.plist',
  },
}

by_bundle={a.get('BundlePath'):a for a in kept}
for bp,tmpl in needed.items():
    if bp not in by_bundle:
        kept.append(deepcopy(tmpl))

re_bp='RestrictEvents.kext'
if re_bp not in {a.get('BundlePath') for a in kept}:
    kept.append({
        'Arch':'Any',
        'BundlePath':re_bp,
        'Comment':'RestrictEvents',
        'Enabled':True,
        'ExecutablePath':'Contents/MacOS/RestrictEvents',
        'MaxKernel':'',
        'MinKernel':'',
        'PlistPath':'Contents/Info.plist',
    })

order=['AppleMCEReporterDisabler.kext','Lilu.kext','VirtualSMC.kext','WhateverGreen.kext','RestrictEvents.kext']
kept.sort(key=lambda a: order.index(a.get('BundlePath')) if a.get('BundlePath') in order else 999)

pl.setdefault('Kernel',{})['Add']=kept
cfg.write_bytes(plistlib.dumps(pl,sort_keys=False))

print('backup:',bak)
print('Kernel.Add:', [a.get('BundlePath') for a in kept])
PY
```

---

## 11) Kernel Patch: сделать `hv_vmm_present=0` (ключевой шаг)

После этих правок мы добавили 2 kernel patch dict’а в `Kernel -> Patch`, которые меняют видимость `hv_vmm_present` (метод из Proxmox‑обсуждения).

В macOS (правим `config.plist` на EFI):

```bash
python3 - <<'PY'
import plistlib, base64, time
from pathlib import Path

cfg=Path('/Volumes/EFI-PX-HACK/EFI/OC/config.plist')
pl=plistlib.loads(cfg.read_bytes())

ker=pl.setdefault('Kernel',{})
patches=ker.setdefault('Patch',[])

def mk(comment, find_b64, repl_b64, min_kernel):
    return {
        'Arch':'x86_64',
        'Base':'',
        'Comment':comment,
        'Count':1,
        'Enabled':True,
        'Find':base64.b64decode(find_b64),
        'Identifier':'kernel',
        'Limit':0,
        'Mask':b'',
        'MaxKernel':'',
        'MinKernel':min_kernel,
        'Replace':base64.b64decode(repl_b64),
        'ReplaceMask':b'',
        'Skip':0,
    }

p1 = mk(
  'VM check bypass - swap hv_vmm_present<->hibernatecount (1/2)',
  'aGliZXJuYXRlaGlkcmVhZHkAaGliZXJuYXRlY291bnQA',
  'aGliZXJuYXRlaGlkcmVhZHkAaHZfdm1tX3ByZXNlbnQA',
  '20.4.0'
)

p2 = mk(
  'VM check bypass - swap hv_vmm_present<->hibernatecount (2/2)',
  'Ym9vdCBzZXNzaW9uIFVVSUQAaHZfdm1tX3ByZXNlbnQA',
  'Ym9vdCBzZXNzaW9uIFVVSUQAaGliZXJuYXRlY291bnQA',
  '22.0.0'
)

comments=set(p.get('Comment') for p in patches if isinstance(p,dict))
added=0
for p in (p1,p2):
    if p['Comment'] not in comments:
        patches.append(p)
        added += 1

bak=cfg.with_name(cfg.name+f'.bak.kpatch.{int(time.time())}')
bak.write_bytes(cfg.read_bytes())
cfg.write_bytes(plistlib.dumps(pl,sort_keys=False))

print('added',added,'backup',bak)
PY
```

---

## 12) Перезагрузка и проверка Apple ID

Перезагрузите macOS (или VM), после загрузки:

```bash
sysctl kern.hv_vmm_present
```

Должно быть:

```text
kern.hv_vmm_present: 0
```

После этого Apple ID/iCloud логин должен работать.

---

## 13) Снапшот/сохранение состояния (на Proxmox) и откат

### 13.1 Почему `qm snapshot` не работает
В нашей инсталляции Proxmox возвращал `snapshot feature is not available`, поэтому вместо этого используем **ZFS snapshots**.

### 13.2 Создание снапшота (на Proxmox host)
В Proxmox Shell:

```bash
tag=appleid-fixed

zfs list -H -o name -t volume | grep -E 'vm-116-disk-(0|1)$' | while read -r z; do
  echo "SNAP: ${z}@${tag}"
  zfs snapshot "${z}@${tag}"
done

cp -a /etc/pve/qemu-server/116.conf "/etc/pve/qemu-server/116.conf.${tag}"
```

### 13.3 Скрипт отката (в `/root`)
Создайте:

```bash
cat > /root/rollback-vm116-appleid-fixed.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

VMID=116
TAG=appleid-fixed
CONF=/etc/pve/qemu-server/${VMID}.conf
CONF_BAK=${CONF}.${TAG}

log() { echo "[rollback] $*"; }

log "Stopping VM ${VMID}..."
qm stop "${VMID}" --skiplock 1 >/dev/null 2>&1 || true

if [[ -f "${CONF_BAK}" ]]; then
  log "Restoring config ${CONF_BAK} -> ${CONF}"
  cp -a "${CONF_BAK}" "${CONF}"
else
  log "WARN: ${CONF_BAK} not found; leaving config as-is"
fi

log "Finding zvols for VM ${VMID}..."
zvols=()
while IFS= read -r z; do
  case "$z" in
    */vm-${VMID}-disk-0|*/vm-${VMID}-disk-1) zvols+=("$z") ;;
  esac
done < <(zfs list -H -o name -t volume)

if [[ ${#zvols[@]} -eq 0 ]]; then
  log "ERROR: No zvols found for vm-${VMID}-disk-0/1"
  exit 1
fi

for z in "${zvols[@]}"; do
  snap="${z}@${TAG}"
  log "Rolling back ${snap}"
  zfs rollback -r "${snap}"
done

log "Starting VM ${VMID}..."
qm start "${VMID}"
qm status "${VMID}" || true
log "DONE"
EOF

chmod +x /root/rollback-vm116-appleid-fixed.sh
```

Запуск отката:

```bash
/root/rollback-vm116-appleid-fixed.sh
```

---

## 14) Обновления macOS (важное предупреждение)
Не обновляйте macOS “в лоб” (особенно до **Tahoe 26.x**) без теста на клоне/снапшоте.

Причина: kernel patch может перестать матчиться, и вы потеряете:
- `hv_vmm_present=0`
- Apple ID
- или даже загрузку

Рекомендуемый процесс:
1) сделать ZFS snapshots
2) сделать clone VM
3) обновлять **clone**, а рабочую VM оставить.

---

## Диагностика (если что-то пошло не так)

### Apple ID снова “Сбой проверки”
Проверить:

```bash
sysctl kern.hv_vmm_present
```

Если снова `1`:
- patch не применился (обновление ядра/сломанный OpenCore)
- проверяйте `config.plist` на EFI и наличие Patch entries

### Проверить, что RestrictEvents реально загружен
```bash
kmutil showloaded | grep -i RestrictEvents
nvram -p | grep boot-args
```

---

## Что именно “мы получили” и как это воспроизводится
- Базовая VM Sequoia по `OSX‑PROXMOX`: [`luchina-gabriel/OSX-PROXMOX`](https://github.com/luchina-gabriel/OSX-PROXMOX)
- Apple ID на Sequoia‑VM: нужен обход VM‑детекта (`hv_vmm_present=0`), см. контекст: [Proxmox thread](https://forum.proxmox.com/threads/macos-sequoia-cant-log-apple-id-and-its-services.154328/)
- Для удобной работы без Metal: NoMachine
- Для управления без ручных шагов: SSH в macOS
- Для сохранения состояния: ZFS snapshot + rollback script (т.к. `qm snapshot` недоступен)

---

Если хотите, я могу дополнить этот гайд разделом **“автоматизация: один скрипт на Proxmox, который проверяет hv_vmm_present по SSH и валидирует Apple ID готовность”** (смоук‑проверка перед апдейтами).
