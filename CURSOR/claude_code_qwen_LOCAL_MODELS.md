# Локальный Claude Code + Qwen 3.6 (Dense / MoE) на Windows + RTX 4090 24 ГБ: полный гайд развёртывания

## 0. Что в итоге получается

После развёртывания у вас есть:

1. **Claude Code** в терминале, работающий против **локальной LLM** двумя способами:
   - **llama.cpp** (`llama-server.exe`) → **free-claude-code** (Anthropic-совместимый прокси) → **реальный потоковый** ответ по OpenAI `/v1/chat/completions`.
   - **LM Studio** (локальный сервер на `localhost`, обычно порт **1234**) → Claude Code ходит как к Anthropic-совместимому API (через переменные окружения в сессии).
2. **Интерактивное меню (TUI)** выбора: профиль **dense / moe**, **reasoning on/off**, **размер контекста**, плюс «последние настройки» и «быстрый старт». Также есть пункт **«Свой путь к .gguf…»** для запуска **любой** локальной модели.
3. **Корректные ответы в llama.cpp**: не форсировать `--chat-template qwen` (иначе на части сборок ломается разбор чата и модель «игнорирует» вопрос).
4. **Управление VRAM на RTX 4090**:
   - llama.cpp: `--fit on`, `--fit-target`, кэш KV `q4_0`, разумный batch/ubatch, **dense**: полный GPU, **moe**: умеренный CPU spill экспертов.
   - LM Studio: **`--gpu 1.0`** (все слои на GPU) по умолчанию; запас VRAM под систему — за счёт модели ~19–21 ГБ на 24 ГБ, а не занижением offload. При OOM — fallback по контексту и ступеням **`--gpu`**. **`--parallel 1`**, вывод **`lms`** в логи (`%USERPROFILE%\.qwen-local-setup\lms\`), тихий консольный режим из меню (**`-QuietLmStudioUi 1`**) чтобы не засыпать TUI Claude Code.
5. **Вспомогательные ярлыки**: остановка LM Studio, выгрузка llama.cpp/прокси, логи, **ngrok** для шаринга локального порта.
6. **Локальный прокси без «ложного 503»**: обход системного **HTTP(S)_PROXY** для `127.0.0.1` (**`NO_PROXY`** + снятие переменных прокси в сессии и во временном **`FCC_ENV_FILE`**), иначе httpx может слать запросы к llama через корпоративный прокси.
7. **Reasoning**: согласованность **`--reasoning on`** в llama-server с обработкой **`reasoning_content`** в free-claude-code (без принудительного **`ENABLE_MODEL_THINKING=false`** в override).
8. **claude-mem** (опционально для облачных сценариев; в локальных ярлыках по умолчанию выключен) — с автопочинкой установки.

---

## 1. Аппаратные и системные требования

- **ОС**: Windows 10/11 x64.
- **GPU**: NVIDIA **RTX 4090 (24 ГБ VRAM)** + актуальный драйвер Game Ready / Studio.
- **RAM**: рекомендуется **≥ 32 ГБ** системной памяти.
- **Диск**: десятки ГБ под модели GGUF (dense ~19–20 ГБ файл + запас; MoE — отдельно).
- **Файл подкачки**: при работе LM Studio / mmap иногда всплывает `VirtualLock` / «файл подкачки слишком мал». Имеет смысл **увеличить pagefile** (например **32–64 ГБ** на быстром SSD), если видите подобные ошибки в логах.

---

## 2. Карта портов и процессов (чтобы не путаться)

| Компонент | Порт | Назначение |
|-----------|------|------------|
| LM Studio OpenAI API | **1234** (у вас в ярлыках) | `/v1/models`, `/v1/chat/completions` |
| llama.cpp dense | **1240** (если в `run-claude-local-session.ps1` не задавали иной `-Port` при конфликте с 1234) | OpenAI-совместимый `/v1/*` |
| llama.cpp moe | **1241** | то же |
| free-claude-code (dense) | **8084** | Anthropic-совместимый прокси к llama.cpp |
| free-claude-code (moe) | **8085** | то же |
| claude-mem worker UI | **37777** | локальный observer |

---

## 3. Установка базового ПО (без ключей в гайде)

### 3.1. Git

Установите Git for Windows (нужно для `free-claude-code` и удобства обновлений).

### 3.2. Node.js LTS + npm

- Установите Node.js LTS с [официального сайта Node.js](https://nodejs.org/).
- Проверка:

```powershell
node -v
npm -v
```

### 3.3. Bun (нужен для runtime-команд `claude-mem`)

Установка по документации Bun для Windows. Проверка:

```powershell
bun -v
```

Убедитесь, что `~\.bun\bin` попадает в `PATH` (установщик обычно делает это).

### 3.4. Python toolchain: `uv` (для free-claude-code)

Установите `uv` с [официальной документации Astral `uv`](https://docs.astral.sh/uv/).
Проверка:

```powershell
uv --version
```

> В ваших скриптах встречается путь вида `C:\Users\<User>\.local\bin\uv.exe` — на новой машине путь может отличаться. Либо добавьте `uv` в `PATH`, либо поправьте строку в `run-claude-local-session.ps1` / `run-claude-cloud-session.ps1`.

### 3.5. NVIDIA CUDA / cuDNN

Для **готовых бинарников llama.cpp под CUDA** отдельная установка CUDA Toolkit часто **не обязательна**, но **драйвер NVIDIA** обязателен. Если бинарь требует CUDA DLL — скрипт `install-llamacpp-win-cuda.ps1` подтягивает **cudart-пакет** из релизов `llama.cpp`.

### 3.6. LM Studio

1. Установите LM Studio с официального сайта.
2. Скачайте в LM Studio модели (см. раздел 6).
3. Убедитесь, что доступен **`lms.exe`** (CLI). Типичный путь (портable-установка):

`...\LM Studio\resources\app\.webpack\lms.exe`

### 3.7. ngrok (только для ярлыков Share Local)

1. Установите ngrok.
2. Выполните **однократную** аутентификацию по документации ngrok (токен храните локально, **не** вставляйте в репозиторий).

Проверка:

```powershell
ngrok version
```

### 3.8. Claude Code (CLI)

Установите **Claude Code** по официальной инструкции Anthropic (команда может называться `claude` / `claude.cmd` в `%APPDATA%\npm\`).

Проверка:

```powershell
where.exe claude
claude --version
```

---

## 4. Структура каталогов (рекомендуемая)

Пример (замените диск/папки):

```text
D:\qwen-local-setup\          # этот репозиторий / ваш «проект»
D:\qwen-local-setup\bin\llama.cpp\llama-server.exe
D:\LMStudio\                  # portable LM Studio (как у вас I:\LMStudio)
D:\Models\Qwen-Local\         # GGUF файлы
%USERPROFILE%\.qwen-local-setup\   # состояние меню, логи lms-load, и т.д.
```

Создайте папку логов (если ярлык «Logs» указывает на неё):

```powershell
New-Item -ItemType Directory -Force -Path "D:\qwen-local-setup\logs" | Out-Null
```

---

## 5. Установка llama.cpp (Windows CUDA бинарник)

В репозитории есть скрипт:

`scripts/install-llamacpp-win-cuda.ps1`

Он:

- качает **последний релиз** `llama-*-bin-win-cuda-*-x64.zip` с GitHub `ggml-org/llama.cpp`;
- раскладывает в `I:\qwen-local-setup\bin\llama.cpp\` (по умолчанию);
- докачивает **cudart** zip при отсутствии DLL.

Запуск:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\qwen-local-setup\scripts\install-llamacpp-win-cuda.ps1" `
  -InstallDir "D:\qwen-local-setup\bin\llama.cpp"
```

Проверка:

```powershell
Test-Path "D:\qwen-local-setup\bin\llama.cpp\llama-server.exe"
```

---

## 6. Модели GGUF (ваш сетап RTX 4090 24 ГБ)

### 6.1. Рекомендованные квантовки (как в ваших скриптах)

| Профиль | Архитектура | Файл (пример имени) | Роль |
|---------|-------------|----------------------|------|
| **dense** | Qwen3.6 **27B** dense | `...-Q5_K_P.gguf` | Основной «качество» при ~24 ГБ VRAM |
| **moe** | Qwen3.6 **35B-A3B** MoE | `...-Q4_K_P.gguf` (или `@q4_k_m` в LM Studio) | Быстрее/экономнее VRAM за счёт MoE |

> **Не использовать** «слишком тяжёлые» варианты для dense на 24 ГБ без запаса (например Q6), если цель — стабильность Windows + запас под DWM.

### 6.2. Пути к файлам в `run-claude-local-session.ps1`

Сейчас зашито (замените на свои):

- dense: `I:\Models\Qwen-Local\Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-Q5_K_P.gguf`
- moe: `I:\Models\Qwen-Local\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf`

LM Studio использует **идентификаторы моделей** из каталога моделей; скрипт подбирает `model id` через `/v1/models`.

> Начиная с актуальной версии меню, эти «зашитые» пути — это **пресеты**. В ярлыках **Claude Code (Local …)** можно выбрать **«Свой путь к .gguf…»**, и тогда сессия запустится с указанным файлом без правки скрипта.

---

## 7. free-claude-code (прокси Anthropic → локальный OpenAI)

### 7.1. Получить код

```powershell
git clone https://github.com/Alishahryar1/free-claude-code.git "D:\qwen-local-setup\free-claude-code"
```

(Апстрим — публичный репозиторий [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code); при необходимости клонируйте свой форк и подставьте его URL.)

### 7.2. Установить зависимости через `uv`

```powershell
cd "D:\qwen-local-setup\free-claude-code"
uv sync
```

### 7.3. Секреты

- **Не коммитьте** `.env` с реальными ключами.
- Для **локального** режима через прокси в скрипте используется **локальный** токен-заглушка (`freecc`) — это не секрет удалённого API, но и не публикуйте его как «безопасность».

### 7.4. Ключевое изменение провайдера llama.cpp (стриминг)

Файл: `free-claude-code/providers/llamacpp/client.py`

Смысл: провайдер переведён на **OpenAI Chat Completions** + **токеновый стриминг**, и при выключенном thinking используется `ReasoningReplayMode.DISABLED`.

В том же файле дополнительно реализован обход для **списка моделей**: метод **`list_model_ids`** ходит **прямым `httpx` GET** на **`/models`** (без цепочки OpenAI SDK), потому что отдельные сборки `llama-server` дают непредсказуемые ответы на «стандартную» проверку. Полный перечень правок по репозиторию — в **§7.5** (таблица и окружение).

Ниже — **фрагмент** (только **`_build_request_body`** и импорты); он не отражает весь текущий класс целиком.

```python
"""Llama.cpp provider via OpenAI-compatible ``/chat/completions`` (token streaming).

Some ``llama-server`` builds buffer the Anthropic-native ``/v1/messages`` SSE stream until
generation finishes, so Claude Code shows the full reply at once. The OpenAI chat path
streams chunk-by-chunk as tokens are generated.
"""

from __future__ import annotations

from typing import Any

from config.constants import ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS
from core.anthropic import ReasoningReplayMode, build_base_request_body
from providers.base import ProviderConfig
from providers.defaults import LLAMACPP_DEFAULT_BASE
from providers.openai_compat import OpenAIChatTransport


class LlamaCppProvider(OpenAIChatTransport):
    """Local llama-server using OpenAI Chat Completions + real-time deltas."""

    def __init__(self, config: ProviderConfig):
        super().__init__(
            config,
            provider_name="LLAMACPP",
            base_url=config.base_url or LLAMACPP_DEFAULT_BASE,
            api_key=config.api_key or "llamacpp",
        )

    def _build_request_body(
        self, request: Any, thinking_enabled: bool | None = None
    ) -> dict[str, Any]:
        thinking_enabled = self._is_thinking_enabled(request, thinking_enabled)
        replay = (
            ReasoningReplayMode.REASONING_CONTENT
            if thinking_enabled
            else ReasoningReplayMode.DISABLED
        )
        return build_base_request_body(
            request,
            default_max_tokens=ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS,
            reasoning_replay=replay,
        )
```

После изменений имеет смысл прогнать тесты:

```powershell
cd "D:\qwen-local-setup\free-claude-code"
uv run pytest tests/providers/test_llamacpp.py
```

### 7.5. Патчи free-claude-code и локальный запуск (прокси, reasoning, диагностика 503)

Ниже — правки, которые держат в рабочем состоянии связку **`run-claude-local-session.ps1`** + каталог **`free-claude-code/`** внутри `qwen-local-setup`. При обновлении апстрима free-claude-code имеет смысл заново пройтись по списку и при необходимости перенести дифф.

**Изменения в Python (`free-claude-code/`)**

| Область | Файл | Зачем |
|--------|------|--------|
| Список моделей | `providers/llamacpp/client.py` | **`list_model_ids`** через прямой **`httpx` GET** `/models`: часть сборок `llama-server` даёт нестабильный ответ при обходе через OpenAI SDK. |
| Валидация при старте | `config/settings.py` | Поле **`fcc_skip_configured_model_validation`** и env **`FCC_SKIP_CONFIGURED_MODEL_VALIDATION`**. |
| Старт приложения | `api/runtime.py` | При включённом флаге пропускается **`validate_configured_models`**, чтобы старт не зависел от «идеального» `GET /models` и совпадения ID. |

**Временный `FCC_ENV_FILE` (лаунчер)**

`Ensure-FreeClaudeCodeProxyLocal` записывает override в **`%USERPROFILE%\.qwen-local-setup\fcc-local-override.<timestamp>.env`** и задаёт **`FCC_ENV_FILE`** перед **`uv run`**, чтобы корневой **`.env`** репозитория (часто устаревший **`LLAMACPP_BASE_URL`**, **`ENABLE_WEB_SERVER_TOOLS=true`** и т.д.) не перетирал актуальные значения.

Типичные ключи в override:

- **`LLAMACPP_BASE_URL`** — фактический базовый URL llama-server (например `http://127.0.0.1:1240/v1`).
- **`MODEL`** — строка вида `llamacpp/<имя файла .gguf>`.
- **`ANTHROPIC_AUTH_TOKEN`** — тот же токен, что выставляет лаунчер для Claude Code (локально часто заглушка **`freecc`**).
- **`MESSAGING_PLATFORM=none`**
- **`ENABLE_WEB_SERVER_TOOLS=false`** — для Claude Code с локальными tools лишний веб-слой не нужен и может мешать.
- **`FCC_SKIP_CONFIGURED_MODEL_VALIDATION=true`**
- **`NO_PROXY`** — строка **точно как в скрипте** (и в override совпадает с **`Set-LlamaLocalBypassProxyEnv`**):

  `127.0.0.1,127.0.0.1:1234,127.0.0.1:1240,127.0.0.1:1241,127.0.0.1:8084,127.0.0.1:8085,localhost,::1`

- **`HTTP_PROXY=`**, **`HTTPS_PROXY=`**, **`ALL_PROXY=`** — пустые значения в файле override; плюс в PowerShell переменные с теми же именами **удаляются** (`Remove-Item Env:...`), чтобы не тянуть прокси из родительской сессии.

**HTTP(S)-прокси и ложный 503 на localhost**

Если в окружении заданы **`HTTP_PROXY` / `HTTPS_PROXY`**, **httpx** внутри прокси может отправлять даже **`http://127.0.0.1:1240/...`** через системный прокси. В **`free-claude-code/server.log`** это проявляется как **`503 Service Unavailable`**, **пустое тело** ответа и заголовок **`proxy-connection: close`** на **`POST .../v1/chat/completions`** (и иногда **`GET /models`**). В UI Claude Code это часто отображается как **`Error code: 503`** с **`request_id`**, хотя access log uvicorn может показывать **200** на другой фазе — ориентируйтесь на **`server.log`** и **`request_id`**.

В **`run-claude-local-session.ps1`** функция **`Set-LlamaLocalBypassProxyEnv`**:

- задаёт **`NO_PROXY`** (см. строку выше);
- снимает **`HTTP_PROXY`**, **`HTTPS_PROXY`**, **`ALL_PROXY`** и те же имена **в нижнем регистре**.

Она вызывается в начале ветки **`Runtime -eq "llamacpp"`** и в **`Ensure-FreeClaudeCodeProxyLocal`** перед **`Start-Process`** с uvicorn, чтобы дочерний процесс наследовал корректное окружение.

**Порты прокси:** **`8084`** для профиля **dense**, **`8085`** для **moe** (передаётся в **`Ensure-FreeClaudeCodeProxyLocal -ProxyPort`**). Перед стартом слушающий процесс на этом порту принудительно останавливается, чтобы не оставался старый uvicorn с устаревшим **`FCC_ENV_FILE`** / **`MODEL`**.

**Reasoning (`reasoning_content`)**

- Режим в llama задаётся **`--reasoning off|on`** из меню (**`-ReasoningMode`**).
- При **`--reasoning on`** поток от llama содержит **`reasoning_content`**. Если в override прокси принудительно выключить thinking (например **`ENABLE_MODEL_THINKING=false`** «для всех»), прокси может отбрасывать нужные дельты → **пустой или битый ответ** в Claude Code. В актуальной схеме ключ **`ENABLE_MODEL_THINKING`** в **`fcc-local-override*.env` не задаётся**: в коде лаунчера явно оставлено поведение по умолчанию прокси, чтобы не ломать **`reasoning_content`**. Логика **`ReasoningReplayMode`** в провайдере — как в §7.4.

**Прочая стабильность лаунчера**

- Дымовая проверка прокси **`Test-ProxyQuickMessage`**: **`POST`** на **`<base прокси>/v1/messages`**, тело — минимальный Anthropic-совместимый JSON (**`stream: true`**, одно user-сообщение **`ping`**), заголовки **`Authorization: Bearer …`**, **`anthropic-version: 2023-06-01`**, **`Invoke-WebRequest`** с **`-UseBasicParsing`**. **`Invoke-RestMethod`** для SSE не используется: он ожидает JSON и даёт сбои или некорректное поведение на **`text/event-stream`**. После успешного ответа лаунчер может вывести ориентир **ttfb** (время до первого байта) в консоль.
- **`Assert-LlamaServerUsesVram`**: разбор строк лога **`CUDA0 model buffer`** и сверка с **`nvidia-smi`** (исправленные регексы под реальный вывод).
- **`Ensure-LlamaCppServer`**: надёжное извлечение **`n_ctx`** из лога; **`catch`** только для явного **`FATAL_NCTX_TOO_LARGE`**.
- **`run-claude-local-menu.ps1`**: **`try/catch`** вокруг запуска сессии, вывод текста ошибки и пауза **Enter**, чтобы окно не закрывалось без сообщения при сбое.

**Где смотреть логи**

- Основная диагностика прокси: **`server.log`** в каталоге репозитория **`free-claude-code`** (у типичного клона путь вида **`I:\qwen-local-setup\free-claude-code\server.log`**; на другой машине замените корень). Формат — JSON-строки **loguru**, ищите **`request_id`**, **`LLAMACPP_STREAM`**, **`LLAMACPP_ERROR`**, строки **`HTTP Response: POST http://127.0.0.1:...`**.
- Вывод процесса uvicorn: **`%USERPROFILE%\.qwen-local-setup\free-claude-code.local.*.out.log`** и **`.err.log`** — чаще всего только старт **uvicorn**; исключения Python/трассировки при **`LOG_API_ERROR_TRACEBACKS=true`** тоже полезно смотреть в **`server.log`**.
- Лог **llama-server** (аргумент **`--log-file`** в **`Ensure-LlamaCppServer`**): **`%TEMP%\llama-server-<порт>.log`** (например **`llama-server-1240.log`** / **`1241.log`**).

**Дополнительная отладка прокси**

В override или в **`.env`** можно временно включить **`LOG_API_ERROR_TRACEBACKS=true`** (см. **`free-claude-code/config/settings.py`**, **`README.md`** / **`.env.example`**) — в лог попадут полные traceback при ошибках API. Не оставляйте включённым постоянно на продакшене: больше шума и чувствительных деталей в файле.

---

## 8. Параметры llama.cpp (`llama-server`) для вашего сетапа

Ниже — логика из `Ensure-LlamaCppServer` в `run-claude-local-session.ps1`:

- **`--jinja`**: шаблоны из GGUF.
- **НЕ** передаётся `--chat-template qwen` (важно для релевантности).
- **`--reasoning`**: `off` или `on` из меню.
- **`--fit on`** + **`--fit-target`**: **3072 MiB** (dense) / **2560 MiB** (moe) — запас под Windows.
- **Dense**: `--batch-size 512`, `--ubatch-size 128`, `--n-gpu-layers all`, KV `q4_0`.
- **MoE**: `--batch-size 2048`, `--ubatch-size 512`, `--n-cpu-moe 6` (архитектурно допустимый spill).
- **Анти-«подмешивание старых промптов»**: `--no-cache-prompt`, `--cache-ram 0`.

Порты dense/moe см. раздел 2.

Связка с прокси и переменными окружения (**обход HTTP-прокси для localhost**, **`FCC_ENV_FILE`**, reasoning) — раздел **7.5**.

---

## 9. Параметры LM Studio / `lms load` для вашего сетапа

Ключевые идеи в `run-claude-local-session.ps1`:

- **`Get-RecommendLmGpuOffload`**: по умолчанию **`1.0`**; занижение только если оценка размера GGUF+оверход не влезает в VRAM. Запас под Windows — не через искусственное **`--gpu 0.9`**, а за счёт выбора модели по объёму. Для **кастомного `.gguf`** оценка VRAM берётся по вашему файлу (если указан в меню).
- **Загрузка модели**: `--parallel 1 --yes` (снижает `n_parallel` и память). Команды **`lms`** запускаются с перенаправлением stdout/stderr в **`%USERPROFILE%\.qwen-local-setup\lms\`**, чтобы не смешивать вывод с Claude Code.
- **Fallback при ошибке загрузки**: уменьшение контекста и ступени **`--gpu`** (например 1.0 → 0.98 → … → 0.85).
- Ярлык **LM Studio** через меню передаёт **`-QuietLmStudioUi 1`**: строки лаунчера пишутся в **`%USERPROFILE%\.qwen-local-setup\lmstudio-session-launcher.log`** и **дублируются в ту же консоль**, что и интерактивное меню (отдельное окно «только логи» не создаётся). **LM Studio.exe** стартует через **`cmd /c start /D …`**, чтобы Electron не цеплялся к консоли. **Claude Code** запускается **в отдельном** окне PowerShell через **`invoke-claude-in-console.ps1`**; после выхода из Claude в исходном окне выполняется **`finally`** (выгрузка модели / остановка сервера).
- Перед preload: обычно `unload --all` + пауза (анти-«хвосты» прошлой сессии). Если выбранный `.gguf` **уже активен** (виден в `GET /v1/models`), лаунчер **может пропустить** `unload`/preload/force-load и сразу запускать Claude Code.

Логи загрузки: `%USERPROFILE%\.qwen-local-setup\lms-load.log`.

---

## 10. Меню запуска (Claude Code Local)

Файл: `scripts/run-claude-local-menu.ps1`

- Меню оформлено как TUI в стиле «облачных» ярлыков (рамки + баннер). Баннер зависит от рантайма: **LLAMA.CPP** или **LM STUDIO** (см. `scripts/launcher-tui.ps1`).
- Сохраняет последний выбор в `%USERPROFILE%\.qwen-local-setup\claude-local-menu.<runtime>.last.json` (включая `custom_model_path`, если вы указывали свой `.gguf`).
- В ручном режиме добавлен пункт **«Свой путь к .gguf…»**. После ввода пути меню попросит выбрать «профиль тюнинга» (Dense/MoE) — это влияет на список доступных `ctx` и параметры запуска (batch/ubatch/fit-target).
- Для `llamacpp` вызывает `run-claude-local-session.ps1` с `-ShowLlamaConsole 1`.
- Для `lmstudio` — с `-StartLMStudioGui 1` и `-Port 1234` (как в ярлыке).
- Ошибки запуска сессии перехватываются **`try/catch`**: сообщение выводится в консоль, затем пауза **Enter**, чтобы окно PowerShell не исчезало сразу при сбое.

---

## 11. Ярлыки рабочего стола: точные свойства (как у вас сейчас)

| Ярлык | Target | Arguments | Working directory |
|------|--------|-----------|-------------------|
| **Share Local (MoE + ngrok).lnk** | `C:\Program Files\PowerShell\7\powershell.cmd` | `-NoProfile -ExecutionPolicy Bypass -File "I:\qwen-local-setup\scripts\share-ngrok-local.ps1" -Profile moe -LMStudioRoot "I:\LMStudio" -Port 1234` | `I:\qwen-local-setup` |
| **Claude Code (Local llama.cpp).lnk** | `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` | `-NoProfile -ExecutionPolicy Bypass -File "I:\qwen-local-setup\scripts\run-claude-local-menu.ps1" -Runtime llamacpp` | `I:\qwen-local-setup` |
| **Unload llama.cpp VRAM.lnk** | `powershell.exe` | `-NoProfile -ExecutionPolicy Bypass -File "I:\qwen-local-setup\scripts\unload-llamacpp-and-proxies.ps1"` | `I:\qwen-local-setup` |
| **Claude Code (Local LM Studio).lnk** | `powershell.exe` | `-NoProfile -ExecutionPolicy Bypass -File "I:\qwen-local-setup\scripts\run-claude-local-menu.ps1" -Runtime lmstudio -Port 1234` | `I:\qwen-local-setup` |
| **Stop Local Qwen (VRAM).lnk** | `powershell.exe` | `-NoProfile -ExecutionPolicy Bypass -File I:\qwen-local-setup\scripts\stop-local-qwen-now.ps1` | `I:\qwen-local-setup` |
| **Logs (Qwen Local).lnk** | `C:\WINDOWS\explorer.exe` | `I:\qwen-local-setup\logs` | *(пусто)* |
| **Share Local (Dense + ngrok).lnk** | `C:\Program Files\PowerShell\7\powershell.cmd` | `-NoProfile -ExecutionPolicy Bypass -File "I:\qwen-local-setup\scripts\share-ngrok-local.ps1" -Profile dense -LMStudioRoot "I:\LMStudio" -Port 1234` | `I:\qwen-local-setup` |

> **Важно про Share Local**: в `share-ngrok-local.ps1` параметр `-ContextLength 65536` может быть **несовместим с VRAM 24 ГБ** для выбранной модели. На новой установке начните с **16384/24576** (как в основном лаунчере) и поднимайте осторожно.

### 11.1. Скрипт генерации ярлыков (перенос на новую машину)

Сохраните как `recreate-desktop-shortcuts.ps1` и отредактируйте `$Root`, `$LMStudioRoot`, `$Desktop`:

```powershell
$Root         = "D:\qwen-local-setup"
$LMStudioRoot = "D:\LMStudio"
$Desktop      = [Environment]::GetFolderPath("Desktop")
$ws           = New-Object -ComObject WScript.Shell

function New-Shortcut {
  param(
    [string]$Path,
    [string]$TargetPath,
    [string]$Arguments,
    [string]$WorkingDirectory
  )
  $s = $ws.CreateShortcut($Path)
  $s.TargetPath = $TargetPath
  $s.Arguments = $Arguments
  $s.WorkingDirectory = $WorkingDirectory
  $s.Save()
}

# PowerShell 7 (если установлен) — как у вас для ngrok
$pwshCmd = "C:\Program Files\PowerShell\7\powershell.cmd"
$ps51    = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

New-Shortcut -Path "$Desktop\Share Local (MoE + ngrok).lnk" `
  -TargetPath $pwshCmd `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\share-ngrok-local.ps1`" -Profile moe -LMStudioRoot `"$LMStudioRoot`" -Port 1234" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Claude Code (Local llama.cpp).lnk" `
  -TargetPath $ps51 `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\run-claude-local-menu.ps1`" -Runtime llamacpp" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Unload llama.cpp VRAM.lnk" `
  -TargetPath $ps51 `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\unload-llamacpp-and-proxies.ps1`"" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Claude Code (Local LM Studio).lnk" `
  -TargetPath $ps51 `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\run-claude-local-menu.ps1`" -Runtime lmstudio -Port 1234" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Stop Local Qwen (VRAM).lnk" `
  -TargetPath $ps51 `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\stop-local-qwen-now.ps1`"" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Logs (Qwen Local).lnk" `
  -TargetPath "$env:WINDIR\explorer.exe" `
  -Arguments "$Root\logs" `
  -WorkingDirectory $Root

New-Shortcut -Path "$Desktop\Share Local (Dense + ngrok).lnk" `
  -TargetPath $pwshCmd `
  -Arguments "-NoProfile -ExecutionPolicy Bypass -File `"$Root\scripts\share-ngrok-local.ps1`" -Profile dense -LMStudioRoot `"$LMStudioRoot`" -Port 1234" `
  -WorkingDirectory $Root
```

---

## 12. Полные тексты вспомогательных скриптов

> **Как поддерживать гайд синхронным с репозиторием:** файлы ниже продублированы в этом документе специально для сценария «один Markdown на новый ПК». После правок в `scripts/*.ps1` пересоберите вставки командой:
>
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File "D:\qwen-local-setup\scripts\sync-local-setup-guide-embed.ps1"
> ```
>
> (Замените `D:\qwen-local-setup` на корень вашей копии.) Скрипт **не** использует `Regex.Replace` для вставки кода — иначе символы `$` в PowerShell ломают файл.
>
> **Ярлыки `.lnk`:** это бинарные объекты Windows; в гайде они описаны таблицей в **§11** и воспроизводятся скриптом из **§11.1** (целевой путь, аргументы, рабочая папка).

### 12.1. `scripts/ensure-streaming-friendly-terminal.ps1`

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

### 12.2. `scripts/launcher-tui.ps1`

```powershell
# TUI-меню для лаунчеров Qwen / Claude (рамки, прокрутка, баннер).

function Set-LauncherTuiConsole {
  try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
  } catch {}
}

function Get-LauncherTuiBox {
  return @{
    TL = [char]0x2554; TR = [char]0x2557; BL = [char]0x255A; BR = [char]0x255D
    H  = [char]0x2550; V  = [char]0x2551
    LJ = [char]0x2560; RJ = [char]0x2563
  }
}

# В PowerShell нельзя писать [char] * N — только ([string][char]) * N
function Repeat-TuiChar {
  param(
    [char]$Ch,
    [int]$Count
  )
  if ($Count -lt 1) { return "" }
  return ([string]$Ch) * $Count
}

function Write-TuiRow {
  param(
    [Parameter(Mandatory = $true)]
    [AllowEmptyString()]
    [string]$Text,
    [Parameter(Mandatory = $true)][int]$InnerWidth,
    [System.ConsoleColor]$Fg = "Gray"
  )
  $b = Get-LauncherTuiBox
  if ($Text.Length -gt $InnerWidth) {
    $Text = $Text.Substring(0, [Math]::Max(0, $InnerWidth - 1)) + [char]0x2026
  } else {
    $Text = $Text.PadRight($InnerWidth)
  }
  Write-Host ($b.V + $Text + $b.V) -ForegroundColor $Fg
}

function Write-TuiBannerQwen {
  param([int]$InnerWidth)
  # Тот же визуальный язык, что и у Claude (FIGlet «ANSI Shadow»), по центру как CLAUDE (ширина 59).
  $raw = @(
    " ██████╗ ██╗    ██╗███████╗███╗   ██╗"
    "██╔═══██╗██║    ██║██╔════╝████╗  ██║"
    "██║   ██║██║ █╗ ██║█████╗  ██╔██╗ ██║"
    "██║▄▄ ██║██║███╗██║██╔══╝  ██║╚██╗██║"
    "╚██████╔╝╚███╔███╔╝███████╗██║ ╚████║"
    " ╚══▀▀═╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝"
  )
  $bannerW = 59
  foreach ($ln in $raw) {
    $len = $ln.Length
    if ($len -ge $bannerW) {
      $row = $ln.Substring(0, $bannerW)
    } else {
      $padL = [int][Math]::Floor(($bannerW - $len) / 2)
      $padR = $bannerW - $len - $padL
      $row = ((" " * $padL) + $ln + (" " * $padR))
    }
    Write-TuiRow -Text $row -InnerWidth $InnerWidth -Fg DarkCyan
  }
}

function Write-TuiBannerClaude {
  param([int]$InnerWidth)
  $lines = @(
    "   ██████╗██╗     ██╗      █████╗ ██╗   ██╗██████╗ ███████╗",
    "  ██╔════╝██║     ██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝",
    "  ██║     ██║     ██║     ███████║██║   ██║██║  ██║█████╗  ",
    "  ██║     ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  ",
    "  ╚██████╗███████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗",
    "   ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝"
  )
  foreach ($ln in $lines) {
    Write-TuiRow -Text $ln -InnerWidth $InnerWidth -Fg DarkMagenta
  }
}

function Write-TuiBannerLlamaCpp {
  param([int]$InnerWidth)
  # Ширина баннера ~59, как у Claude/Qwen
  $lines = @(
    " ██╗     ██╗      █████╗ ███╗   ███╗ █████╗      ██████╗██████╗ ██████╗ "
    " ██║     ██║     ██╔══██╗████╗ ████║██╔══██╗    ██╔════╝██╔══██╗██╔══██╗"
    " ██║     ██║     ███████║██╔████╔██║███████║    ██║     ██████╔╝██████╔╝"
    " ██║     ██║     ██╔══██║██║╚██╔╝██║██╔══██║    ██║     ██╔═══╝ ██╔═══╝ "
    " ███████╗███████╗██║  ██║██║ ╚═╝ ██║██║  ██║    ╚██████╗██║     ██║     "
    " ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝     ╚═════╝╚═╝     ╚═╝     "
  )
  foreach ($ln in $lines) {
    Write-TuiRow -Text $ln -InnerWidth $InnerWidth -Fg DarkGreen
  }
}

function Write-TuiBannerLMStudio {
  param([int]$InnerWidth)
  $lines = @(
    " ██╗     ███╗   ███╗    ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗ "
    " ██║     ████╗ ████║    ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗"
    " ██║     ██╔████╔██║    ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║"
    " ██║     ██║╚██╔╝██║    ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║"
    " ███████╗██║ ╚═╝ ██║    ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝"
    " ╚══════╝╚═╝     ╚═╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ "
  )
  foreach ($ln in $lines) {
    Write-TuiRow -Text $ln -InnerWidth $InnerWidth -Fg DarkCyan
  }
}

function Show-TuiFramedMenu {
  param(
    [ValidateSet("Qwen", "Claude", "LlamaCpp", "LMStudio")]
    [string]$AppBrand,
    [Parameter(Mandatory = $true)][string]$Title,
    [string]$Subtitle = "",
    [Parameter(Mandatory = $true)][object[]]$Items,
    [int]$InitialIndex = 0,
    [int]$MaxVisible = 12,
    # Exit = Esc полностью отменяет (как главное меню). Back = Esc вернуться к предыдущему шагу (мастер «другая модель»).
    [ValidateSet("Exit", "Back")]
    [string]$EscapeAction = "Exit"
  )

  Set-LauncherTuiConsole
  $b = Get-LauncherTuiBox
  $win = $Host.UI.RawUI.WindowSize
  $frameW = [Math]::Min(90, [Math]::Max(54, $win.Width - 2))
  $inner = $frameW - 2
  $n = $Items.Count
  if ($n -lt 1) {
    throw "Show-TuiFramedMenu: список Items пуст."
  }
  $idx = [Math]::Max(0, [Math]::Min($InitialIndex, $n - 1))
  $heightCap = [Math]::Max(6, $win.Height - 20)
  $visible = [Math]::Max(4, [Math]::Min($MaxVisible, [Math]::Min($n, $heightCap)))
  # При dot-source $script: — область вызывающего файла; скролл ломался. Hashtable — общий изменяемый объект.
  $scroll = @{ Top = 0 }

  function Sync-TuiScroll {
    if ($idx -lt $scroll.Top) { $scroll.Top = $idx }
    $maxTop = [Math]::Max(0, $n - $visible)
    if ($idx -ge $scroll.Top + $visible) { $scroll.Top = $idx - $visible + 1 }
    if ($scroll.Top -gt $maxTop) { $scroll.Top = $maxTop }
    if ($scroll.Top -lt 0) { $scroll.Top = 0 }
  }

  function Redraw-TuiMenu {
    Sync-TuiScroll
    Clear-Host
    Write-Host ($b.TL + (Repeat-TuiChar $b.H ($frameW - 2)) + $b.TR) -ForegroundColor Cyan
    Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
    switch ($AppBrand) {
      "Qwen" { Write-TuiBannerQwen -InnerWidth $inner }
      "Claude" { Write-TuiBannerClaude -InnerWidth $inner }
      "LlamaCpp" { Write-TuiBannerLlamaCpp -InnerWidth $inner }
      "LMStudio" { Write-TuiBannerLMStudio -InnerWidth $inner }
      default { Write-TuiBannerClaude -InnerWidth $inner }
    }
    Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
    Write-Host ($b.LJ + (Repeat-TuiChar $b.H $inner) + $b.RJ) -ForegroundColor DarkCyan
    Write-TuiRow -Text (" " + $Title.Trim()) -InnerWidth $inner -Fg White
    if (-not [string]::IsNullOrWhiteSpace($Subtitle)) {
      Write-TuiRow -Text (" " + $Subtitle.Trim()) -InnerWidth $inner -Fg DarkGray
    }
    Write-Host ($b.LJ + (Repeat-TuiChar $b.H $inner) + $b.RJ) -ForegroundColor DarkCyan
    Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
    for ($r = 0; $r -lt $visible; $r++) {
      $i = $scroll.Top + $r
      if ($i -ge $n) {
        Write-TuiRow -Text "" -InnerWidth $inner
        continue
      }
      $lbl = [string]$Items[$i].Label
      $mark = if ($i -eq $idx) { ("  {0} " -f [char]0x25B6) } else { "     " }
      $row = $mark + $lbl
      $fg = if ($i -eq $idx) { "Yellow" } else { "Gray" }
      Write-TuiRow -Text $row -InnerWidth $inner -Fg $fg
    }
    Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
    $escHint = if ($EscapeAction -eq "Back") { "Esc — назад" } else { "Esc — выход" }
    $hint = ("  {0}{1}  выбор   Enter — OK   {2}   Home/End   PgUp/PgDn" -f [char]0x2191, [char]0x2193, $escHint)
    Write-TuiRow -Text $hint -InnerWidth $inner -Fg DarkGray
    if ($n -gt $visible) {
      $pg = ("  строки {0}-{1} из {2}" -f ($scroll.Top + 1), ([Math]::Min($scroll.Top + $visible, $n)), $n)
      Write-TuiRow -Text $pg -InnerWidth $inner -Fg DarkCyan
    }
    Write-Host ($b.BL + (Repeat-TuiChar $b.H ($frameW - 2)) + $b.BR) -ForegroundColor Cyan
  }

  $scroll.Top = 0
  Sync-TuiScroll
  [Console]::CursorVisible = $false
  try {
    Redraw-TuiMenu
    while ($true) {
      $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
      switch ($key.VirtualKeyCode) {
        38 {
          if ($idx -gt 0) { $idx-- }
          Redraw-TuiMenu
        }
        40 {
          if ($idx -lt $n - 1) { $idx++ }
          Redraw-TuiMenu
        }
        33 {
          $idx = [Math]::Max(0, $idx - $visible)
          Redraw-TuiMenu
        }
        34 {
          $idx = [Math]::Min($n - 1, $idx + $visible)
          Redraw-TuiMenu
        }
        36 {
          $idx = 0
          Redraw-TuiMenu
        }
        35 {
          $idx = $n - 1
          Redraw-TuiMenu
        }
        13 { return $Items[$idx] }
        27 {
          if ($EscapeAction -eq "Back") {
            return [pscustomobject]@{ __menuBack = $true }
          }
          return $null
        }
      }
    }
  } finally {
    [Console]::CursorVisible = $true
  }
}

function Show-TuiWaitFrame {
  param(
    [ValidateSet("Qwen", "Claude", "LlamaCpp", "LMStudio")]
    [string]$AppBrand,
    [Parameter(Mandatory = $true)][string]$Message
  )
  Set-LauncherTuiConsole
  $b = Get-LauncherTuiBox
  $win = $Host.UI.RawUI.WindowSize
  $frameW = [Math]::Min(82, [Math]::Max(50, $win.Width - 4))
  $inner = $frameW - 2
  Clear-Host
  Write-Host ($b.TL + (Repeat-TuiChar $b.H ($frameW - 2)) + $b.TR) -ForegroundColor Cyan
  Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
  switch ($AppBrand) {
    "Qwen" { Write-TuiBannerQwen -InnerWidth $inner }
    "Claude" { Write-TuiBannerClaude -InnerWidth $inner }
    "LlamaCpp" { Write-TuiBannerLlamaCpp -InnerWidth $inner }
    "LMStudio" { Write-TuiBannerLMStudio -InnerWidth $inner }
    default { Write-TuiBannerClaude -InnerWidth $inner }
  }
  Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
  Write-TuiRow -Text ("  " + $Message) -InnerWidth $inner -Fg Yellow
  Write-TuiRow -Text ("".PadRight($inner)) -InnerWidth $inner
  Write-Host ($b.BL + (Repeat-TuiChar $b.H ($frameW - 2)) + $b.BR) -ForegroundColor Cyan
}
```

### 12.3. `scripts/run-claude-local-menu.ps1`

```powershell
[CmdletBinding()]
param(
  [ValidateSet("llamacpp","lmstudio")]
  [string]$Runtime = "llamacpp",
  [ValidateSet("interactive","quick","last")]
  [string]$StartMode = "interactive",
  [int]$Port = 1234,
  [int]$DryRun = 0
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. (Join-Path $PSScriptRoot "ensure-streaming-friendly-terminal.ps1")
. (Join-Path $PSScriptRoot "launcher-tui.ps1")

function Get-TuiBrand {
  param([Parameter(Mandatory = $true)][string]$Rt)
  if ($Rt -eq "llamacpp") { return "LlamaCpp" }
  return "LMStudio"
}

function Get-TuiSubtitle {
  param([Parameter(Mandatory = $true)][string]$Rt)
  if ($Rt -eq "llamacpp") { return "Claude Code · llama.cpp (локально)" }
  return "Claude Code · LM Studio (локально)"
}

function Get-StatePath {
  param([Parameter(Mandatory = $true)][string]$Rt)
  $dir = Join-Path $HOME ".qwen-local-setup"
  if (-not (Test-Path -LiteralPath $dir)) {
    New-Item -ItemType Directory -Path $dir | Out-Null
  }
  return (Join-Path $dir ("claude-local-menu.{0}.last.json" -f $Rt))
}

function Get-DefaultConfig {
  [ordered]@{
    session_profile   = "moe"
    reasoning_mode    = "off"
    context_length    = 24576
    custom_model_path = ""
  }
}

function Get-ContextOptions {
  param([Parameter(Mandatory = $true)][string]$Profile)
  if ($Profile -eq "dense") { return @(16384, 12288, 8192) }
  return @(24576, 16384, 12288, 8192)
}

function Get-ContextDefaultForProfile {
  param([Parameter(Mandatory = $true)][string]$Profile)
  if ($Profile -eq "dense") { return 16384 }
  return 24576
}

function Get-ProfileHintFromGgufPath {
  param([Parameter(Mandatory = $true)][string]$Path)
  $low = $Path.ToLowerInvariant()
  if ($low -match "35b|a3b|moe") { return "moe" }
  return "dense"
}

function Load-LastConfig {
  param([Parameter(Mandatory = $true)][string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) { return $null }
  try {
    $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction Stop
    if (-not $raw) { return $null }
    $obj = $raw | ConvertFrom-Json -ErrorAction Stop
    if (-not $obj.session_profile -or -not $obj.reasoning_mode -or -not $obj.context_length) {
      return $null
    }
    $cmp = ""
    try { $cmp = [string]$obj.custom_model_path } catch { $cmp = "" }
    if (-not $cmp) { $cmp = "" }
    return [ordered]@{
      session_profile   = [string]$obj.session_profile
      reasoning_mode    = [string]$obj.reasoning_mode
      context_length    = [int]$obj.context_length
      custom_model_path = $cmp.Trim()
    }
  } catch {
    return $null
  }
}

function Save-LastConfig {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)]$Config
  )
  $json = ($Config | ConvertTo-Json -Depth 4)
  $enc = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $json, $enc)
}

function Format-ConfigLabel {
  param([Parameter(Mandatory = $true)]$Cfg)
  $custom = ""
  try { $custom = [string]$Cfg.custom_model_path } catch { $custom = "" }
  if ($custom -and $custom.Trim()) {
    $leaf = [System.IO.Path]::GetFileName($custom.Trim())
    $m = "свой .gguf: $leaf"
  } else {
    $m = if ($Cfg.session_profile -eq "moe") { "35B-A3B (MoE)" } else { "27B (Dense)" }
  }
  $r = if ($Cfg.reasoning_mode -eq "on") { "с reasoning" } else { "без reasoning" }
  return ("{0}, {1}, ctx {2}" -f $m, $r, $Cfg.context_length)
}

function Read-ValidatedGgufPath {
  param(
    [Parameter(Mandatory = $true)][string]$AppBrand
  )
  while ($true) {
    Show-TuiWaitFrame -AppBrand $AppBrand -Message "Введите полный путь к .gguf и нажмите Enter (Esc в меню недоступен — просто введите путь)."
    [Console]::CursorVisible = $true
    try {
      $line = Read-Host "Путь"
    } finally {
      [Console]::CursorVisible = $false
    }
    $p = if ($line) { $line.Trim() } else { "" }
    if (-not $p) {
      Write-Host "Пустой путь — повторите." -ForegroundColor Yellow
      Start-Sleep -Seconds 1
      continue
    }
    if (-not (Test-Path -LiteralPath $p)) {
      Write-Host "Файл не найден. Проверьте путь." -ForegroundColor Yellow
      Start-Sleep -Seconds 2
      continue
    }
    if (-not $p.ToLowerInvariant().EndsWith(".gguf")) {
      Write-Host "Ожидается файл .gguf." -ForegroundColor Yellow
      Start-Sleep -Seconds 2
      continue
    }
    return (Resolve-Path -LiteralPath $p).Path
  }
}

function Start-LocalSession {
  param(
    [Parameter(Mandatory = $true)][string]$Rt,
    [Parameter(Mandatory = $true)]$Cfg,
    [Parameter(Mandatory = $true)][int]$LmsPort,
    [Parameter(Mandatory = $true)][int]$Dry
  )
  $sessionScript = Join-Path $PSScriptRoot "run-claude-local-session.ps1"
  if (-not (Test-Path -LiteralPath $sessionScript)) {
    throw "Не найден run-claude-local-session.ps1: $sessionScript"
  }

  $custom = ""
  try { $custom = [string]$Cfg.custom_model_path } catch { $custom = "" }
  $customArg = @{}
  if ($custom -and $custom.Trim()) {
    $customArg["CustomModelPath"] = $custom.Trim()
  }

  if ($Rt -eq "llamacpp") {
    & $sessionScript `
      -SessionProfile $Cfg.session_profile `
      -Runtime $Rt `
      -ContextLength ([int]$Cfg.context_length) `
      -ReasoningMode $Cfg.reasoning_mode `
      -StartClaudeMem 0 `
      -OpenClaudeMemObserver 0 `
      -StartObsidian 0 `
      -ClaudeTools "minimal" `
      -DryRun $Dry `
      -ShowLlamaConsole 1 `
      @customArg
    return
  }

  & $sessionScript `
    -SessionProfile $Cfg.session_profile `
    -Runtime $Rt `
    -ContextLength ([int]$Cfg.context_length) `
    -ReasoningMode $Cfg.reasoning_mode `
    -StartClaudeMem 0 `
    -OpenClaudeMemObserver 0 `
    -StartObsidian 0 `
    -ClaudeTools "minimal" `
    -DryRun $Dry `
    -Port $LmsPort `
    -StartLMStudioGui 1 `
    -ShowLlamaConsole 0 `
    -QuietLmStudioUi 1 `
    @customArg
}

$tuiBrand = Get-TuiBrand -Rt $Runtime
$tuiSubtitle = Get-TuiSubtitle -Rt $Runtime
$statePath = Get-StatePath -Rt $Runtime
$last = Load-LastConfig -Path $statePath
$defaults = Get-DefaultConfig
$selected = $null

if ($StartMode -eq "last" -and $last) {
  $selected = $last
} elseif ($StartMode -eq "quick") {
  $selected = $defaults
}

if (-not $selected) {
  $startItems = [System.Collections.Generic.List[object]]::new()
  if ($last) {
    [void]$startItems.Add([pscustomobject]@{
      Label = ("Запустить с последними настройками ({0})" -f (Format-ConfigLabel -Cfg $last))
      id    = "last"
    })
  }
  [void]$startItems.Add([pscustomobject]@{
    Label = ("Быстрый старт (по умолчанию: {0})" -f (Format-ConfigLabel -Cfg $defaults))
    id    = "quick"
  })
  [void]$startItems.Add([pscustomobject]@{
    Label = "Ручной выбор (модель → режим → контекст)"
    id    = "manual"
  })

  $startChoice = Show-TuiFramedMenu -AppBrand $tuiBrand -Title "Claude Code — локальный запуск" -Subtitle $tuiSubtitle -Items ($startItems.ToArray())

  if (-not $startChoice) {
    Write-Host "Выход." -ForegroundColor DarkGray
    exit 0
  }

  if ($startChoice.id -eq "last" -and $last) {
    $selected = $last
  } elseif ($startChoice.id -eq "quick") {
    $selected = $defaults
  } else {
    $modelItems = @(
      [pscustomobject]@{ Label = "35B-A3B (MoE) — пресет"; id = "moe" }
      [pscustomobject]@{ Label = "27B (Dense) — пресет"; id = "dense" }
      [pscustomobject]@{ Label = "Свой путь к .gguf…"; id = "custom" }
    )
    $m = Show-TuiFramedMenu -AppBrand $tuiBrand -Title "1) Модель" -Subtitle "Пресет Qwen или произвольный .gguf" -Items $modelItems
    if (-not $m) {
      Write-Host "Отмена." -ForegroundColor DarkGray
      exit 0
    }

    $profile = [string]$m.id
    $customPath = ""
    if ($m.id -eq "custom") {
      $customPath = Read-ValidatedGgufPath -AppBrand $tuiBrand
      $hint = Get-ProfileHintFromGgufPath -Path $customPath
      $tplItems = @(
        [pscustomobject]@{ Label = "Тюнинг как у Dense 27B (batch/контексты)"; id = "dense" }
        [pscustomobject]@{ Label = "Тюнинг как у MoE 35B (batch/контексты)"; id = "moe" }
      )
      $initialTpl = if ($hint -eq "moe") { 1 } else { 0 }
      $tpl = Show-TuiFramedMenu -AppBrand $tuiBrand -Title "Профиль llama.cpp / списки ctx" -Subtitle ("Авто-подсказка по имени файла: {0}" -f $hint) -Items $tplItems -InitialIndex $initialTpl
      if (-not $tpl) {
        Write-Host "Отмена." -ForegroundColor DarkGray
        exit 0
      }
      $profile = [string]$tpl.id
    }

    $reasoningItems = @(
      [pscustomobject]@{ Label = "Обычная (без reasoning) — по умолчанию"; id = "off" }
      [pscustomobject]@{ Label = "С reasoning"; id = "on" }
    )
    $r = Show-TuiFramedMenu -AppBrand $tuiBrand -Title "2) Режим ответа" -Subtitle "llama.cpp: флаг --reasoning" -Items $reasoningItems
    if (-not $r) {
      Write-Host "Отмена." -ForegroundColor DarkGray
      exit 0
    }
    $reasoningMode = [string]$r.id

    $ctxValues = Get-ContextOptions -Profile $profile
    $ctxDefault = Get-ContextDefaultForProfile -Profile $profile
    $ctxItems = [System.Collections.Generic.List[object]]::new()
    foreach ($ctx in $ctxValues) {
      $suffix = if ($ctx -eq $ctxDefault) { " (default)" } else { "" }
      [void]$ctxItems.Add([pscustomobject]@{
        Label = ("{0} tokens{1}" -f $ctx, $suffix)
        id    = [string]$ctx
      })
    }
    $defaultCtxIndex = [Array]::IndexOf($ctxValues, $ctxDefault)
    if ($defaultCtxIndex -lt 0) { $defaultCtxIndex = 0 }
    $c = Show-TuiFramedMenu -AppBrand $tuiBrand -Title "3) Контекстное окно" -Subtitle "n_ctx для локального сервера" -Items ($ctxItems.ToArray()) -InitialIndex $defaultCtxIndex
    if (-not $c) {
      Write-Host "Отмена." -ForegroundColor DarkGray
      exit 0
    }

    $selected = [ordered]@{
      session_profile   = $profile
      reasoning_mode    = $reasoningMode
      context_length    = [int]$c.id
      custom_model_path = $customPath
    }
  }
}

Save-LastConfig -Path $statePath -Config $selected
try {
  Start-LocalSession -Rt $Runtime -Cfg $selected -LmsPort $Port -Dry $DryRun
} catch {
  Write-Host ""
  Write-Host ("Ошибка: {0}" -f $_.Exception.Message) -ForegroundColor Red
  Write-Host "Полный текст можно скопировать выше. Нажми Enter, чтобы закрыть окно." -ForegroundColor Yellow
  try {
    Read-Host | Out-Null
  } catch {
    Start-Sleep -Seconds 30
  }
  exit 1
}
```

### 12.4. `scripts/invoke-claude-in-console.ps1`

```powershell
# Запуск Claude Code в отдельном окне: наследует ANTHROPIC_* и прочий env от родительского процесса.
param(
  [Parameter(Mandatory = $true)][string]$Model,
  [string]$Tools = ""
)

$ErrorActionPreference = "Stop"
if ($Tools -and $Tools.Trim().Length -gt 0) {
  & claude --model $Model --tools $Tools
} else {
  & claude --model $Model
}
exit $LASTEXITCODE
```

### 12.5. `scripts/share-ngrok-local.ps1`

```powershell
<#
One-click "share" shortcut:
- Ensure LM Studio server is up
- Unload + load requested model profile (dense/moe)
- Start ngrok tunnel to local port
#>

[CmdletBinding()]
param(
  [ValidateSet("dense","moe")]
  [string]$Profile,
  [string]$LMStudioRoot = "I:\LMStudio",
  [int]$Port = 1234,
  [int]$ContextLength = 65536
)

$ErrorActionPreference = "Stop"

function Resolve-LmsExe([string]$Root) {
  $p = Join-Path $Root "LM Studio\resources\app\.webpack\lms.exe"
  if (Test-Path -LiteralPath $p) { return $p }
  $found = Get-ChildItem -Path $Root -Recurse -Filter "lms.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { return $found.FullName }
  return ""
}

function Ensure-Server([string]$LmsExe,[int]$Port,[string]$Root) {
  try { & $LmsExe server start --port $Port *> $null; return } catch {}
  $gui = Join-Path $Root "LM Studio\LM Studio.exe"
  if (Test-Path -LiteralPath $gui) {
    Start-Process -FilePath $gui | Out-Null
    Start-Sleep -Seconds 2
  }
  & $LmsExe server start --port $Port *> $null
}

$lmsExe = Resolve-LmsExe $LMStudioRoot
if (-not $lmsExe) { throw "lms.exe not found under $LMStudioRoot" }

Ensure-Server -LmsExe $lmsExe -Port $Port -Root $LMStudioRoot

$id = if ($Profile -eq "dense") { "qwen3.6-27b-uncensored-hauhaucs-aggressive" } else { "qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive" }
try { & $lmsExe unload --all *> $null } catch {}
try { & $lmsExe load $id --context-length $ContextLength *> $null } catch {}

if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
  throw "ngrok not found on PATH."
}

Write-Host "Starting ngrok tunnel for localhost:$Port (model=$id)" -ForegroundColor Green
& ngrok http $Port
```

### 12.6. ``scripts/stop-local-qwen-now.ps1``

```powershell
[CmdletBinding()]
param(
  [string]$LMStudioRoot = "I:\LMStudio",
  [switch]$KillLMStudioProcess
)

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"
$PSNativeCommandUseErrorActionPreference = $false

function Resolve-LmsExe([string]$Root) {
  $cmd = Get-Command lms -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $p = Join-Path $Root "LM Studio\resources\app\.webpack\lms.exe"
  if (Test-Path -LiteralPath $p) { return $p }
  $found = Get-ChildItem -Path $Root -Recurse -Filter "lms.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { return $found.FullName }
  return ""
}

Write-Host "Stopping local Qwen endpoint..." -ForegroundColor Yellow
$lmsExe = Resolve-LmsExe $LMStudioRoot
if ($lmsExe) {
  & $lmsExe unload --all *> $null
  & $lmsExe server stop *> $null
}

if ($KillLMStudioProcess) {
  Get-Process -Name "LM Studio" -ErrorAction SilentlyContinue | Stop-Process -Force
}

Write-Host "Done: endpoint stopped, model unloaded from VRAM." -ForegroundColor Green
```

### 12.7. ``scripts/unload-llamacpp-and-proxies.ps1``

```powershell
[CmdletBinding()]
param()

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

function Stop-ListeningPort([int]$Port) {
  try {
    $conns = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
      if ($c.OwningProcess -and $c.OwningProcess -gt 0) {
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
      }
    }
  } catch {}
}

# llama.cpp servers we start
Stop-ListeningPort -Port 1240
Stop-ListeningPort -Port 1241

# local free-claude-code proxies we start
Stop-ListeningPort -Port 8084
Stop-ListeningPort -Port 8085

# Fallback: kill leftover llama-server.exe processes (only our binary path)
try {
  $exe = "I:\qwen-local-setup\bin\llama.cpp\llama-server.exe"
  Get-Process -Name "llama-server" -ErrorAction SilentlyContinue | ForEach-Object {
    try {
      if ($_.Path -and ($_.Path -ieq $exe)) {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
      }
    } catch {}
  }
} catch {}

Write-Host "OK: выгрузил llama.cpp + локальные прокси (VRAM освобождена)" -ForegroundColor Green
```

> На новой машине замените строку `$exe = "I:\qwen-local-setup\..."`.

### 12.8. ``scripts/install-llamacpp-win-cuda.ps1`` (полный файл из репозитория)

```powershell
[CmdletBinding()]
param(
  [string]$InstallDir = "I:\qwen-local-setup\bin\llama.cpp",
  [string]$Repo = "ggml-org/llama.cpp"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Get-LatestReleaseAssetUrl {
  param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$NameRegex
  )

  $rel = Invoke-RestMethod -Uri ("https://api.github.com/repos/{0}/releases/latest" -f $Repo) -Headers @{
    "User-Agent" = "qwen-local-setup"
  }

  $asset = @($rel.assets) | Where-Object { $_.name -match $NameRegex } | Select-Object -First 1
  if (-not $asset) {
    $names = @($rel.assets) | ForEach-Object { $_.name }
    throw ("Could not find release asset matching regex: {0}`nAvailable assets:`n- {1}" -f $NameRegex, ($names -join "`n- "))
  }

  return $asset.browser_download_url
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

function Ensure-CudaRuntimeDlls {
  param([Parameter(Mandatory = $true)][string]$InstallDir,[Parameter(Mandatory = $true)][string]$Repo)

  $hasCudart = @(Get-ChildItem -LiteralPath $InstallDir -File -Filter "cudart64_*.dll" -ErrorAction SilentlyContinue).Count -gt 0
  $hasCublas = @(Get-ChildItem -LiteralPath $InstallDir -File -Filter "cublas64_*.dll" -ErrorAction SilentlyContinue).Count -gt 0
  if ($hasCudart -and $hasCublas) {
    Write-Host "CUDA runtime DLLs already present in $InstallDir" -ForegroundColor Green
    return
  }

  Write-Host "CUDA runtime DLLs missing; downloading cudart package..." -ForegroundColor Yellow
  $cudartUrl = $null
  try { $cudartUrl = Get-LatestReleaseAssetUrl -Repo $Repo -NameRegex "(?i)^cudart-llama-bin-win-cuda-12\.4-x64\.zip$" } catch {}
  if (-not $cudartUrl) {
    $cudartUrl = Get-LatestReleaseAssetUrl -Repo $Repo -NameRegex "(?i)^cudart-llama-bin-win-cuda-13\.1-x64\.zip$"
  }

  $tmp = Join-Path $env:TEMP ("llama.cpp-cudart-{0}.zip" -f ([guid]::NewGuid().ToString("n")))
  Write-Host "Downloading: $cudartUrl" -ForegroundColor Cyan
  Invoke-WebRequest -Uri $cudartUrl -OutFile $tmp -UseBasicParsing
  Write-Host "Extracting cudart into: $InstallDir" -ForegroundColor Cyan
  Expand-Archive -LiteralPath $tmp -DestinationPath $InstallDir -Force
  Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}

# Pick Windows CUDA x64 build (prefer CUDA 12.4 unless only 13.1 exists).
$url = $null
try { $url = Get-LatestReleaseAssetUrl -Repo $Repo -NameRegex "(?i)^llama-.*-bin-win-cuda-12\.4-x64\.zip$" } catch {}
if (-not $url) {
  try { $url = Get-LatestReleaseAssetUrl -Repo $Repo -NameRegex "(?i)^llama-.*-bin-win-cuda-13\.1-x64\.zip$" } catch {}
}
if (-not $url) {
  # Fallback: accept any llama *bin-win-cuda* x64 zip.
  $url = Get-LatestReleaseAssetUrl -Repo $Repo -NameRegex "(?i)^llama-.*-bin-win-cuda-.*-x64\.zip$"
}

$direct = Join-Path $InstallDir "llama-server.exe"
if (Test-Path -LiteralPath $direct) {
  Write-Host "llama-server.exe already present in $InstallDir" -ForegroundColor Green
  Ensure-CudaRuntimeDlls -InstallDir $InstallDir -Repo $Repo
  return
}

$tmp = Join-Path $env:TEMP ("llama.cpp-win-cuda-{0}.zip" -f ([guid]::NewGuid().ToString("n")))

Write-Host "Downloading: $url" -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing

Write-Host "Extracting into: $InstallDir" -ForegroundColor Cyan
Expand-Archive -LiteralPath $tmp -DestinationPath $InstallDir -Force
Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue

# Some release zips contain a nested folder; flatten if needed.
if (-not (Test-Path -LiteralPath $direct)) {
  $nested = Get-ChildItem -LiteralPath $InstallDir -Recurse -File -Filter "llama-server.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($nested) {
    Copy-Item -LiteralPath $nested.FullName -Destination $direct -Force
  }
}

if (-not (Test-Path -LiteralPath $direct)) {
  throw "Install finished but llama-server.exe was not found in $InstallDir"
}

Ensure-CudaRuntimeDlls -InstallDir $InstallDir -Repo $Repo

Write-Host "Installed: $direct" -ForegroundColor Green
```

### 12.9. ``scripts/start-claude-mem.ps1`` (с self-repair)

```powershell
[CmdletBinding()]
param(
  [int]$OpenBrowser = 0,
  [switch]$SkipStatus,
  # Обновление плагина до последней версии (npx claude-mem update), затем stop/clean/start.
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

# Сброс «зависшего» worker.pid: внутренний worker-service сразу exit(0), если считает дубликат — тогда HTTP не поднимается.
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

---

## 13. Главный файл: `scripts/run-claude-local-session.ps1`

> **Полный текст:** ниже — дословная копия `scripts/run-claude-local-session.ps1` из репозитория на момент запуска этого скрипта. Теория и таблица патчей прокси — **§7.5**.

```powershell
[CmdletBinding()]
param(
  [Alias("Profile")]
  [ValidateSet("dense","moe")]
  [string]$SessionProfile,
  [ValidateSet("lmstudio","llamacpp")]
  [string]$Runtime = "llamacpp",
  [string]$LMStudioRoot = "I:\LMStudio",
  # Optional full path to LM Studio.exe if autodetection fails.
  [string]$LMStudioGuiExe = "",
  # For Runtime=lmstudio: 1 = launch LM Studio GUI before server/model load (recommended for desktop shortcuts).
  [int]$StartLMStudioGui = 0,
  [int]$Port = 1234,
  # 0 = auto by profile (dense=8192, moe=16384) for near-90% VRAM target.
  [int]$ContextLength = 0,
  # LM Studio: доля слоёв на GPU (1.0 = все слои на GPU). Запас под Windows — за счёт модели ~19–21 ГБ на 24 ГБ, не занижением offload.
  [double]$GpuOffload = 1.0,
  # 1 = для Runtime=lmstudio не писать диагностику в консоль (в файл %USERPROFILE%\.qwen-local-setup\lmstudio-session-launcher.log), меньше мусора в TUI Claude Code.
  [int]$QuietLmStudioUi = 0,
  # Use int instead of bool because some launchers pass everything as strings.
  # 0 = don't start, 1 = start
  [int]$StartClaudeMem = 0,
  [int]$StartObsidian = 0,
  [string]$ObsidianPath = "",
  [string]$ObsidianVaultPath = "",
  # 0 = don't open, 1 = open (default).
  # 0 = don't open browser tab, 1 = open viewer
  [int]$OpenClaudeMemObserver = 0,
  # 1 = run checks + smoke request and exit (no interactive Claude Code TUI)
  [int]$DryRun = 0,
  # 0 = don't show, 1 = show llama.cpp console window (separate window)
  [int]$ShowLlamaConsole = 0,
  # Tool calling is the main value of Claude Code, but sending *all* tool schemas
  # to a small local context (e.g. 8k) can exceed n_ctx. Use a curated default.
  # Set to "default" to let Claude Code decide; set to "" to disable tools.
  [string]$ClaudeTools = "minimal",
  # llama.cpp server-side reasoning mode: off = direct answer, on = thinking traces enabled.
  [ValidateSet("off","on")]
  [string]$ReasoningMode = "off",
  # Полный путь к .gguf (любая локальная модель). Пусто = пресеты dense/moe из SessionProfile.
  [string]$CustomModelPath = ""
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

. (Join-Path $PSScriptRoot "ensure-streaming-friendly-terminal.ps1")

$script:SessionQuietUi = $false

function Write-SessionDiag {
  param(
    [Parameter(Mandatory = $true)][string]$Message,
    [System.ConsoleColor]$ForegroundColor = [System.ConsoleColor]::Gray
  )
  if ($script:SessionQuietUi) {
    $logDir = Join-Path $HOME ".qwen-local-setup"
    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $line = ("{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message)
    Add-Content -LiteralPath (Join-Path $logDir "lmstudio-session-launcher.log") -Value $line -Encoding UTF8
    # Та же консоль, что и интерактивное меню — отдельное окно «только логи» не открываем.
    Write-Host $line -ForegroundColor $ForegroundColor
    return
  }
  Write-Host $Message -ForegroundColor $ForegroundColor
}

function Get-LmsExeUsable {
  param([Parameter(Mandatory=$true)][string]$LmsExe)
  # LM Studio auto-updates can temporarily lock lms.exe (Windows error: "file is being used").
  # When that happens, copy to a stable temp path and execute the copy.
  if (-not (Test-Path -LiteralPath $LmsExe)) { return $LmsExe }
  try {
    $fs = [System.IO.File]::Open($LmsExe, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
    $fs.Close()
    return $LmsExe
  } catch {
    $logDir = Join-Path $HOME ".qwen-local-setup"
    if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $tmp = Join-Path $logDir "lms-temp.exe"
    try { Copy-Item -LiteralPath $LmsExe -Destination $tmp -Force } catch { return $LmsExe }
    return $tmp
  }
}

function Invoke-LmsSafe {
  param(
    [Parameter(Mandatory=$true)][string]$LmsExe,
    [Parameter(Mandatory=$true)][string[]]$Args,
    [switch]$IgnoreFailure
  )
  $logDir = Join-Path $HOME ".qwen-local-setup\lms"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
  $outLog = Join-Path $logDir "lms-cmd-last.out.log"
  $errLog = Join-Path $logDir "lms-cmd-last.err.log"
  try {
    $exe = Get-LmsExeUsable -LmsExe $LmsExe
    Remove-Item -LiteralPath $outLog -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $errLog -ErrorAction SilentlyContinue
    $p = Start-Process -FilePath $exe -ArgumentList $Args -Wait -PassThru -WindowStyle Hidden `
      -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    $code = 0
    if ($null -ne $p -and $null -ne $p.ExitCode) { $code = [int]$p.ExitCode }
  } catch {
    $code = 1
  }
  if (-not $IgnoreFailure -and $code -ne 0) {
    throw "lms command failed: $($Args -join ' ') (exit=$code, see $outLog / $errLog)"
  }
  return $code
}

function Resolve-LmsExe([string]$Root) {
  $cmd = Get-Command lms -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $p = Join-Path $Root "LM Studio\resources\app\.webpack\lms.exe"
  if (Test-Path -LiteralPath $p) { return $p }
  $found = Get-ChildItem -Path $Root -Recurse -Filter "lms.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { return $found.FullName }
  throw "lms.exe not found under $Root"
}

function Resolve-LMStudioGuiExe {
  param(
    [string]$ExplicitPath,
    [string]$LmsExePath,
    [string]$SearchRoot
  )
  if ($ExplicitPath -and (Test-Path -LiteralPath $ExplicitPath)) {
    return (Resolve-Path -LiteralPath $ExplicitPath).Path
  }
  if ($LmsExePath -and (Test-Path -LiteralPath $LmsExePath)) {
    # Typical layout: ...\LM Studio\resources\app\.webpack\lms.exe  ->  ...\LM Studio\LM Studio.exe
    $d = Split-Path -Parent $LmsExePath
    for ($i = 0; $i -lt 4; $i++) { $d = Split-Path -Parent $d }
    $candidate = Join-Path $d "LM Studio.exe"
    if (Test-Path -LiteralPath $candidate) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }
  if ($SearchRoot -and (Test-Path -LiteralPath $SearchRoot)) {
    $found = Get-ChildItem -LiteralPath $SearchRoot -Recurse -Filter "LM Studio.exe" -ErrorAction SilentlyContinue |
      Select-Object -First 1
    if ($found) { return $found.FullName }
  }
  $localDefault = Join-Path $env:LOCALAPPDATA "Programs\LM Studio\LM Studio.exe"
  if (Test-Path -LiteralPath $localDefault) { return (Resolve-Path -LiteralPath $localDefault).Path }
  return ""
}

function Test-LMStudioProcessRunning {
  foreach ($n in @("LM Studio", "lm-studio")) {
    try {
      if (Get-Process -Name $n -ErrorAction SilentlyContinue) { return $true }
    } catch {}
  }
  try {
    $any = Get-Process -ErrorAction SilentlyContinue | Where-Object {
      $_.Path -and ($_.Path -like "*\\LM Studio\\LM Studio.exe" -or $_.Path -like "*LM Studio.exe")
    } | Select-Object -First 1
    return [bool]$any
  } catch {}
  return $false
}

function Ensure-LMStudioGui {
  param(
    [string]$GuiExe,
    [int]$WarmupSeconds = 10
  )
  if (-not $GuiExe -or -not (Test-Path -LiteralPath $GuiExe)) {
    throw "LM Studio.exe path is missing or invalid: '$GuiExe'. Укажи полный путь через -LMStudioGuiExe."
  }
  if (-not (Test-LMStudioProcessRunning)) {
    Write-SessionDiag "LM Studio: запускаю GUI отдельно от этой консоли (start /D …) — иначе Electron пишет логи в окно PowerShell/Claude Code." Cyan
    $workDir = Split-Path -LiteralPath $GuiExe
    # start "" /D "dir" "exe" — разрыв цепочки консоли; прямой Start-Process на LM Studio.exe часто оставляет AttachConsole → сотни строк [LMSInternal] в том же TTY, что и claude.
    Start-Process -FilePath "cmd.exe" -ArgumentList @(
      "/c",
      "start",
      "`"`"",
      "/D",
      "`"$workDir`"",
      "`"$GuiExe`""
    ) -WindowStyle Hidden | Out-Null
  } else {
    Write-SessionDiag "LM Studio: GUI уже запущен." DarkGray
  }
  Write-SessionDiag "LM Studio: жду инициализацию (${WarmupSeconds}s)..." DarkGray
  Start-Sleep -Seconds $WarmupSeconds
}

function Test-OpenAIReady([int]$Port) {
  $url = "http://localhost:$Port/v1/models"
  try {
    $r = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 15
    return [bool]$r
  } catch {
    return $false
  }
}

function Test-HttpOk([string]$Url,[int]$TimeoutSec = 5) {
  try {
    # Avoid the "Script Execution Risk" prompt in Windows PowerShell (5.1)
    $iwr = Get-Command Invoke-WebRequest -ErrorAction Stop
    if ($iwr.Parameters.ContainsKey("UseBasicParsing")) {
      $r = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec -UseBasicParsing
    } else {
      $r = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec
    }
    return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
  } catch {
    return $false
  }
}

function Test-HttpResponding([string]$Url,[int]$TimeoutSec = 3) {
  # "Responding" means the server returned any HTTP response (including 401/403/404).
  try {
    $iwr = Get-Command Invoke-WebRequest -ErrorAction Stop
    if ($iwr.Parameters.ContainsKey("UseBasicParsing")) {
      $null = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec -UseBasicParsing
    } else {
      $null = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec
    }
    return $true
  } catch {
    try {
      if ($_.Exception.Response -and $_.Exception.Response.StatusCode) { return $true }
    } catch {}
    return $false
  }
}

function Ensure-Server([string]$LmsExe,[string]$Root,[int]$Port) {
  if (Test-OpenAIReady -Port $Port) { return }

  Invoke-LmsSafe -LmsExe $LmsExe -Args @("server","start","--port",$Port) -IgnoreFailure | Out-Null
  for ($i = 0; $i -lt 12; $i++) {
    if (Test-OpenAIReady -Port $Port) { return }
    Start-Sleep -Seconds 2
  }

  # Second attempt: some LM Studio builds need a repeated start after daemon wakeup.
  Invoke-LmsSafe -LmsExe $LmsExe -Args @("server","start","--port",$Port) -IgnoreFailure | Out-Null
  for ($i = 0; $i -lt 12; $i++) {
    if (Test-OpenAIReady -Port $Port) { return }
    Start-Sleep -Seconds 2
  }
  throw "LM Studio endpoint did not become ready on http://localhost:$Port/v1/models"
}

function Try-LoadOnce([string]$LmsExe,[string]$ModelId,[int]$Context,[int]$TimeoutSec,[double]$GpuOffload) {
  $gpuArg = $GpuOffload.ToString("0.00",[System.Globalization.CultureInfo]::InvariantCulture)
  # Keep preload memory profile aligned with force-load path.
  # Without --parallel 1 LM Studio may pick higher parallelism and consume extra VRAM/RAM.
  $lmsArgs = @("load",$ModelId,"--context-length",$Context,"--gpu",$gpuArg,"--parallel","1","--yes")
  $logDir = Join-Path $HOME ".qwen-local-setup\lms"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss-ffff"
  $outLog = Join-Path $logDir ("preload-{0}.out.log" -f $stamp)
  $errLog = Join-Path $logDir ("preload-{0}.err.log" -f $stamp)
  $exe = Get-LmsExeUsable -LmsExe $LmsExe
  $p = Start-Process -FilePath $exe -ArgumentList $lmsArgs -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog
  $done = Wait-Process -Id $p.Id -Timeout $TimeoutSec -ErrorAction SilentlyContinue
  if (-not $done) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    return $false
  }
  $p.Refresh()
  return ($p.ExitCode -eq 0)
}

function Load-ModelBestEffort([string]$LmsExe,[int]$PreferredContext,[double]$GpuOffload) {
  $candidates = @()
  if ($CustomModelPath -and $CustomModelPath.Trim() -and (Test-Path -LiteralPath $CustomModelPath.Trim())) {
    $candidates += (Resolve-Path -LiteralPath $CustomModelPath.Trim()).Path
  }
  if ($candidates.Count -eq 0) {
    $candidates = if ($SessionProfile -eq "dense") {
      @(
        "hauhaucs/qwen3.6-27b-uncensored-hauhaucs-aggressive/qwen3.6-27b-uncensored-hauhaucs-aggressive-q5_k_p.gguf",
        "qwen3.6-27b-uncensored-hauhaucs-aggressive"
      )
    } else {
      @(
        "hauhaucs/qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive/qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive-q4_k_p.gguf",
        "qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive@q4_k_m",
        "qwen3.6-35b-a3b-uncensored-hauhaucs-aggressive"
      )
    }
  }

  foreach ($candidate in $candidates) {
    Write-SessionDiag "Trying to preload $candidate with ctx=$PreferredContext ..." DarkCyan
    # Some large models can take >25s to load on first run; allow more time.
    if (Try-LoadOnce -LmsExe $LmsExe -ModelId $candidate -Context $PreferredContext -TimeoutSec 180 -GpuOffload $GpuOffload) {
      Write-SessionDiag "Model preloaded: $candidate" Green
      return $true
    }
  }
  Write-Host "Warning: preload skipped/failed. Continuing; model will lazy-load on first request." -ForegroundColor Yellow
  return $false
}

function Ensure-ModelLoaded([string]$LmsExe,[string]$ModelId,[int]$Context,[double]$GpuOffload) {
  Write-SessionDiag "Ensuring model is loaded with ctx=$Context ..." DarkCyan
  Invoke-LmsSafe -LmsExe $LmsExe -Args @("unload","--all") -IgnoreFailure | Out-Null

  $logDir = Join-Path $HOME ".qwen-local-setup"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
  $logPath = Join-Path $logDir "lms-load.log"
  $stdoutPath = Join-Path $logDir "lms-load.stdout.log"
  $stderrPath = Join-Path $logDir "lms-load.stderr.log"
  $timeoutSec = 300

  # VRAM fallback strategy:
  # - If CUDA buffer allocation fails, retry with smaller context and/or lower GPU offload.
  $ctxCandidates = @($Context)
  if ($SessionProfile -eq "dense") {
    # Keep dense on-GPU and reduce context first if needed.
    $ctxCandidates += @(12288, 8192, 6144)
  } else {
    $ctxCandidates += @(12288, 8192)
  }
  $ctxCandidates = $ctxCandidates | Where-Object { $_ -is [int] -and $_ -gt 0 } | Select-Object -Unique

  $gpuCandidates = @($GpuOffload, 0.98, 0.95, 0.92, 0.88, 0.85) |
    Where-Object { $_ -ge 0.70 -and $_ -le 1.0 } |
    Select-Object -Unique

  $lastLog = ""
  foreach ($ctxTry in $ctxCandidates) {
    foreach ($gpuTry in $gpuCandidates) {
      $gpuArg = $gpuTry.ToString("0.00",[System.Globalization.CultureInfo]::InvariantCulture)
      Remove-Item -LiteralPath $logPath -ErrorAction SilentlyContinue
      # NOTE: --parallel reduces internal concurrency (and memory usage).
      # On some builds, default parallelism can be >1 and increases VRAM needs.
      $lmsArgs = @("load",$ModelId,"--context-length",$ctxTry,"--gpu",$gpuArg,"--parallel","1","--yes")
      $output = ""
      try {
        $exe = Get-LmsExeUsable -LmsExe $LmsExe
        Remove-Item -LiteralPath $stdoutPath -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $stderrPath -ErrorAction SilentlyContinue
        $p = Start-Process -FilePath $exe -ArgumentList $lmsArgs -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
        $done = Wait-Process -Id $p.Id -Timeout $timeoutSec -ErrorAction SilentlyContinue
        if (-not $done) {
          Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
          $code = 124
          $outText = ""
          $errText = ""
          try { $outText = (Get-Content -Raw -LiteralPath $stdoutPath -ErrorAction SilentlyContinue) } catch { $outText = "" }
          try { $errText = (Get-Content -Raw -LiteralPath $stderrPath -ErrorAction SilentlyContinue) } catch { $errText = "" }
          $output = ("timeout waiting for lms load (ctx=$ctxTry gpu=$gpuArg)`n" + $outText + "`n" + $errText).Trim()
        } else {
          $p.Refresh()
          $code = $p.ExitCode
          $outText = ""
          $errText = ""
          try { $outText = (Get-Content -Raw -LiteralPath $stdoutPath -ErrorAction SilentlyContinue) } catch { $outText = "" }
          try { $errText = (Get-Content -Raw -LiteralPath $stderrPath -ErrorAction SilentlyContinue) } catch { $errText = "" }
          $output = ($outText + "`n" + $errText).Trim()
        }
      } catch {
        $code = 1
        $output = $_.Exception.Message
      }
      $output | Set-Content -LiteralPath $logPath -Encoding UTF8
      try { $lastLog = (Get-Content -Raw -LiteralPath $logPath -ErrorAction SilentlyContinue) } catch { $lastLog = "" }

      if (($output -match "paging file is too small") -or ($lastLog -match "paging file is too small")) {
        throw ("LM Studio не смог загрузить движок (ошибка paging file). " +
               "Увеличь файл подкачки Windows (pagefile) и повтори. " +
               "Подсказка: Пуск → 'Дополнительно' → 'Настройка представления и производительности системы' → " +
               "Дополнительно → Виртуальная память → Изменить → выставить 32–64 ГБ (или 'Системный размер') на диске C:. " +
               "Детали: {0}" -f $logPath)
      }

      # LM Studio can sometimes print success but still return a non-zero code.
      # Treat explicit success text as authoritative.
      $looksSuccessful = ($output -match "Model loaded successfully") -or ($lastLog -match "Model loaded successfully")

      if ($code -eq 0 -or $looksSuccessful) {
        if ($ctxTry -ne $Context -or [Math]::Abs($gpuTry - $GpuOffload) -gt 0.0001) {
          Write-SessionDiag "Loaded with fallback: ctx=$ctxTry gpu=$gpuArg" Yellow
        }
        return
      }

      # If it looks like a config/CLI error, fail fast.
      $isHardFailure =
        ($output -match "Unknown option") -or
        ($output -match "Usage:\\s+lms\\s+load") -or
        ($output -match "not recognized") -or
        ($output -match "ENOENT") -or
        ($lastLog -match "ENOENT")

      if ($isHardFailure) {
        throw "Model failed to load (config/CLI error). See $logPath."
      }

      # Otherwise continue trying fallbacks (treat as VRAM/transient by default).
    }
  }

  throw "Model failed to load after fallbacks. Tried contexts: $($ctxCandidates -join ', ') and GPU offload: $($gpuCandidates -join ', '). See $logPath."
}

function Test-OpenAIModelsEndpoint([string]$BaseUrl,[int]$TimeoutSec = 10) {
  try {
    $r = Invoke-RestMethod -Uri ($BaseUrl.TrimEnd("/") + "/models") -Method Get -TimeoutSec $TimeoutSec
    return [bool]$r
  } catch {
    return $false
  }
}

function Ensure-LlamaCppServer {
  param(
    [Parameter(Mandatory = $true)][string]$ModelPath,
    [Parameter(Mandatory = $true)][int]$Port,
    [Parameter(Mandatory = $true)][int]$ContextLength,
    [Parameter(Mandatory = $true)][string]$Profile,
    [int]$ShowConsole = 0
  )

  $exe = "I:\qwen-local-setup\bin\llama.cpp\llama-server.exe"
  if (-not (Test-Path -LiteralPath $exe)) { throw "llama-server.exe not found at $exe" }
  if (-not (Test-Path -LiteralPath $ModelPath)) { throw "Model file not found: $ModelPath" }

  $openAIBase = "http://127.0.0.1:$Port/v1"

  # Always restart on the target port so ctx/flags are applied deterministically.
  try {
    Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
      ForEach-Object {
        if ($_.OwningProcess) { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
      }
  } catch {}

  $threads = 16
  $threadsBatch = 24
  $logPath = Join-Path $env:TEMP ("llama-server-{0}.log" -f $Port)
  try { Remove-Item -LiteralPath $logPath -Force -ErrorAction SilentlyContinue } catch {}

  # Deep-research tuning:
  # - Keep Windows responsive by reserving VRAM margin with --fit-target (MiB).
  # - Disable "thinking" by default via --reasoning off for better UX.
  # - Expose metrics/perf for real tok/s debugging.
  # Dense profile needs extra desktop headroom on Windows to avoid UI stalls.
  $fitTargetMiB = if ($Profile -eq "dense") { 3072 } else { 2560 }

  $llamaArgs = @(
    "--model", $ModelPath,
    "--jinja",
    "--host", "127.0.0.1",
    "--port", $Port,
    "--ctx-size", $ContextLength,
    "--device", "CUDA0",
    "--log-file", $logPath,
    "--log-prefix",
    "--log-timestamps",
    "--metrics",
    "--perf",
    "--fit", "on",
    "--fit-target", $fitTargetMiB,
    "--threads", $threads,
    "--threads-batch", $threadsBatch,
    "--parallel", "1",
    "--no-cont-batching",
    "--n-gpu-layers", "all",
    "--batch-size", $(if ($Profile -eq "moe") { "2048" } else { "512" }),
    "--ubatch-size", $(if ($Profile -eq "moe") { "512" } else { "128" }),
    "--flash-attn", "on",
    "--cache-type-k", "q4_0",
    "--cache-type-v", "q4_0",
    # NOTE: do NOT force "--chat-template qwen" here.
    # With current llama.cpp build b8994 + Qwen3.6 GGUF this can degrade chat/completions
    # prompts to ~2 tokens (effectively empty user input), producing irrelevant boilerplate.
    # Let llama.cpp use the template embedded in GGUF metadata.
    # Reasoning mode is selected by the launcher menu (default off).
    "--reasoning", $ReasoningMode,
    "--no-warmup",
    # Claude Code шлёт разные системные/тул промпты; кэш промпта + similarity (LCP) на слотах
    # может подмешивать «хвосты» от прошлых запросов → ответ не на тот вопрос (англ. мусор и т.д.).
    "--no-cache-prompt",
    "--cache-ram", "0"
  )
  if ($Profile -eq "moe") {
    # Light MoE expert spill to CPU to keep VRAM margin stable on Windows.
    # (Adjustable later if you want stricter VRAM-only.)
    $llamaArgs += @("--n-cpu-moe", "6")
  }

  $tailProc = $null
  # Окно tail по лог-файлу отключено: при ShowLlamaConsole=1 и так показывается консоль llama-server.exe;
  # второе окно дублировало те же строки.

  # If user requested visibility, show the llama-server console itself.
  # This is the most reliable way to see load progress/errors.
  $ws = if ($ShowConsole -ne 0) { "Normal" } else { "Hidden" }
  $p = Start-Process -FilePath $exe -ArgumentList $llamaArgs -PassThru -WindowStyle $ws
  # Model load -> VRAM can take several minutes on Windows; don't time out too early.
  for ($i = 0; $i -lt 1800; $i++) {
    if (($i % 10) -eq 0) {
      $sec = [int](($i * 500) / 1000)
      $tail = ""
      try { $tail = (Get-Content -LiteralPath $logPath -ErrorAction SilentlyContinue | Select-Object -Last 4) -join " | " } catch {}
      Write-Host "llama.cpp: жду готовность /v1/models... (${sec}s) ${tail}" -ForegroundColor DarkGray
    }

    if (Test-OpenAIModelsEndpoint -BaseUrl $openAIBase -TimeoutSec 2) {
      # Sanity: if server came up with an unexpectedly huge n_ctx (kills tok/s), fail fast.
      try {
        $ctxLine = (Get-Content -LiteralPath $logPath -ErrorAction SilentlyContinue |
          Select-String -Pattern 'llama_context:\s+n_ctx\s*=\s*(\d+)' -AllMatches | Select-Object -Last 1)
        if ($ctxLine -and $ctxLine.Matches.Count -gt 0) {
          $nctx = [int]$ctxLine.Matches[0].Groups[1].Value
          if ($nctx -gt 32768) {
            throw "FATAL_NCTX_TOO_LARGE n_ctx=$nctx (reduce context for speed)"
          }
        }
      } catch {
        if ($_.Exception.Message -match 'FATAL_NCTX_TOO_LARGE') { throw }
        Write-Host ("llama.cpp: проверка n_ctx из лога пропущена: {0}" -f $_.Exception.Message) -ForegroundColor DarkGray
      }
      return @{ Process = $p; BaseUrl = $openAIBase; Port = $Port; LogPath = $logPath; TailProc = $tailProc }
    }
    if ($p -and $p.HasExited) {
      $tail = ""
      try { $tail = (Get-Content -LiteralPath $logPath -ErrorAction SilentlyContinue | Select-Object -Last 80) -join "`n" } catch {}
      throw ("llama-server exited early (exit={0}). Log tail:`n{1}" -f $p.ExitCode, $tail)
    }
    Start-Sleep -Milliseconds 500
  }
  $tail = ""
  try { $tail = (Get-Content -LiteralPath $logPath -ErrorAction SilentlyContinue | Select-Object -Last 80) -join "`n" } catch {}
  throw ("llama-server did not become ready at {0}/models. Log tail:`n{1}" -f $openAIBase, $tail)
}

function Get-NvidiaSmiExe {
  $cmd = Get-Command "nvidia-smi.exe" -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  $cmd2 = Get-Command "nvidia-smi" -ErrorAction SilentlyContinue
  if ($cmd2) { return $cmd2.Source }
  return ""
}

function Get-PreferredModelPathForProfile {
  param([Parameter(Mandatory = $true)][string]$Profile)
  if ($Profile -eq "dense") {
    return "I:\Models\Qwen-Local\Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-Q5_K_P.gguf"
  }
  return "I:\Models\Qwen-Local\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf"
}

function Get-RecommendLmGpuOffload {
  param(
    [Parameter(Mandatory = $true)][string]$Profile,
    [double]$Requested = 1.0,
    [string]$ModelPathOverride = ""
  )

  # 1.0 = все слои на GPU. Запас под драйвер/DWM — за счёт того, что GGUF ~19–21 ГБ на карте 24 ГБ, а не занижением --gpu.
  $req = [Math]::Round([Math]::Min(1.0, [Math]::Max(0.0, $Requested)), 2)

  $totalMiB = 24576.0
  $smi = Get-NvidiaSmiExe
  if ($smi) {
    try {
      $raw = (& $smi --query-gpu=memory.total --format=csv,noheader,nounits 2>$null | Select-Object -First 1)
      if ($raw) {
        $parsed = [double]($raw.Trim())
        if ($parsed -gt 0) { $totalMiB = $parsed }
      }
    } catch {}
  }

  $modelPath = if ($ModelPathOverride -and $ModelPathOverride.Trim() -and (Test-Path -LiteralPath $ModelPathOverride.Trim())) {
    (Resolve-Path -LiteralPath $ModelPathOverride.Trim()).Path
  } else {
    Get-PreferredModelPathForProfile -Profile $Profile
  }
  if (-not (Test-Path -LiteralPath $modelPath)) {
    return $req
  }

  $sizeMiB = [Math]::Ceiling((Get-Item -LiteralPath $modelPath).Length / 1MB)
  $overhead = if ($Profile -eq "dense") { 1.08 } else { 1.06 }
  $estimatedModelMiB = [Math]::Ceiling($sizeMiB * $overhead)

  # Только если оценка «вес + KV/оверход» не влезает в VRAM — мягко ограничиваем долю GPU (редкий случай).
  $vramFloorMiB = 384.0
  if ($estimatedModelMiB + $vramFloorMiB -gt $totalMiB) {
    $cap = [Math]::Max(0.5, ($totalMiB - $vramFloorMiB) / $estimatedModelMiB)
    return [Math]::Round([Math]::Min($req, $cap), 2)
  }
  return $req
}

function Get-GpuMemMiBForPid([int]$ProcessId) {
  $smi = Get-NvidiaSmiExe
  if (-not $smi) { return -1 }
  try {
    $out = & $smi --query-compute-apps=pid,used_gpu_memory --format=csv,noheader,nounits 2>$null
    foreach ($line in ($out | Where-Object { $_ })) {
      $parts = $line -split "," | ForEach-Object { $_.Trim() }
      if ($parts.Count -ge 2) {
        $pidStr = $parts[0]
        $memStr = $parts[1]
        if ($pidStr -as [int] -eq $ProcessId) {
          return [int]$memStr
        }
      }
    }
  } catch {}
  return 0
}

function Assert-LlamaServerUsesVram {
  param(
    [Parameter(Mandatory=$true)]$LlamaProc,
    [string]$LogPath = "",
    [int]$MinMiB = 8192
  )

  if (-not $LlamaProc) { return }
  $smi = Get-NvidiaSmiExe
  if ($smi) {
    # Prefer total VRAM usage on Windows/WDDM.
    for ($i = 0; $i -lt 40; $i++) {
      try {
        $usedLine = (& $smi --query-gpu=memory.used --format=csv,noheader,nounits 2>$null | Select-Object -First 1)
        $usedStr = if ($null -ne $usedLine) { [string]$usedLine } else { "" }
        $memUsed = 0
        if ($usedStr.Trim().Length -gt 0 -and [int]::TryParse($usedStr.Trim(), [ref]$memUsed)) {
          if ($memUsed -ge $MinMiB) { return }
        }
      } catch {}
      Start-Sleep -Milliseconds 500
    }
  }

  # On Windows/WDDM nvidia-smi per-PID memory is often N/A; use llama-server log as source of truth.
  # Важно: regex только в одинарных кавычках — в двойных '\s' превращается в буквальные '\s' и никогда не матчит лог.
  if ($LogPath -and (Test-Path -LiteralPath $LogPath)) {
    for ($i = 0; $i -lt 120; $i++) {
      try {
        $txt = Get-Content -LiteralPath $LogPath -ErrorAction SilentlyContinue
        $m = ($txt | Select-String -Pattern 'CUDA0 model buffer size\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*MiB' -AllMatches | Select-Object -Last 1)
        if ($m -and $m.Matches -and $m.Matches.Count -gt 0) {
          $raw = $m.Matches[0].Groups[1].Value
          $val = [double]::Parse($raw, [System.Globalization.CultureInfo]::InvariantCulture)
          if ($val -ge $MinMiB) { return }
        }
      } catch {}
      Start-Sleep -Milliseconds 500
    }

    $tail = ""
    try { $tail = (Get-Content -LiteralPath $LogPath -ErrorAction SilentlyContinue | Select-Object -Last 60) -join "`n" } catch {}
    throw "llama-server запустился, но не видно выделения VRAM по логу ($LogPath). Хвост лога:`n$tail"
  }
}

function Get-LlamaCppCtxCandidates {
  param(
    [Parameter(Mandatory = $true)][int]$RequestedContext,
    [Parameter(Mandatory = $true)][string]$Profile
  )

  if ($RequestedContext -gt 0) {
    return @($RequestedContext)
  }

  # Авто-режим по умолчанию: оптимизируем под скорость/интерактивность.
  # Большой n_ctx резко режет tok/s (attention сканирует весь KV).
  if ($Profile -eq "dense") {
    return @(16384, 12288, 8192)
  }
  return @(24576, 16384, 12288, 8192)
}

function Set-LlamaLocalBypassProxyEnv {
  # httpx в free-claude-code по умолчанию читает HTTP(S)_PROXY из окружения.
  # Если системный/корпоративный прокси задан, запросы к 127.0.0.1:1240 идут через него → 503, пустое тело,
  # в ответе часто видно proxy-connection: close (см. server.log после POST /v1/chat/completions).
  $env:NO_PROXY = "127.0.0.1,127.0.0.1:1234,127.0.0.1:1240,127.0.0.1:1241,127.0.0.1:8084,127.0.0.1:8085,localhost,::1"
  foreach ($k in @('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy')) {
    Remove-Item "Env:$k" -ErrorAction SilentlyContinue
  }
}

function Ensure-FreeClaudeCodeProxyLocal {
  param(
    [Parameter(Mandatory = $true)][string]$ProviderModel,
    [Parameter(Mandatory = $true)][string]$LlamaCppBaseUrl,
    [int]$ProxyPort = 8084,
    [string]$AuthToken = "freecc"
  )

  # Всегда перезапускаем прокси: иначе после прошлой сессии остаётся старый uvicorn с кэшем Settings/другим MODEL,
  # а llama уже перезапущена → 503 / рассинхрон при смене dense/moe или новом FCC_ENV_FILE.
  try {
    Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $ProxyPort -ErrorAction SilentlyContinue |
      Where-Object { $_.State -eq "Listen" } |
      ForEach-Object {
        if ($_.OwningProcess) { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
      }
  } catch {}
  Start-Sleep -Milliseconds 600

  $dir = "I:\qwen-local-setup\free-claude-code"
  if (-not (Test-Path -LiteralPath $dir)) { throw "free-claude-code dir not found: $dir" }

  $uv = "C:\Users\chelaxian\.local\bin\uv.exe"
  if (-not (Test-Path -LiteralPath $uv)) { throw "uv.exe not found at $uv" }

  $logDir = Join-Path $HOME ".qwen-local-setup"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $outLog = Join-Path $logDir "free-claude-code.local.$stamp.out.log"
  $errLog = Join-Path $logDir "free-claude-code.local.$stamp.err.log"

  # free-claude-code: в репозитории .env задаёт LLAMACPP_BASE_URL=http://localhost:8080/v1.
  # `uv run` подмешивает .env в окружение дочернего Python и может перетереть переменные
  # родительского PowerShell → валидация модели бьёт не в тот llama-server (InternalServerError).
  # FCC_ENV_FILE подключается последним (см. config/settings._env_files) и переопределяет .env.
  $fccOverride = Join-Path $logDir ("fcc-local-override.$stamp.env")
  $overrideUtf8 = New-Object System.Text.UTF8Encoding($false)
  $ov = [System.Collections.Generic.List[string]]::new()
  [void]$ov.Add(("LLAMACPP_BASE_URL={0}" -f $LlamaCppBaseUrl.TrimEnd("/")))
  [void]$ov.Add(("MODEL={0}" -f $ProviderModel))
  [void]$ov.Add(("ANTHROPIC_AUTH_TOKEN={0}" -f $AuthToken))
  [void]$ov.Add("MESSAGING_PLATFORM=none")
  # В корневом .env часто ENABLE_WEB_SERVER_TOOLS=true — для Claude Code с локальными tools это лишний путь и 503.
  [void]$ov.Add("ENABLE_WEB_SERVER_TOOLS=false")
  # ENABLE_MODEL_THINKING не трогаем: при llama --reasoning on в потоке идёт reasoning_content;
  # если выключить thinking в прокси, дельты отбрасываются → пустой ответ / странные ошибки в клиенте.
  # Некоторые сборки llama-server отдают 500 на /v1/models при проверке OpenAI SDK/httpx.
  [void]$ov.Add("FCC_SKIP_CONFIGURED_MODEL_VALIDATION=true")
  # То же, что Set-LlamaLocalBypassProxyEnv: uv run подмешивает .env репозитория, где может быть HTTP_PROXY.
  [void]$ov.Add("NO_PROXY=127.0.0.1,127.0.0.1:1234,127.0.0.1:1240,127.0.0.1:1241,127.0.0.1:8084,127.0.0.1:8085,localhost,::1")
  [void]$ov.Add("HTTP_PROXY=")
  [void]$ov.Add("HTTPS_PROXY=")
  [void]$ov.Add("ALL_PROXY=")
  [System.IO.File]::WriteAllText($fccOverride, ($ov -join "`n"), $overrideUtf8)

  Push-Location $dir
  try {
    Set-LlamaLocalBypassProxyEnv
    $env:LLAMACPP_BASE_URL = $LlamaCppBaseUrl
    $env:MODEL = $ProviderModel
    $env:ANTHROPIC_AUTH_TOKEN = $AuthToken
    $env:FCC_ENV_FILE = $fccOverride
    $env:MESSAGING_PLATFORM = "none"

    $cmd = "& `"$uv`" run uvicorn server:app --host 127.0.0.1 --port $ProxyPort"
    $p = Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-Command",$cmd) -WindowStyle Hidden -PassThru -RedirectStandardOutput $outLog -RedirectStandardError $errLog
  } finally {
    Pop-Location
  }

  $base = ("http://127.0.0.1:{0}" -f $ProxyPort)
  for ($i = 0; $i -lt 60; $i++) {
    try {
      if (Test-HttpResponding -Url ($base + "/v1/models") -TimeoutSec 2) {
        return @{ BaseUrl = $base; AuthToken = $AuthToken }
      }
    } catch {}
    if ($p -and $p.HasExited) {
      throw "free-claude-code proxy exited early (exit=$($p.ExitCode)). Logs: $errLog ; $outLog"
    }
    Start-Sleep -Seconds 1
  }
  throw "free-claude-code proxy did not become ready on $base. Logs: $errLog ; $outLog"
}

function Test-ProxyQuickMessage {
  param(
    [Parameter(Mandatory=$true)][string]$ProxyBaseUrl,
    [Parameter(Mandatory=$true)][string]$AuthToken,
    [Parameter(Mandatory=$true)][string]$ModelId,
    [int]$TimeoutSec = 60,
    [int]$MaxTokens = 128
  )

  # free-claude-code always returns Anthropic-style SSE (text/event-stream).
  # Invoke-RestMethod expects JSON and fails or misbehaves; buffer the full body via WebRequest.
  $msg = @{
    model = $ModelId
    max_tokens = $MaxTokens
    temperature = 0
    stream = $true
    messages = @(@{ role = "user"; content = "ping" })
  } | ConvertTo-Json -Depth 8

  $headers = @{
    "Authorization" = ("Bearer {0}" -f $AuthToken)
    "anthropic-version" = "2023-06-01"
  }
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    $uri = $ProxyBaseUrl.TrimEnd("/") + "/v1/messages"
    $r = Invoke-WebRequest -Uri $uri -Method Post -ContentType "application/json; charset=utf-8" -Headers $headers -Body $msg -TimeoutSec $TimeoutSec -UseBasicParsing
    $sw.Stop()
    $len = 0
    if ($null -ne $r.Content) { $len = $r.Content.Length }
    $ok = ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300 -and $len -gt 0)
    return @{
      ok = $ok
      ms = $sw.ElapsedMilliseconds
    }
  } catch {
    $sw.Stop()
    return @{
      ok = $false
      ms = $sw.ElapsedMilliseconds
      error = $_.Exception.Message
    }
  }
}

function Get-OpenAIModelIds([string]$BaseUrl) {
  $resp = Invoke-RestMethod -Uri ($BaseUrl.TrimEnd("/") + "/models") -Method Get -TimeoutSec 15
  $ids = @()
  if ($resp.PSObject.Properties.Name -contains "data" -and $resp.data) {
    $ids = @($resp.data | ForEach-Object { $_.id } | Where-Object { $_ })
  } elseif ($resp.PSObject.Properties.Name -contains "models") {
    $ids = @($resp.models | ForEach-Object { $_.id } | Where-Object { $_ })
  }
  return $ids
}

function Test-ModelIdsMatchGgufFile {
  param(
    [string[]]$Ids,
    [Parameter(Mandatory = $true)][string]$GgufPath
  )
  if (-not $Ids -or $Ids.Count -eq 0) { return $false }
  if (-not (Test-Path -LiteralPath $GgufPath)) { return $false }
  $leaf = [System.IO.Path]::GetFileName($GgufPath)
  $normGguf = ($GgufPath -replace "\\","/")
  foreach ($id in $Ids) {
    if (-not $id) { continue }
    if ($id -eq $leaf) { return $true }
    if ($id -like "*$leaf*") { return $true }
    $normId = ($id -replace "\\","/")
    if ($normGguf -and ($normId -like "*$normGguf*" -or $normGguf -like "*$normId*")) { return $true }
  }
  return $false
}

function Test-LlamaCppActiveModelOnPort {
  param(
    [Parameter(Mandatory = $true)][int]$Port,
    [Parameter(Mandatory = $true)][string]$GgufPath
  )
  try {
    $ids = Get-OpenAIModelIds -BaseUrl ("http://127.0.0.1:{0}/v1" -f $Port)
    return (Test-ModelIdsMatchGgufFile -Ids $ids -GgufPath $GgufPath)
  } catch {
    return $false
  }
}

function Get-ModelId {
  param(
    [string]$BaseUrl,
    [string]$Profile,
    [string]$CustomPathHint = ""
  )
  $ids = Get-OpenAIModelIds -BaseUrl $BaseUrl
  if ($CustomPathHint -and $CustomPathHint.Trim() -and (Test-Path -LiteralPath $CustomPathHint.Trim())) {
    $rp = (Resolve-Path -LiteralPath $CustomPathHint.Trim()).Path
    $leaf = [System.IO.Path]::GetFileName($rp)
    $rpSlash = ($rp -replace "\\","/")
    foreach ($id in $ids) {
      if (-not $id) { continue }
      if ($id -eq $leaf -or $id -like "*$leaf*") { return $id }
      $idSlash = ($id -replace "\\","/")
      if ($idSlash -like "*$leaf*" -or $rpSlash -like "*$idSlash*") { return $id }
    }
    if ($ids.Count -eq 1 -and $ids[0]) { return $ids[0] }
  }
  if ($Profile -eq "dense") {
    $m = $ids | Where-Object { $_ -match "27b" } | Select-Object -First 1
    if (-not $m) { $m = $ids | Select-Object -First 1 }
    return $m
  }
  $n = $ids | Where-Object { $_ -match "35b|a3b" } | Select-Object -First 1
  if (-not $n) { $n = $ids | Select-Object -First 1 }
  return $n
}

function Get-ModelIdWithRetry([string]$BaseUrl,[string]$Profile,[string]$LmsExe,[string]$Root,[int]$Port,[string]$CustomPathHint = "") {
  for ($i = 0; $i -lt 4; $i++) {
    try {
      $m = Get-ModelId -BaseUrl $BaseUrl -Profile $Profile -CustomPathHint $CustomPathHint
      if ($m) { return $m }
    } catch {}
    Ensure-Server -LmsExe $LmsExe -Root $Root -Port $Port
    Start-Sleep -Seconds 2
  }
  return ""
}

function Ensure-ClaudeSettings {
  param([bool]$EnableMem)
  $dir = Join-Path $HOME ".claude"
  if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $path = Join-Path $dir "settings.json"
  $obj = @{}
  if (Test-Path -LiteralPath $path) {
    try { $obj = (Get-Content -Raw -LiteralPath $path | ConvertFrom-Json) } catch { $obj = @{} }
  }
  if (-not $obj.env) { $obj | Add-Member -NotePropertyName env -NotePropertyValue @{} -Force }
  $obj.env.CLAUDE_CODE_ATTRIBUTION_HEADER = "0"
  $obj.env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"

  # Local sessions: keep prompts clean unless explicitly enabled.
  # claude-mem plugin injects a SessionStart block into Claude Code.
  if (-not $obj.enabledPlugins) { $obj | Add-Member -NotePropertyName enabledPlugins -NotePropertyValue @{} -Force }
  $obj.enabledPlugins."claude-mem@thedotmack" = [bool]$EnableMem

  # Write UTF-8 WITHOUT BOM (some tooling mis-parses BOM as an unexpected token).
  $json = ($obj | ConvertTo-Json -Depth 10)
  $enc = New-Object System.Text.UTF8Encoding($false)
  for ($i = 0; $i -lt 20; $i++) {
    try {
      [System.IO.File]::WriteAllText($path, $json, $enc)
      return
    } catch {
      Start-Sleep -Milliseconds 250
    }
  }
  [System.IO.File]::WriteAllText($path, $json, $enc)
}

function Ensure-ClaudeMemWorker {
  param([bool]$Enabled)
  if (-not $Enabled) { return }

  # If the observer UI is already up, assume worker is running.
  if (Test-HttpOk -Url "http://127.0.0.1:37777" -TimeoutSec 2) { return }

  $logDir = Join-Path $HOME ".qwen-local-setup"
  if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
  $logPath = Join-Path $logDir "claude-mem.boot.log"
  Remove-Item -LiteralPath $logPath -ErrorAction SilentlyContinue

  try {
    $bunBin = "C:\Users\chelaxian\.bun\bin"
    if (Test-Path -LiteralPath $bunBin) { $env:PATH = $bunBin + ";" + $env:PATH }

    # If worker is already running, we're done.
    $status = ""
    try { $status = (npx claude-mem status 2>&1 | Out-String) } catch {}
    if ($status -match "Worker is running") { return }

    "[$(Get-Date -Format o)] npx claude-mem start" | Set-Content -LiteralPath $logPath -Encoding UTF8
    $out = (npx claude-mem start 2>&1 | Out-String)
    $out | Add-Content -LiteralPath $logPath -Encoding UTF8

    # Wait for observer to become reachable (can take a bit on first boot).
    for ($i = 0; $i -lt 60; $i++) {
      if (Test-HttpOk -Url "http://127.0.0.1:37777" -TimeoutSec 2) { return }
      Start-Sleep -Seconds 1
    }

    Write-Host "Warning: claude-mem observer did not become ready on http://127.0.0.1:37777 (see $logPath)." -ForegroundColor Yellow
  } catch {
    Write-Host "Warning: failed to start claude-mem worker (see $logPath)." -ForegroundColor Yellow
  }
}

function Ensure-ObsidianVault {
  param([string]$VaultPath)
  if (-not $VaultPath -or $VaultPath.Trim().Length -eq 0) { return "" }
  if (-not (Test-Path -LiteralPath $VaultPath)) {
    New-Item -ItemType Directory -Path $VaultPath | Out-Null
  }
  foreach ($d in @("00 Inbox","01 Projects","02 Daily","03 Templates","99 Meta")) {
    $p = Join-Path $VaultPath $d
    if (-not (Test-Path -LiteralPath $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
  }

  $homeNotePath = Join-Path $VaultPath "99 Meta\\Home.md"
  if (-not (Test-Path -LiteralPath $homeNotePath)) {
    @(
      "# Home",
      "",
      "- [Observer (claude-mem)](http://127.0.0.1:37777)",
      "- Быстрый захват: ``00 Inbox/Inbox.md``",
      "- Шаблоны: ``03 Templates/``",
      "",
      "## Ежедневный ритм",
      "- Утром: открыть ``02 Daily/`` и создать дневную заметку",
      "- В течение дня: быстрые мысли/ссылки → ``00 Inbox/Inbox.md``",
      "- Вечером: разнести по проектам в ``01 Projects/``",
      ""
    ) | Set-Content -LiteralPath $homeNotePath -Encoding UTF8
  }

  $inbox = Join-Path $VaultPath "00 Inbox\\Inbox.md"
  if (-not (Test-Path -LiteralPath $inbox)) {
    @(
      "# Inbox",
      "",
      "## Быстрые заметки",
      "- ",
      ""
    ) | Set-Content -LiteralPath $inbox -Encoding UTF8
  }

  $template = Join-Path $VaultPath "03 Templates\\Capture.md"
  if (-not (Test-Path -LiteralPath $template)) {
    @(
      "# Capture",
      "",
      "- **Контекст**:",
      "- **Что хочу получить**:",
      "- **Ограничения / риски**:",
      "- **Следующие шаги**:",
      ""
    ) | Set-Content -LiteralPath $template -Encoding UTF8
  }

  return $VaultPath
}

function Start-ObsidianApp {
  param([bool]$Enabled,[string]$PathHint,[string]$VaultPath)
  if (-not $Enabled) { return }

  # If already running, don't spawn duplicates.
  try {
    if (Get-Process -Name "Obsidian" -ErrorAction SilentlyContinue) { return }
  } catch {}

  $localAppDataExe = Join-Path $env:LOCALAPPDATA "Programs\\Obsidian\\Obsidian.exe"
  $candidates = @(
    $PathHint,
    $localAppDataExe,
    "C:\Users\chelaxian\AppData\Local\Programs\Obsidian\Obsidian.exe",
    "C:\Program Files\Obsidian\Obsidian.exe",
    "C:\Program Files (x86)\Obsidian\Obsidian.exe"
  ) | Where-Object { $_ -and $_.Trim().Length -gt 0 } | Select-Object -Unique

  foreach ($p in $candidates) {
    if (Test-Path -LiteralPath $p) {
      try {
        $obsidianArgs = @()
        if ($VaultPath -and $VaultPath.Trim().Length -gt 0) {
          $obsidianArgs += @("--vault",$VaultPath)
        }
        # Launch via cmd "start" to keep Obsidian logs out of the console.
        try {
          # Build a single cmd.exe /c string; avoid PowerShell parsing issues with escaped quotes.
          $cmdLine = 'start "" "' + $p + '"'
          if ($VaultPath -and $VaultPath.Trim().Length -gt 0) {
            $cmdLine = $cmdLine + ' --vault "' + $VaultPath + '"'
          }
          Start-Process -FilePath "cmd.exe" -ArgumentList @("/d","/c",$cmdLine) -WindowStyle Hidden | Out-Null
        } catch {
          Start-Process -FilePath $p -ArgumentList $obsidianArgs | Out-Null
        }
        Start-Sleep -Milliseconds 750
        return
      } catch {}
    }
  }
  try {
    # Fallback to protocol handler if executable path is unknown.
    Start-Process -FilePath "obsidian://open" | Out-Null
  } catch {
    $protoOk = $false
    try { $protoOk = Test-Path -LiteralPath "Registry::HKEY_CLASSES_ROOT\\obsidian" } catch {}
    if (-not $protoOk) {
      Write-Host "Warning: Obsidian was not started. Obsidian.exe was not found and obsidian:// protocol is not registered. Provide -ObsidianPath or install Obsidian." -ForegroundColor Yellow
    } else {
      Write-Host "Warning: Obsidian was not started (protocol launch failed)." -ForegroundColor Yellow
    }
  }
}

$lmsExe = $null
$openAIBase = "http://localhost:$Port/v1"
$anthropicBase = "http://localhost:$Port"
# 8k часто не хватает на системный промпт + tool schemas в Claude Code.
# Держим дефолт выше, но избегаем 65k+ чтобы не убить скорость.
$effectiveContext = if ($ContextLength -gt 0) { $ContextLength } elseif ($SessionProfile -eq "dense") { 16384 } else { 24576 }
# Первый ответ с reasoning + 27B может занимать десятки секунд; короткий таймаут даёт ложный «fail» и лишние рестарты.
$proxyProbeTimeoutSec = if ($ReasoningMode -eq "on") { 180 } else { 60 }
$proxyProbeMaxTokens = if ($ReasoningMode -eq "on") { 256 } else { 128 }
try {
  $script:SessionQuietUi = ($QuietLmStudioUi -ne 0)
  Write-SessionDiag "Starting local session: $SessionProfile (Runtime=$Runtime)" Cyan

  # Optional integrations (off by default for local LLM sessions to reduce noise and prompt bloat).
  $enableMem = ($StartClaudeMem -ne 0)
  $enableObsidian = ($StartObsidian -ne 0)

  Ensure-ClaudeMemWorker -Enabled $enableMem
  if ($enableMem -and $OpenClaudeMemObserver -ne 0) {
    try { Start-Process -FilePath "http://127.0.0.1:37777" | Out-Null } catch {}
  }

  if ($enableObsidian) {
    $defaultVault = "C:\Users\chelaxian\Documents\Obsidian Vault"
    $vault = Ensure-ObsidianVault -VaultPath $(
      if ($ObsidianVaultPath -and $ObsidianVaultPath.Trim().Length -gt 0) { $ObsidianVaultPath } else { $defaultVault }
    )
    Start-ObsidianApp -Enabled $true -PathHint $ObsidianPath -VaultPath $vault
  }

  Ensure-ClaudeSettings -EnableMem $enableMem

  # И llamacpp, и LM Studio ходят на 127.0.0.1/localhost; при HTTP(S)_PROXY запросы могут уйти в корпоративный прокси → 503/пустые ответы.
  Set-LlamaLocalBypassProxyEnv

  $skipLmReload = $false

  if ($Runtime -eq "llamacpp") {
    # Avoid clashing with LM Studio default 1234.
    $llamaPort = if ($Port -eq 1234) { if ($SessionProfile -eq "dense") { 1240 } else { 1241 } } else { $Port }
    $modelPath = if ($CustomModelPath -and $CustomModelPath.Trim()) {
      $mp = $CustomModelPath.Trim()
      if (-not (Test-Path -LiteralPath $mp)) { throw "CustomModelPath: файл не найден: $mp" }
      if (-not $mp.ToLowerInvariant().EndsWith(".gguf")) { throw "CustomModelPath: ожидается .gguf: $mp" }
      (Resolve-Path -LiteralPath $mp).Path
    } elseif ($SessionProfile -eq "dense") {
      "I:\Models\Qwen-Local\Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-Q5_K_P.gguf"
    } else {
      "I:\Models\Qwen-Local\Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf"
    }

    $pathHint = if ($CustomModelPath -and $CustomModelPath.Trim()) { $modelPath } else { "" }

    $ctxCandidates = Get-LlamaCppCtxCandidates -RequestedContext $ContextLength -Profile $SessionProfile
    $ll = $null
    $lastErr = $null
    $skipLlamaRestart = (Test-LlamaCppActiveModelOnPort -Port $llamaPort -GgufPath $modelPath)
    if ($skipLlamaRestart) {
      Write-SessionDiag ("llama.cpp: на порту {0} уже отдаётся эта модель — перезапуск сервера пропущен." -f $llamaPort) Green
      $openAIBaseEarly = "http://127.0.0.1:$llamaPort/v1"
      $ll = @{ Process = $null; BaseUrl = $openAIBaseEarly; Port = $llamaPort; LogPath = ""; TailProc = $null }
    } else {
      foreach ($ctxTry in $ctxCandidates) {
        try {
          Write-Host "llama.cpp: старт (ctx=$ctxTry)..." -ForegroundColor DarkGray
          $ll = Ensure-LlamaCppServer -ModelPath $modelPath -Port $llamaPort -ContextLength $ctxTry -Profile $SessionProfile -ShowConsole $ShowLlamaConsole
          $effectiveContext = $ctxTry
          $minVram = if ($SessionProfile -eq "moe") { 512 } else { 8192 }
          Assert-LlamaServerUsesVram -LlamaProc $ll.Process -LogPath $ll.LogPath -MinMiB $minVram
          break
        } catch {
          $lastErr = $_.Exception.Message
          Write-Host "llama.cpp: не взлетело на ctx=$ctxTry ($lastErr)" -ForegroundColor Yellow
          try { Start-Sleep -Seconds 2 } catch {}
        }
      }
    }
    if (-not $ll) { throw "llama.cpp could not start with any ctx candidate. Last error: $lastErr" }

    $openAIBase = $ll.BaseUrl

    # Route Claude Code (Anthropic) traffic through free-claude-code to llama.cpp (OpenAI).
    $modelId = (Get-ModelId -BaseUrl $openAIBase -Profile $SessionProfile -CustomPathHint $pathHint)
    if (-not $modelId) { throw "No model id available via $openAIBase/models" }

    $proxyPort = if ($SessionProfile -eq "dense") { 8084 } else { 8085 }
    $proxy = Ensure-FreeClaudeCodeProxyLocal -ProviderModel ("llamacpp/{0}" -f $modelId) -LlamaCppBaseUrl $openAIBase -ProxyPort $proxyPort -AuthToken "freecc"
    $anthropicBase = $proxy.BaseUrl
    $env:ANTHROPIC_AUTH_TOKEN = $proxy.AuthToken

    $model = $modelId

    # Fast user-experience guard: if first response is too slow, restart with smaller ctx.
    $probe = Test-ProxyQuickMessage -ProxyBaseUrl $anthropicBase -AuthToken $env:ANTHROPIC_AUTH_TOKEN -ModelId $model -TimeoutSec $proxyProbeTimeoutSec -MaxTokens $proxyProbeMaxTokens
    if (-not $probe.ok) {
      Write-Host ("llama.cpp: первый ответ через прокси не успел за {0}s ({1}). Уменьшаю ctx и перезапускаю..." -f $proxyProbeTimeoutSec, $probe.error) -ForegroundColor Yellow
      $fallback = @(32768, 24576, 16384, 12288, 8192) | Where-Object { $_ -lt $effectiveContext } | Select-Object -Unique
      $recovered = $false
      foreach ($ctxTry in $fallback) {
        try {
          $ll = Ensure-LlamaCppServer -ModelPath $modelPath -Port $llamaPort -ContextLength $ctxTry -Profile $SessionProfile -ShowConsole $ShowLlamaConsole
          $effectiveContext = $ctxTry
          $minVram = if ($SessionProfile -eq "moe") { 512 } else { 8192 }
          Assert-LlamaServerUsesVram -LlamaProc $ll.Process -LogPath $ll.LogPath -MinMiB $minVram
          $openAIBase = $ll.BaseUrl
          $modelId = (Get-ModelId -BaseUrl $openAIBase -Profile $SessionProfile -CustomPathHint $pathHint)
          if (-not $modelId) { throw "No model id available via $openAIBase/models" }
          $proxy = Ensure-FreeClaudeCodeProxyLocal -ProviderModel ("llamacpp/{0}" -f $modelId) -LlamaCppBaseUrl $openAIBase -ProxyPort $proxyPort -AuthToken "freecc"
          $anthropicBase = $proxy.BaseUrl
          $env:ANTHROPIC_AUTH_TOKEN = $proxy.AuthToken
          $model = $modelId
          $probe2 = Test-ProxyQuickMessage -ProxyBaseUrl $anthropicBase -AuthToken $env:ANTHROPIC_AUTH_TOKEN -ModelId $model -TimeoutSec $proxyProbeTimeoutSec -MaxTokens $proxyProbeMaxTokens
          if ($probe2.ok) {
            Write-Host "llama.cpp: восстановлено на ctx=$ctxTry (ttfb≈$($probe2.ms)ms)" -ForegroundColor Green
            $recovered = $true
            break
          }
        } catch {}
      }
      if (-not $recovered) {
        Write-Host "llama.cpp: предупреждение — быстрый ответ всё ещё медленный. Claude Code может 'крутиться' на первом сообщении." -ForegroundColor Yellow
      }
    } else {
      Write-Host "llama.cpp: ttfb≈$($probe.ms)ms" -ForegroundColor DarkGray
    }
  } else {
    $lmsExe = Resolve-LmsExe $LMStudioRoot
    $lmCustomResolved = ""
    if ($CustomModelPath -and $CustomModelPath.Trim()) {
      $lcp = $CustomModelPath.Trim()
      if (-not (Test-Path -LiteralPath $lcp)) { throw "CustomModelPath: файл не найден: $lcp" }
      if (-not $lcp.ToLowerInvariant().EndsWith(".gguf")) { throw "CustomModelPath: ожидается .gguf: $lcp" }
      $lmCustomResolved = (Resolve-Path -LiteralPath $lcp).Path
    }
    $lmGpuPathForVram = if ($lmCustomResolved) { $lmCustomResolved } else { "" }
    $lmGpuOffload = Get-RecommendLmGpuOffload -Profile $SessionProfile -Requested $GpuOffload -ModelPathOverride $lmGpuPathForVram
    Write-SessionDiag ("LM Studio: target GPU offload={0}" -f $lmGpuOffload.ToString("0.00",[System.Globalization.CultureInfo]::InvariantCulture)) DarkGray
    if ($StartLMStudioGui -ne 0) {
      $guiExe = Resolve-LMStudioGuiExe -ExplicitPath $LMStudioGuiExe -LmsExePath $lmsExe -SearchRoot $LMStudioRoot
      if (-not $guiExe) {
        throw "Не найден LM Studio.exe (GUI). Установи LM Studio в '$LMStudioRoot' или задай -LMStudioGuiExe 'C:\...\LM Studio.exe'."
      }
      Ensure-LMStudioGui -GuiExe $guiExe -WarmupSeconds 10
    }
    Ensure-Server -LmsExe $lmsExe -Root $LMStudioRoot -Port $Port
    $lmGgufForProbe = if ($lmCustomResolved) { $lmCustomResolved } else { Get-PreferredModelPathForProfile -Profile $SessionProfile }
    $idsNow = @()
    try { $idsNow = Get-OpenAIModelIds -BaseUrl $openAIBase } catch { $idsNow = @() }
    $skipLmReload = $false
    if ($lmGgufForProbe -and (Test-Path -LiteralPath $lmGgufForProbe) -and (Test-ModelIdsMatchGgufFile -Ids $idsNow -GgufPath $lmGgufForProbe)) {
      $skipLmReload = $true
      Write-SessionDiag "LM Studio: выбранный .gguf уже в /v1/models — пропускаю unload и предзагрузку." Green
    }
    if (-not $skipLmReload) {
      Invoke-LmsSafe -LmsExe $lmsExe -Args @("unload","--all") -IgnoreFailure | Out-Null
      Start-Sleep -Seconds 1
      [void](Load-ModelBestEffort -LmsExe $lmsExe -PreferredContext $effectiveContext -GpuOffload $lmGpuOffload)
    }
    $lmPathHint = if ($lmCustomResolved) { $lmCustomResolved } else { "" }
    $model = Get-ModelIdWithRetry -BaseUrl $openAIBase -Profile $SessionProfile -LmsExe $lmsExe -Root $LMStudioRoot -Port $Port -CustomPathHint $lmPathHint
    if (-not $model) { throw "No model id available via $openAIBase/models" }
  }

  # Force-load the selected model with the desired context length.
  # Without this, LM Studio may lazy-load with a smaller default n_ctx (e.g. 4096),
  # which can break Claude Code system prompts and tool calling.
  if ($Runtime -eq "lmstudio") {
    try {
      if (-not $skipLmReload) {
        Ensure-ModelLoaded -LmsExe $lmsExe -ModelId $model -Context $effectiveContext -GpuOffload $lmGpuOffload
      } else {
        Write-SessionDiag "LM Studio: принудительная перезагрузка модели пропущена (уже активна)." DarkGray
      }
    } catch {
      if ($DryRun -ne 0) { throw }
      Write-Host "Warning: model force-load failed; continuing with lazy-load. Details: $($_.Exception.Message)" -ForegroundColor Yellow
    }
  }

  $env:ANTHROPIC_BASE_URL = $anthropicBase
  $env:ANTHROPIC_API_KEY = "sk-local"
  if (-not $env:ANTHROPIC_AUTH_TOKEN) { $env:ANTHROPIC_AUTH_TOKEN = "local" }

  # Pin default tiers to the local model to avoid UI/model-picker drift.
  $env:ANTHROPIC_DEFAULT_OPUS_MODEL = $model
  $env:ANTHROPIC_DEFAULT_SONNET_MODEL = $model
  $env:ANTHROPIC_DEFAULT_HAIKU_MODEL = $model

  Write-Host "Claude Code model: $model" -ForegroundColor Green

  if ($DryRun -ne 0) {
    if ($Runtime -eq "llamacpp") {
      # End-to-end: Claude Code -> Anthropic proxy -> llama.cpp (SSE, not JSON)
      $dr = Test-ProxyQuickMessage -ProxyBaseUrl $anthropicBase -AuthToken $env:ANTHROPIC_AUTH_TOKEN -ModelId $model -TimeoutSec ([Math]::Max($proxyProbeTimeoutSec, 90)) -MaxTokens $proxyProbeMaxTokens
      if (-not $dr.ok) { throw "dry-run failed: $($dr.error)" }
      Write-Host "dry-run:OK" -ForegroundColor Green
      return
    } else {
      # Minimal end-to-end smoke test: OpenAI-compatible request to LM Studio.
      $body = @{
        model = $model
        messages = @(@{ role = "user"; content = "ping" })
        max_tokens = 16
        temperature = 0
      } | ConvertTo-Json -Depth 6

      try {
        $resp = Invoke-RestMethod -Uri ($openAIBase.TrimEnd("/") + "/chat/completions") -Method Post -ContentType "application/json" -Body $body -TimeoutSec 60
        if (-not $resp) { throw "empty response" }
        Write-Host "dry-run:OK" -ForegroundColor Green
        return
      } catch {
        throw "dry-run failed: $($_.Exception.Message)"
      }
    }
  }

  $toolsArg = $null
  if ($ClaudeTools -eq "minimal") {
    # Keep tool calling, but reduce schema size to fit small n_ctx.
    $toolsArg = "Read,Edit,Bash,Glob,Grep"
  } elseif ($ClaudeTools -eq "default") {
    $toolsArg = $null
  } else {
    # Allow custom comma/space list, or empty string to disable tools.
    $toolsArg = $ClaudeTools
  }

  $claudeHelper = Join-Path $PSScriptRoot "invoke-claude-in-console.ps1"
  if (-not (Test-Path -LiteralPath $claudeHelper)) {
    throw "Не найден invoke-claude-in-console.ps1: $claudeHelper"
  }
  $workDir = (Get-Location).Path
  # Тихий LM Studio: отдельное окно для Claude Code — в этом процессе не остаётся interleaved stdout от Electron/LMS.
  if ($Runtime -eq "lmstudio" -and ($QuietLmStudioUi -ne 0)) {
    Write-Host "Claude Code откроется в отдельном окне PowerShell. Это окно можно свернуть; после выхода из Claude здесь появится сообщение о выгрузке модели." -ForegroundColor DarkCyan
    $psiArgs = [System.Collections.Generic.List[string]]::new()
    [void]$psiArgs.Add("-NoProfile")
    [void]$psiArgs.Add("-ExecutionPolicy")
    [void]$psiArgs.Add("Bypass")
    [void]$psiArgs.Add("-File")
    [void]$psiArgs.Add($claudeHelper)
    [void]$psiArgs.Add("-Model")
    [void]$psiArgs.Add($model)
    if ($null -ne $toolsArg) {
      [void]$psiArgs.Add("-Tools")
      [void]$psiArgs.Add($toolsArg)
    }
    $p = Start-Process -FilePath "powershell.exe" -ArgumentList @($psiArgs.ToArray()) -WorkingDirectory $workDir -Wait -PassThru
    if ($p -and $p.ExitCode -ne 0) {
      Write-Host ("Claude Code завершился с кодом {0}." -f $p.ExitCode) -ForegroundColor Yellow
    }
  } elseif ($null -ne $toolsArg) {
    & claude --model $model --tools $toolsArg
  } else {
    & claude --model $model
  }
}
finally {
  Write-Host "Stopping local endpoint and freeing VRAM..." -ForegroundColor Yellow
  if ($Runtime -eq "lmstudio") {
    Invoke-LmsSafe -LmsExe $lmsExe -Args @("unload","--all") -IgnoreFailure | Out-Null
    Invoke-LmsSafe -LmsExe $lmsExe -Args @("server","stop") -IgnoreFailure | Out-Null
  }
}
```

> **Примечание:** строки `freecc`, `sk-local`, `local` — **локальные заглушки** для маршрутизации к прокси. В `free-claude-code` должен быть согласованный `ANTHROPIC_AUTH_TOKEN`. Лаунчер подмешивает **`FCC_ENV_FILE`** с **`LLAMACPP_BASE_URL`** — см. **§7.5**.

---
## 14. Краткий чеклист: что проверить при сбое (503, пустой ответ, reasoning)

1. **`free-claude-code/server.log`** в каталоге репозитория прокси — по **`request_id`** из ошибки Claude Code; убедиться, что **`POST`** на **`127.0.0.1:1240|1241`** не даёт **503** с **`proxy-connection`** (признак ухода на системный прокси).
2. **`Set-LlamaLocalBypassProxyEnv`** / строка **`NO_PROXY`** в **`fcc-local-override*.env`** (§7.5); при необходимости вручную отключить системный прокси для локальных адресов в параметрах Windows.
3. Актуальность **`FCC_ENV_FILE`**: после смены dense/moe или порта llama перезапускается **новый** uvicorn с новым override; старый процесс на **8084/8085** не должен оставаться слушать.
4. Согласованность **reasoning**: **`--reasoning on`** в llama и отсутствие принудительного **`ENABLE_MODEL_THINKING=false`** в override (§7.5).
5. **`%TEMP%\llama-server-<порт>.log`** — загрузка модели, **offload**, ошибки контекста (**`FATAL_NCTX_TOO_LARGE`** и автопонижение ctx в лаунчере).
6. По необходимости временно **`LOG_API_ERROR_TRACEBACKS=true`** для полного traceback в логах прокси.

Подробности и таблица патчей — **§7.5**.

---

## 15. Быстрая проверка после переноса

```powershell
# LM Studio: только проверка цепочки (без интерактива Claude)
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\qwen-local-setup\scripts\run-claude-local-session.ps1" `
  -SessionProfile moe -Runtime lmstudio -Port 1234 -ContextLength 16384 -DryRun 1

# llama.cpp + прокси: dry-run
powershell -NoProfile -ExecutionPolicy Bypass -File "D:\qwen-local-setup\scripts\run-claude-local-session.ps1" `
  -SessionProfile dense -Runtime llamacpp -ContextLength 8192 -DryRun 1 -ShowLlamaConsole 1
```

---

## 16. Конфиденциальность

В инструкцию **не** включайте: ключи Anthropic/OpenAI, токены ngrok, пароли, содержимое `.env` с секретами. Для ngrok достаточно: «выполнить официальную настройку `ngrok config add-authtoken` на машине».

---
