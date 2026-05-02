# Развёртывание с нуля: Qwen Code, Claude Code, LiteLLM, free-claude-code, claude-mem, Obsidian + NVIDIA NIM и Z.AI GLM

Пошаговая инструкция для воспроизведения рабочей связки на **новой установке Windows**. Секреты (API-ключи, токены) **не** приводятся — только имена переменных окружения и шаблоны.

## Оглавление

1. [Цель и архитектура](#1-цель-и-архитектура)
2. [Требования и установка базовых инструментов](#2-требования-и-установка-базовых-инструментов)
3. [Переменные окружения (без значений)](#3-переменные-окружения-без-значений)
4. [Каталог проекта и сессии Qwen](#4-каталог-проекта-и-сессии-qwen)
5. [LiteLLM для пресетов NIM (порт 4000)](#5-litellm-для-пресетов-nim-порт-4000)
6. [free-claude-code для Claude Code → NIM](#6-free-claude-code-для-claude-code--nim)
7. [claude-mem](#7-claude-mem)
8. [Obsidian](#8-obsidian)
9. [Логика совместимости NIM (whitelist, прокси, обрезка контекста)](#9-логика-совместимости-nim-whitelist-прокси-обрезка-контекста)
10. [Ярлыки на рабочем столе: эквивалент `.lnk` в PowerShell](#10-ярлыки-на-рабочем-столе-эквивалент-lnk-в-powershell)
11. [Полные тексты ключевых скриптов](#11-полные-тексты-ключевых-скриптов)

---

## 1. Цель и архитектура

- **Qwen Code** работает с **Z.AI Coding API** (OpenAI-совместимый) и с **NVIDIA NIM** (integrate OpenAI).
- **Пресеты NIM** (GLM-4.7 tools, DeepSeek Terminus tools) идут через **LiteLLM** на `http://127.0.0.1:4000/v1`.
- **Произвольная модель NIM** вне белого списка: локальный **Node-прокси** `nim-integrate-string-content-proxy.mjs` (строковый `content`, усечение истории по tier).
- **Claude Code** для Z.AI — напрямую на `api.z.ai` (Anthropic-совместимый эндпоинт).
- **Claude Code** для NIM — через локальный **free-claude-code** (uvicorn), который проксирует в NIM; для моделей вне whitelist — `minimal` tools и те же ограничения в Python.
- **claude-mem** — воркер на `127.0.0.1:37777`; **Obsidian** — хранилище для сессий Claude (рабочая директория при запуске).

---

## 2. Требования и установка базовых инструментов

### 2.1. Node.js LTS

Установите [Node.js](https://nodejs.org/) (LTS). Убедитесь, что в PATH есть:

- `node`, `npm`
- после глобальных установок — `%APPDATA%\npm`

### 2.2. Qwen Code (CLI)

```powershell
npm install -g @qwen-code/qwen-code@latest
```

Проверка: `qwen --help` (или полный путь `%APPDATA%\npm\qwen.cmd`).

### 2.3. Claude Code (CLI)

Установка по официальной документации Anthropic (глобальный npm-пакет). Типично:

```powershell
npm install -g @anthropic-ai/claude-code
```

Проверка: `claude --help`, ожидается `claude.cmd` в `%APPDATA%\npm`.

### 2.4. uv (Astral)

Установите [uv](https://docs.astral.sh/uv/). В скриптах сессии Claude путь к `uv.exe` может быть задан явно — на новой машине **исправьте** путь в `run-claude-cloud-session.ps1` (функция `Ensure-FreeClaudeCodeProxy`) на ваш, например:

`%USERPROFILE%\.local\bin\uv.exe`

### 2.5. Bun (опционально, для fallback claude-mem)

Рекомендуется для fallback-запуска воркера claude-mem: [Bun](https://bun.sh/).

### 2.6. Копирование репозитория `qwen-local-setup`

Скопируйте дерево проекта (скрипты, `qwen-sessions`, `free-claude-code`) в выбранный корень, например:

- `D:\qwen-local-setup`

Далее в инструкции: **`$RepoRoot`** — этот каталог.

**Обязательно** замените во всех скриптах жёстко прошитые пути:

- `I:\qwen-local-setup` → ваш `$RepoRoot`
- `C:\Users\chelaxian\...` → ваши `Desktop`, `Documents`, `uv.exe`, иконка `.ico`

---

## 3. Переменные окружения (без значений)

Задайте на уровне **пользователя** (Windows: «Переменные среды») или через `setx` (новая сессия):

| Переменная | Назначение |
|------------|------------|
| `ZAI_API_KEY` | Z.AI Coding / Anthropic-совместимые вызовы для Claude и OpenAI-режим Qwen |
| `NVIDIA_NIM_API_KEY` | Доступ к NVIDIA integrate API для NIM |

Не коммитьте значения. В репозитории используйте только `*.example` при необходимости.

---

## 4. Каталог проекта и сессии Qwen

В репозитории должны существовать:

- `qwen-sessions\nim-glm-47\.qwen\settings.json` — NIM GLM-4.7 через LiteLLM `:4000`
- `qwen-sessions\nim-deepseek-v31\.qwen\settings.json` — NIM DeepSeek Terminus через `:4000`
- `qwen-sessions\zai-glm47\.qwen\settings.json` — Z.AI GLM-4.7

Динамические сессии создаются в `qwen-sessions\_dynamic\...` скриптом `run-qwen-code-dynamic.ps1`.

---

## 5. LiteLLM для пресетов NIM (порт 4000)

`run-qwen-code-nvidia-nim.ps1` ожидает:

1. Слушающий порт **4000** на `127.0.0.1`, либо
2. Скрипт запуска: **`%USERPROFILE%\.qwen\litellm\start-nvidia-nim-proxy.ps1`**

Создайте каталог `%USERPROFILE%\.qwen\litellm\` и разместите там свой прокси-лаунчер. Пример **шаблона** (адаптируйте под ваш `config.yaml` и способ вызова `litellm`):

```powershell
# %USERPROFILE%\.qwen\litellm\start-nvidia-nim-proxy.ps1  (ШАБЛОН)
$ErrorActionPreference = "Stop"
$env:NVIDIA_NIM_API_KEY = [Environment]::GetEnvironmentVariable("NVIDIA_NIM_API_KEY", "User")
if ([string]::IsNullOrWhiteSpace($env:NVIDIA_NIM_API_KEY)) {
  throw "Задайте пользовательскую переменную NVIDIA_NIM_API_KEY"
}
$here = $PSScriptRoot
$config = Join-Path $here "litellm-nim-config.yaml"
if (-not (Test-Path -LiteralPath $config)) {
  throw "Создайте $config — см. документацию LiteLLM и маппинг model_list на integrate.api.nvidia.com"
}
# Пример: litellm в PATH после pipx/pip install
litellm --config $config --port 4000 --host 127.0.0.1
```

В `config.yaml` должны быть объявлены имена моделей в точности как в `settings.json` сессий (`nim-glm-4.7-tools`, `nim-deepseek-v3.1-terminus-tools` и т.д.) с `api_base: https://integrate.api.nvidia.com/v1` и ключом из окружения. Конкретное содержимое YAML зависит от вашей подписки и имён моделей в каталоге NIM — **не** включайте ключи в файл, используйте `os.environ/NVIDIA_NIM_API_KEY` в стиле LiteLLM.

---

## 6. free-claude-code для Claude Code → NIM

1. Откройте терминал в `$RepoRoot\free-claude-code`.
2. Установите зависимости через uv (как принято в проекте): например `uv sync`.
3. Прокси поднимается скриптом `run-claude-cloud-session.ps1` через `uv run uvicorn server:app --host 127.0.0.1 --port <порт>`.

Порты по умолчанию в логике лаунчера:

- GLM NIM: **8082** (если не переопределён)
- DeepSeek Terminus: **8083**

Переменные для процесса прокси (без вывода значений в лог пользователя): `NVIDIA_NIM_API_KEY`, `MODEL`, `ANTHROPIC_AUTH_TOKEN` (локальный токен доверия к прокси, не путать с облачным секретом провайдера).

---

## 7. claude-mem

1. Установите плагин по инструкции проекта [claude-mem](https://github.com/thedotmack/claude-mem) (marketplace / `npx claude-mem`).
2. Запуск воркера: см. скрипт `start-claude-mem.ps1` в репозитории (порт **37777**).

Проверка: `http://127.0.0.1:37777/` открывается после `npx claude-mem start`.

---

## 8. Obsidian

1. Установите [Obsidian](https://obsidian.md/).
2. Создайте хранилище (vault) для проектов агента.
3. В `run-claude-cloud-launcher.ps1` и `run-claude-cloud-session.ps1` задайте **свои** `-VaultPath` и `-ObsidianExe` (или отредактируйте значения по умолчанию в файлах).

---

## 9. Логика совместимости NIM (whitelist, прокси, обрезка контекста)

**Белый спискок каталоговых id** (нативный tool calling, без `tool_choice=none` для совместимости с vLLM):

- `z-ai/glm4.7`
- `qwen/qwen3.5-122b-a10b`
- `deepseek-ai/deepseek-v3.1-terminus`

Для **остальных** NIM-моделей:

| Компонент | Поведение |
|-----------|-----------|
| Qwen Code (`run-qwen-code-dynamic.ps1`) | Локальный прокси `nim-integrate-string-content-proxy.mjs`, `tool_choice=none`, `skipStartupContext`, tier micro/standard/large |
| Claude (`run-claude-cloud-launcher.ps1`) | `--tools minimal` если модель не в whitelist |
| free-claude-code (`providers/nvidia_nim/request.py`) | flatten `content`, `tool_choice=none`, cap `max_tokens`, обрезка сообщений по бюджету |

**Типичные ошибки API:**

- `400` из-за массива в `content` → flatten в строку.
- `400` из-за `tool_choice=auto` на бэкендах без auto tool choice → `none`.
- `400` при маленьком контексте (например 4096) и длинной истории → tier **micro** + trim в прокси и в Python.

---

## 10. Ярлыки на рабочем столе: эквивалент `.lnk` в PowerShell

Файлы `.lnk` бинарные; их свойства воспроизводятся скриптом. Ниже **один скрипт**, который создаёт:

- `Claude Code (cloud).lnk`
- `Qwen Code (cloud).lnk`
- `Claude Mem Start.lnk`
- `Claude Mem Viewer.lnk`

Перед запуском задайте пути в параметрах.

```powershell
# create-desktop-shortcuts.ps1 — сохраните и выполните с правками путей
param(
  [string]$RepoRoot = "D:\qwen-local-setup",
  [string]$DesktopPath = [Environment]::GetFolderPath("Desktop"),
  [string]$VaultPath = "$env:USERPROFILE\Documents\Obsidian Vault",
  [string]$ObsidianExe = "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe",
  [string]$IconLocation = "$env:USERPROFILE\Pictures\claudecode.ico,0"
)

$ErrorActionPreference = "Stop"
$cmdExe = (Get-Command cmd.exe).Source
$psExe  = (Get-Command powershell.exe).Source
$ws = New-Object -ComObject WScript.Shell

$launcherClaude = Join-Path $RepoRoot "scripts\run-claude-cloud-launcher.ps1"
$launcherQwen   = Join-Path $RepoRoot "scripts\run-qwen-code-launcher.ps1"
$memScript      = Join-Path $RepoRoot "scripts\start-claude-mem.ps1"

function New-Shortcut {
  param(
    [string]$LinkPath,
    [string]$TargetPath,
    [string]$Arguments,
    [string]$WorkingDirectory,
    [string]$Icon,
    [string]$Description
  )
  $s = $ws.CreateShortcut($LinkPath)
  $s.TargetPath = $TargetPath
  $s.Arguments = $Arguments
  $s.WorkingDirectory = $WorkingDirectory
  $s.WindowStyle = 1
  if ($Icon) { $s.IconLocation = $Icon }
  if ($Description) { $s.Description = $Description }
  $s.Save()
}

# Claude Code (cloud) — меню провайдеров
New-Shortcut `
  -LinkPath (Join-Path $DesktopPath "Claude Code (cloud).lnk") `
  -TargetPath $cmdExe `
  -Arguments ('/k chcp 65001 >nul & ' + $psExe + ' -NoProfile -ExecutionPolicy Bypass -File "' + $launcherClaude + '"') `
  -WorkingDirectory $RepoRoot `
  -Icon $IconLocation `
  -Description "Claude Code: Z.AI или NIM через free-claude-code — меню. Пресеты NIM без изменений. Другая модель (NIM вне GLM-4.7/Qwen3.5-122B/DeepSeek Terminus): tool_choice=none + content как строка + в лаунчере --tools minimal. Qwen: для таких NIM отдельно локальный прокси string-content."

# Qwen Code (cloud) — меню профилей
New-Shortcut `
  -LinkPath (Join-Path $DesktopPath "Qwen Code (cloud).lnk") `
  -TargetPath $cmdExe `
  -Arguments ('/k chcp 65001 >nul & ' + $psExe + ' -NoProfile -ExecutionPolicy Bypass -File "' + $launcherQwen + '"') `
  -WorkingDirectory $RepoRoot `
  -Icon $IconLocation `
  -Description "Qwen Code: Z.AI Coding / NVIDIA NIM — меню. Пресеты NIM без изменений. Другая модель NIM: локальный прокси string-content + минимальный режим. У Claude для таких NIM — free-claude-code и --tools minimal. Z.AI без ограничений."

# claude-mem — только старт воркера
New-Shortcut `
  -LinkPath (Join-Path $DesktopPath "Claude Mem Start.lnk") `
  -TargetPath $psExe `
  -Arguments ('-NoProfile -ExecutionPolicy Bypass -File "' + $memScript + '" -OpenBrowser 0') `
  -WorkingDirectory $env:USERPROFILE `
  -Icon $IconLocation `
  -Description "Старт claude-mem worker (127.0.0.1:37777)."

# claude-mem — старт + открыть viewer в браузере
New-Shortcut `
  -LinkPath (Join-Path $DesktopPath "Claude Mem Viewer.lnk") `
  -TargetPath $psExe `
  -Arguments ('-NoProfile -ExecutionPolicy Bypass -File "' + $memScript + '" -OpenBrowser 1') `
  -WorkingDirectory $env:USERPROFILE `
  -Icon $IconLocation `
  -Description "claude-mem: старт при необходимости и открыть http://127.0.0.1:37777/"

Write-Host "Shortcuts created on desktop." -ForegroundColor Green
```

Скрипт `scripts\update-cloud-shortcuts.ps1` в репозитории создаёт ярлыки с **другими именами** (`Claude Code (Cloud — выбор провайдера).lnk` и т.д.) — логика та же; переименуйте или объедините с приведённым выше.

---

## 11. Полные тексты ключевых скриптов

Ниже — копии файлов из `scripts/` на момент составления гайда. При расхождении с репозиторием **приоритет у файлов в git**.

### 11.1. `ensure-streaming-friendly-terminal.ps1`

```powershell
# Dot-source перед интерактивным Qwen Code / Claude Code:
#   . (Join-Path $PSScriptRoot 'ensure-streaming-friendly-terminal.ps1')
#
# Qwen Code (Ink + is-in-ci): любые CI_* / CI / CONTINUOUS_INTEGRATION дают «не CI-терминал» —
# страдает интерактив и по ощущениям стриминг (пакетная отрисовка).
# Claude Code в обычном cmd /k тоже не должен видеть фальш-CI.

foreach ($name in @(
    'CI',
    'CONTINUOUS_INTEGRATION',
    'GITHUB_ACTIONS',
    'GITLAB_CI',
    'BUILDKITE',
    'TEAMCITY_VERSION',
    'JENKINS_URL',
    'TRAVIS',
    'CIRCLECI'
  )) {
  if (Test-Path -LiteralPath "Env:$name") {
    Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue
  }
}

foreach ($var in @(Get-ChildItem Env: -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'CI_*' })) {
  Remove-Item -LiteralPath ("Env:{0}" -f $var.Name) -ErrorAction SilentlyContinue
}

if (-not $env:PYTHONUNBUFFERED) {
  $env:PYTHONUNBUFFERED = "1"
}
```

### 11.2. `start-claude-mem.ps1`

```powershell
[CmdletBinding()]
param(
  [int]$OpenBrowser = 0,
  [switch]$SkipStatus,
  [switch]$RepairInstall
)

$ErrorActionPreference = "Stop"

$npmBin = Join-Path $env:APPDATA "npm"
if (Test-Path -LiteralPath $npmBin) {
  $env:PATH = $npmBin + ";" + $env:PATH
}
$bunBin = Join-Path $HOME ".bun\bin"
if (Test-Path -LiteralPath $bunBin) {
  $env:PATH = $bunBin + ";" + $env:PATH
}

function Test-ClaudeMemPortOpen {
  $c = $null
  try {
    $c = New-Object System.Net.Sockets.TcpClient
    $ar = $c.BeginConnect("127.0.0.1", 37777, $null, $null)
    if (-not $ar.AsyncWaitHandle.WaitOne(600)) { return $false }
    $c.EndConnect($ar)
    return $c.Connected
  } catch {
    return $false
  } finally {
    if ($null -ne $c) { try { $c.Close() } catch {} }
  }
}

function Wait-ClaudeMemReady {
  param([int]$TimeoutSec = 20)
  $deadline = (Get-Date).AddSeconds([Math]::Max(1, $TimeoutSec))
  while ((Get-Date) -lt $deadline) {
    if (Test-ClaudeMemPortOpen) { return $true }
    Start-Sleep -Milliseconds 400
  }
  return $false
}

function Start-ClaudeMemFallbackDirect {
  $pluginDir = Join-Path $HOME ".claude\plugins\marketplaces\thedotmack\plugin"
  $workerScript = Join-Path $pluginDir "scripts\worker-service.cjs"
  if (-not (Test-Path -LiteralPath $workerScript)) {
    Write-Host "claude-mem: fallback недоступен (не найден worker-service.cjs)." -ForegroundColor DarkYellow
    return $false
  }

  $logDir = Join-Path $HOME ".qwen-local-setup"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $outLog = Join-Path $logDir "claude-mem.fallback.$stamp.out.log"
  $errLog = Join-Path $logDir "claude-mem.fallback.$stamp.err.log"

  $bunExe = $null
  try {
    $bunCmd = Get-Command bun -ErrorAction SilentlyContinue
    if ($bunCmd) { $bunExe = $bunCmd.Source }
  } catch {}
  if (-not $bunExe) {
    $bunExe = Join-Path $HOME ".bun\bin\bun.exe"
  }
  if (-not (Test-Path -LiteralPath $bunExe)) {
    Write-Host "claude-mem: fallback недоступен (bun.exe не найден)." -ForegroundColor Red
    return $false
  }
  try {
    Start-Process -FilePath $bunExe -WorkingDirectory $pluginDir -ArgumentList @("scripts/worker-service.cjs") -WindowStyle Hidden -RedirectStandardOutput $outLog -RedirectStandardError $errLog | Out-Null
  } catch {
    Write-Host "claude-mem: fallback запуск не удался: $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }

  if (Wait-ClaudeMemReady -TimeoutSec 25) {
    Write-Host "claude-mem: fallback успешно поднял worker (127.0.0.1:37777)." -ForegroundColor Green
    return $true
  }

  Write-Host "claude-mem: fallback не поднял порт 37777. Логи: $outLog ; $errLog" -ForegroundColor Red
  return $false
}

function Repair-ClaudeMemInstall {
  Write-Host "claude-mem: выполняю self-repair (npx claude-mem update)…" -ForegroundColor DarkYellow
  try {
    npx --yes claude-mem update | Out-Null
    return $true
  } catch {
    Write-Host "claude-mem: self-repair не удался: $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }
}

$pidFile = Join-Path $HOME ".claude-mem\worker.pid"

if (Test-ClaudeMemPortOpen) {
  Write-Host "claude-mem уже слушает 127.0.0.1:37777 — повторный старт не нужен." -ForegroundColor DarkGreen
  if ($OpenBrowser -ne 0) {
    try { Start-Process "http://127.0.0.1:37777/" | Out-Null } catch {}
  }
  if (-not $SkipStatus) {
    npx --yes claude-mem status
  }
  exit 0
}

if ($RepairInstall) {
  Write-Host "claude-mem: update (repair)…" -ForegroundColor Cyan
  npx --yes claude-mem update
}

Write-Host "claude-mem: остановка и очистка stale PID…" -ForegroundColor DarkCyan
try { npx --yes claude-mem stop 2>$null } catch {}
Start-Sleep -Milliseconds 500
if (Test-Path -LiteralPath $pidFile) {
  try { Remove-Item -LiteralPath $pidFile -Force -ErrorAction Stop } catch {}
}

Write-Host "claude-mem: start…" -ForegroundColor Cyan
npx --yes claude-mem start

if (-not (Wait-ClaudeMemReady -TimeoutSec 10)) {
  Write-Host "claude-mem: npx start не поднял worker, включаю fallback через bun…" -ForegroundColor DarkYellow
  if (Repair-ClaudeMemInstall) {
    Write-Host "claude-mem: повторный старт после self-repair…" -ForegroundColor DarkYellow
    npx --yes claude-mem start
  }
  if (-not (Wait-ClaudeMemReady -TimeoutSec 12)) {
    [void](Start-ClaudeMemFallbackDirect)
  }
}

if (-not $SkipStatus) {
  Start-Sleep -Seconds 2
  npx --yes claude-mem status
  if (Test-ClaudeMemPortOpen) {
    Write-Host "claude-mem: worker доступен на http://127.0.0.1:37777/" -ForegroundColor Green
  } else {
    Write-Host "claude-mem: worker всё ещё не запущен." -ForegroundColor Red
  }
}

if ($OpenBrowser -ne 0) {
  try { Start-Process "http://127.0.0.1:37777/" | Out-Null } catch {}
}
```

### 11.3. `nim-integrate-string-content-proxy.mjs`

```javascript
/**
 * Локальный OpenAI-совместимый прокси для NVIDIA integrate NIM (динамические модели вне whitelist):
 * 1) content: string (flatten массива частей)
 * 2) усечение messages по бюджету context − max_tokens − margin (Qwen Code иначе шлёт 8k+ токенов при ctx=4096)
 * Tier и лимиты совпадают с run-qwen-code-dynamic.ps1 / free-claude-code request.py.
 */
import http from "node:http";
import { Readable } from "node:stream";

const UPSTREAM_ORIGIN = (process.env.NIM_UPSTREAM_ORIGIN || "https://integrate.api.nvidia.com").replace(/\/$/, "");
const argvPort = process.argv[2] ? parseInt(process.argv[2], 10) : 0;
const PORT = Number.isFinite(argvPort) && argvPort > 0 ? argvPort : parseInt(process.env.NIM_FLATTEN_PROXY_PORT || "0", 10);

const MICRO_RE =
  /nemotron-mini|nemotron-3-content-safety|content-safety-reasoning|\/gliner|\/pii|\b300m\b|nemoretriever|nv-embed|embedcode|cosmos-transfer|cosmos-predict|magpie-tts|voicechat|safety-guard|zeroshot|llama-3\.1-nemotron-safety|transfer2\.5-2b|transfer1-7b|riva-translate|synthetic-video|active-speaker|video-detector|parakeet|whisper|\/tts|text-to-speech/i;
const LARGE_RE =
  /480b|235b|405b|70b|8x7b|8x22b|106b-a47b|\b128k\b|\b1m\b|qwen3-coder|minimax-m2|step-3\.5|solar-10\.7/i;

function tierFromModel(model) {
  const m = String(model || "").toLowerCase();
  if (MICRO_RE.test(m)) return "micro";
  if (LARGE_RE.test(m)) return "large";
  return "standard";
}

function ctxLimitFromTier(tier) {
  if (tier === "micro") return 4096;
  if (tier === "large") return 131072;
  return 16384;
}

function defaultMaxOut(tier) {
  if (tier === "micro") return 512;
  if (tier === "large") return 8192;
  return 2048;
}

function flattenContent(content) {
  if (content == null) return content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return content;
  const parts = [];
  for (const part of content) {
    if (typeof part === "string") {
      parts.push(part);
      continue;
    }
    if (part && typeof part === "object" && part.type === "text" && part.text != null) {
      parts.push(String(part.text));
    }
  }
  return parts.filter((p) => p.length > 0).join("\n\n");
}

function flattenBody(body) {
  if (!body || typeof body !== "object" || !Array.isArray(body.messages)) return body;
  return {
    ...body,
    messages: body.messages.map((m) => {
      if (!m || typeof m !== "object") return m;
      const content = flattenContent(m.content);
      return { ...m, content };
    }),
  };
}

function estMessagesTokens(messages) {
  if (!Array.isArray(messages)) return 0;
  let s = 0;
  for (const m of messages) {
    try {
      s += Math.max(4, Math.ceil(JSON.stringify(m ?? {}).length / 4));
    } catch {
      s += 64;
    }
  }
  return s;
}

function trimMessagesForBudget(messages, maxInputTokens) {
  if (!Array.isArray(messages)) return messages;
  const out = messages.map((m) => (m && typeof m === "object" ? { ...m } : m));
  let guard = 0;
  while (estMessagesTokens(out) > maxInputTokens && guard++ < 2000) {
    if (out.length <= 1) {
      const m0 = out[0];
      if (m0 && typeof m0 === "object" && typeof m0.content === "string") {
        const c = m0.content;
        const targetChars = Math.max(800, (maxInputTokens - 24) * 3);
        if (c.length > targetChars) {
          m0.content = "[truncated]\n" + c.slice(-targetChars);
        }
      }
      break;
    }
    if (out[0]?.role === "system" && out.length > 1) {
      out.splice(1, 1);
    } else {
      out.splice(0, 1);
    }
  }
  return out;
}

function applyNimCompat(body) {
  const b = flattenBody(typeof body === "object" && body ? { ...body } : body);
  const tier = tierFromModel(b.model);
  const ctx = ctxLimitFromTier(tier);
  const defOut = defaultMaxOut(tier);
  let maxOut = Number(b.max_tokens);
  if (!Number.isFinite(maxOut) || maxOut <= 0) maxOut = defOut;
  maxOut = Math.min(maxOut, defOut);
  b.max_tokens = maxOut;
  const margin = tier === "micro" ? 384 : 640;
  const maxInput = Math.max(200, ctx - maxOut - margin);
  b.messages = trimMessagesForBudget(b.messages || [], maxInput);
  return b;
}

function hopByHop(name) {
  const n = name.toLowerCase();
  return (
    n === "connection" ||
    n === "keep-alive" ||
    n === "proxy-authenticate" ||
    n === "proxy-authorization" ||
    n === "te" ||
    n === "trailers" ||
    n === "transfer-encoding" ||
    n === "upgrade"
  );
}

async function readJsonBody(req) {
  const chunks = [];
  for await (const ch of req) chunks.push(ch);
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw.trim()) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

if (!Number.isFinite(PORT) || PORT <= 0) {
  console.error("nim-integrate-string-content-proxy: pass port as argv (node …mjs 39081) or set NIM_FLATTEN_PROXY_PORT.");
  process.exit(1);
}

const server = http.createServer(async (req, res) => {
  try {
    const host = req.headers.host || `127.0.0.1:${PORT}`;
    const url = new URL(req.url || "/", `http://${host}`);

    if (req.method === "GET" && url.pathname === "/v1/models") {
      const r = await fetch(`${UPSTREAM_ORIGIN}/v1/models`, {
        headers: { authorization: req.headers.authorization || "" },
      });
      res.writeHead(r.status);
      if (r.body) Readable.fromWeb(r.body).pipe(res);
      else res.end();
      return;
    }

    if (req.method === "POST" && url.pathname === "/v1/chat/completions") {
      const body = await readJsonBody(req);
      if (body === null) {
        res.writeHead(400, { "content-type": "application/json" });
        res.end(JSON.stringify({ error: { message: "invalid json" } }));
        return;
      }
      const flat = applyNimCompat(body);
      const r = await fetch(`${UPSTREAM_ORIGIN}/v1/chat/completions`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: req.headers.authorization || "",
        },
        body: JSON.stringify(flat),
      });
      const outHeaders = {};
      r.headers.forEach((v, k) => {
        if (!hopByHop(k)) outHeaders[k] = v;
      });
      res.writeHead(r.status, outHeaders);
      if (r.body) Readable.fromWeb(r.body).pipe(res);
      else res.end();
      return;
    }

    res.writeHead(404, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: { message: "not found" } }));
  } catch (e) {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: { message: String(e && e.message ? e.message : e) } }));
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.error(`nim-integrate-string-content-proxy: http://127.0.0.1:${PORT}/v1 → ${UPSTREAM_ORIGIN}/v1`);
});
```

### 11.4. `run-qwen-code-dynamic.ps1`

```powershell
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("zai", "nim")]
  [string]$Provider,

  [Parameter(Mandatory = $true)]
  [string]$ModelId
)

$ErrorActionPreference = "Stop"

. (Join-Path $PSScriptRoot "ensure-streaming-friendly-terminal.ps1")
. (Join-Path $PSScriptRoot "launcher-provider-models.ps1")

function Read-SecretText([string]$Prompt) {
  $sec = Read-Host -Prompt $Prompt -AsSecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
  try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}

function Ensure-NpmBinInPath {
  $npmBin = Join-Path $env:APPDATA "npm"
  if (Test-Path -LiteralPath $npmBin) {
    $env:PATH = $npmBin + ";" + $env:PATH
  }
}

function Resolve-QwenExe {
  $cmd = Get-Command qwen -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  foreach ($p in @(
      (Join-Path $env:APPDATA "npm\qwen.cmd"),
      (Join-Path $env:APPDATA "npm\qwen.ps1")
    )) {
    if (Test-Path -LiteralPath $p) { return $p }
  }
  return ""
}

function Get-SafeDirName([string]$s) {
  $x = ($s -replace '[^a-zA-Z0-9._-]', '_')
  if ($x.Length -gt 48) { $x = $x.Substring(0, 48) }
  if ([string]::IsNullOrWhiteSpace($x)) { $x = "model" }
  return $x
}

function Build-QwenSettingsZai([string]$Mid) {
  return @{
    modelProviders = @{
      openai = @(
        @{
          id           = $Mid
          name         = ("Z.AI — {0} (dynamic)" -f $Mid)
          description  = "Coding API; extra_body как у GLM-4.7"
          envKey       = "OPENAI_API_KEY"
          baseUrl      = "https://api.z.ai/api/coding/paas/v4"
          generationConfig = @{
            timeout            = 600000
            maxRetries         = 4
            contextWindowSize  = 202752
            extra_body         = @{
              enable_thinking       = $true
              chat_template_kwargs  = @{
                enable_thinking = $true
                clear_thinking  = $false
              }
            }
            samplingParams = @{
              temperature = 0.6
              top_p         = 0.95
              max_tokens    = 81920
            }
          }
        }
      )
    }
    security = @{
      auth = @{ selectedType = "openai" }
    }
    model = @{ name = $Mid }
  }
}

function Get-FreeListenPort {
  param([int]$Min = 39080, [int]$Max = 39179)
  for ($p = $Min; $p -le $Max; $p++) {
    $c = $null
    try {
      $c = New-Object System.Net.Sockets.TcpListener([Net.IPAddress]::Loopback, $p)
      $c.Start()
      $c.Stop()
      return $p
    } catch {
      if ($c) { try { $c.Stop() } catch {} }
    }
  }
  throw "Не найден свободный TCP-порт в диапазоне $Min-$Max для NIM-прокси."
}

function Wait-TcpListen {
  param([int]$Port, [int]$TimeoutSec = 15)
  $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSec)
  while ([DateTime]::UtcNow -lt $deadline) {
    $c = $null
    try {
      $c = New-Object System.Net.Sockets.TcpClient
      $c.ReceiveTimeout = 800
      $c.SendTimeout = 800
      $ar = $c.BeginConnect("127.0.0.1", $Port, $null, $null)
      if (-not $ar.AsyncWaitHandle.WaitOne(900)) { continue }
      $c.EndConnect($ar)
      return
    } catch {
    } finally {
      if ($c) { try { $c.Close() } catch {} }
    }
    Start-Sleep -Milliseconds 200
  }
  throw "Прокси NIM не поднялся на 127.0.0.1:$Port за $TimeoutSec с."
}

function Start-NimStringContentProxy {
  param([int]$Port)
  $node = Get-Command node -ErrorAction SilentlyContinue
  if (-not $node) { throw "node не в PATH — нужен для nim-integrate-string-content-proxy.mjs" }
  $scriptPath = Join-Path $PSScriptRoot "nim-integrate-string-content-proxy.mjs"
  if (-not (Test-Path -LiteralPath $scriptPath)) { throw "Не найден $scriptPath" }
  Start-Process -FilePath $node.Source -ArgumentList @("`"$scriptPath`"", "$Port") -WorkingDirectory $PSScriptRoot -WindowStyle Hidden | Out-Null
}

function Get-NimDynamicCompatLimits {
  param([Parameter(Mandatory = $true)][string]$ModelId)
  $l = $ModelId.Trim().ToLowerInvariant()
  while ($l.StartsWith("nvidia_nim/")) {
    $l = $l.Substring("nvidia_nim/".Length)
  }
  if ($l -match 'nemotron-mini|nemotron-3-content-safety|content-safety-reasoning|/gliner|/pii|\b300m\b|nemoretriever|nv-embed|embedcode|cosmos-transfer|cosmos-predict|magpie-tts|voicechat|safety-guard|zeroshot|llama-3\.1-nemotron-safety|transfer2\.5-2b|transfer1-7b|riva-translate|synthetic-video|active-speaker|video-detector|parakeet|whisper|/tts|text-to-speech') {
    return @{
      ContextWindowSize = 4096
      MaxTokens         = 512
      EnvMaxOutput      = 512
      Tier              = "micro"
    }
  }
  if ($l -match '480b|235b|405b|70b|8x7b|8x22b|106b-a47b|\b128k\b|\b1m\b|qwen3-coder|minimax-m2|step-3\.5|solar-10\.7') {
    return @{
      ContextWindowSize = 131072
      MaxTokens         = 8192
      EnvMaxOutput      = 8192
      Tier              = "large"
    }
  }
  return @{
    ContextWindowSize = 16384
    MaxTokens         = 2048
    EnvMaxOutput      = 2048
    Tier              = "standard"
  }
}

function Build-QwenSettingsNim {
  param(
    [string]$Mid,
    [string]$BaseUrl = "https://integrate.api.nvidia.com/v1",
    [switch]$MinimalCompat,
    [hashtable]$CompatLimits = $null
  )

  $nativeTools = Test-NvidiaNimOpenAiNativeToolCalling $Mid

  $extra = [ordered]@{}
  if (-not $MinimalCompat) {
    $lower = $Mid.ToLowerInvariant()
    if ($lower -match "deepseek|terminus") {
      $extra["chat_template_kwargs"] = @{ thinking = $true }
    } elseif ($lower -match "glm|z-ai") {
      $extra["chat_template_kwargs"] = @{ enable_thinking = $true; clear_thinking = $false }
    }
  }
  if (-not $nativeTools) {
    $extra["tool_choice"] = "none"
  }
  $extraHt = @{}
  foreach ($k in $extra.Keys) { $extraHt[$k] = $extra[$k] }

  if ($MinimalCompat) {
    if (-not $CompatLimits) {
      $CompatLimits = Get-NimDynamicCompatLimits $Mid
    }
    $ctxWin = [int]$CompatLimits.ContextWindowSize
    $maxTok = [int]$CompatLimits.MaxTokens
    $tier = [string]$CompatLimits.Tier
    $desc = ("127.0.0.1 прокси → integrate; tier={0} ctx={1} max_out={2}; content string; skipStartupContext; tool_choice=none" -f $tier, $ctxWin, $maxTok)
  } elseif ($nativeTools) {
    $desc = "Прямой integrate.api.nvidia.com/v1; NIM + нативный tool calling (каталог)"
  } else {
    $desc = "Прямой integrate.api.nvidia.com/v1; NIM без tool_choice=auto (extra_body.tool_choice=none)"
  }

  if (-not $MinimalCompat) {
    $maxTok = 81920
    $ctxWin = 131072
  }

  $modelBlock = @{ name = $Mid }
  if ($MinimalCompat) {
    $modelBlock["skipStartupContext"] = $true
  }

  return @{
    modelProviders = @{
      openai = @(
        @{
          id           = $Mid
          name         = ("NVIDIA NIM — {0} (dynamic)" -f $Mid)
          description  = $desc
          envKey       = "OPENAI_API_KEY"
          baseUrl      = $BaseUrl
          generationConfig = @{
            timeout            = 600000
            maxRetries         = 4
            contextWindowSize  = $ctxWin
            extra_body         = $extraHt
            samplingParams     = @{
              temperature = 0.6
              top_p         = 0.95
              max_tokens    = $maxTok
            }
          }
        }
      )
    }
    security = @{
      auth = @{ selectedType = "openai" }
    }
    model    = $modelBlock
  }
}

Remove-Item Env:ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_AUTH_TOKEN -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_DEFAULT_OPUS_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_DEFAULT_SONNET_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:ANTHROPIC_DEFAULT_HAIKU_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_BASE_URL -ErrorAction SilentlyContinue
Remove-Item Env:OPENAI_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:DASHSCOPE_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:QWEN_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:ALIYUN_API_KEY -ErrorAction SilentlyContinue

$rootBase = Join-Path (Split-Path -Parent $PSScriptRoot) "qwen-sessions\_dynamic"
$slug = "{0}-{1}" -f $Provider, (Get-SafeDirName $ModelId)
$sessionRoot = Join-Path $rootBase $slug
$qwenDir = Join-Path $sessionRoot ".qwen"
if (-not (Test-Path -LiteralPath $qwenDir)) {
  New-Item -ItemType Directory -Path $qwenDir -Force | Out-Null
}

if ($Provider -eq "zai") {
  $key = [Environment]::GetEnvironmentVariable("ZAI_API_KEY", "User")
  if ([string]::IsNullOrWhiteSpace($key) -or $key -eq "__SET_ME__") { $key = $env:ZAI_API_KEY }
  if ([string]::IsNullOrWhiteSpace($key) -or $key -eq "__SET_ME__") { $key = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User") }
  if ([string]::IsNullOrWhiteSpace($key) -or $key -eq "__SET_ME__") { $key = $env:OPENAI_API_KEY }
  if ([string]::IsNullOrWhiteSpace($key) -or $key -eq "__SET_ME__") { $key = Read-SecretText "Z.AI API key" }
  $env:OPENAI_API_KEY = $key.Trim()
  $cfg = Build-QwenSettingsZai -Mid $ModelId.Trim()
} else {
  $key = [Environment]::GetEnvironmentVariable("NVIDIA_NIM_API_KEY", "User")
  if ([string]::IsNullOrWhiteSpace($key)) { $key = $env:NVIDIA_NIM_API_KEY }
  if ([string]::IsNullOrWhiteSpace($key)) { $key = Read-SecretText "NVIDIA NIM API key" }
  $env:OPENAI_API_KEY = $key.Trim()
  $midTrim = $ModelId.Trim()
  $script:NimDynamicCompat = $false
  $script:NimCompatLimits = $null
  if (Test-NvidiaNimOpenAiNativeToolCalling $midTrim) {
    $cfg = Build-QwenSettingsNim -Mid $midTrim -BaseUrl "https://integrate.api.nvidia.com/v1"
  } else {
    $script:NimDynamicCompat = $true
    $script:NimCompatLimits = Get-NimDynamicCompatLimits $midTrim
    $px = Get-FreeListenPort
    Start-NimStringContentProxy -Port $px
    Wait-TcpListen -Port $px
    $cfg = Build-QwenSettingsNim -Mid $midTrim -BaseUrl ("http://127.0.0.1:{0}/v1" -f $px) -MinimalCompat -CompatLimits $script:NimCompatLimits
  }
}

$json = ($cfg | ConvertTo-Json -Depth 20)
$settingsPath = Join-Path $qwenDir "settings.json"
[System.IO.File]::WriteAllText($settingsPath, $json, (New-Object System.Text.UTF8Encoding($false)))

$env:API_TIMEOUT_MS = "600000"
if ($Provider -eq "nim" -and $script:NimDynamicCompat -and $script:NimCompatLimits) {
  $env:QWEN_CODE_MAX_OUTPUT_TOKENS = [string]$script:NimCompatLimits.EnvMaxOutput
  $env:QWEN_CODE_EMIT_TOOL_USE_SUMMARIES = "0"
} else {
  $env:QWEN_CODE_MAX_OUTPUT_TOKENS = "81920"
  $env:QWEN_CODE_EMIT_TOOL_USE_SUMMARIES = "1"
}

Ensure-NpmBinInPath
$qwenExe = Resolve-QwenExe
if (-not $qwenExe) {
  throw "Qwen Code CLI не найден. npm install -g @qwen-code/qwen-code@latest"
}

Write-Host ("Qwen Code: {0} / модель {1} → {2}" -f $Provider, $ModelId, $sessionRoot) -ForegroundColor Cyan
if ($Provider -eq "nim" -and $script:NimDynamicCompat -and $script:NimCompatLimits) {
  Write-Host ("NIM (динамика): прокси string-content, skipStartupContext, tier={0} ctx={1} max_out={2} (см. settings.json)." -f $script:NimCompatLimits.Tier, $script:NimCompatLimits.ContextWindowSize, $script:NimCompatLimits.MaxTokens) -ForegroundColor DarkCyan
}

Push-Location $sessionRoot
try {
  & $qwenExe
} finally {
  Pop-Location
}
```

### 11.5. `run-qwen-code-nvidia-nim.ps1`, `run-qwen-code-cloud-zai-glm47.ps1`

См. соответствующие файлы в `scripts/`.

### 11.6. `run-claude-cloud-launcher.ps1`, `run-claude-cloud-session.ps1`

См. `scripts/`. **Важно:** исправьте `$VaultPath`, `$ObsidianExe`, путь к `uv.exe`, при необходимости `$FreeClaudeCodeDir`.

### 11.7. `launcher-provider-models.ps1` (фрагмент: whitelist)

Функция `Test-NvidiaNimOpenAiNativeToolCalling` должна содержать три id каталога:

- `z-ai/glm4.7`
- `qwen/qwen3.5-122b-a10b`
- `deepseek-ai/deepseek-v3.1-terminus`

---

## Быстрый чеклист после миграции

1. Заменить все пути `I:\...` и `C:\Users\chelaxian\...`.
2. Установить Node, Qwen Code, Claude Code, uv, (Bun), Obsidian.
3. Задать `ZAI_API_KEY`, `NVIDIA_NIM_API_KEY` (User).
4. Создать `%USERPROFILE%\.qwen\litellm\` и рабочий LiteLLM на **4000**.
5. `uv sync` в `free-claude-code`.
6. Запустить `create-desktop-shortcuts.ps1` (раздел 10).
7. Проверить: ярлык Qwen → пресет NIM → ответ модели; ярлык Claude → NIM/ Z.AI; `claude-mem` на 37777.

---

*Документ сгенерирован для публикации на GitHub. Не храните секреты в issue и в коммитах.*
