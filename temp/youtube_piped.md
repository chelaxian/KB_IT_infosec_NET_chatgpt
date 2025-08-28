Красота — летит! Теперь про «Поделиться».

Ты хочешь, чтобы:

1. по умолчанию галочка «Ссылка Piped» была **снята** (генерировалась ссылка YouTube), и
2. желательно вообще убрать этот переключатель, чтобы нельзя было показать твой домен.

Самый чистый способ — собрать **кастомный frontend** с изменённым компонентом окна «Поделиться». Ниже даю два варианта: «правильный» (сборка) и «быстрый хак без сборки».

---

# Вариант A (рекомендуется): свой образ piped-frontend

### 1) Склонировать фронт

```bash
cd ~/Browser/piped
git clone https://github.com/TeamPiped/piped-frontend.git
cd piped-frontend
```

### 2) Изменить компонент ShareModal (снимаем галку и прячем опцию)

Открой файл (путь может быть `src/components/Share/ShareModal.vue` или близкий — в проекте легко найти по слову `Share`):

* логика: переменная вида `usePipedLink`/`pipedLink`/`sharePipedLink` обычно инициализируется `true`.
  Поменяй **на `false`**.
* чтобы убрать сам переключатель, оберни блок чекбокса в `v-if="false"` или просто закомментируй/удали разметку чекбокса.

Пример сути правки (псевдокод, в реальном файле имена могут отличаться):

```vue
<script setup>
import { ref } from 'vue'

// было:
const usePipedLink = ref(true)

// стало:
const usePipedLink = ref(false)
</script>

<!-- было -->
<!--
<label class="switch">
  <input type="checkbox" v-model="usePipedLink">
  <span>Ссылка Piped</span>
</label>
-->

<!-- стало: скрыто -->
<!-- v-if="false" гарантированно не отрисует -->
<label v-if="false" class="switch">
  <input type="checkbox" v-model="usePipedLink">
  <span>Ссылка Piped</span>
</label>
```

> Если хочешь только «галка снята по умолчанию», но оставить возможность включить — убери только первую правку (false), чекбокс не скрывай.

### 3) Собрать и запаковать Docker-образ

В корне фронта есть Dockerfile. Запускаем сборку:

```bash
# из каталога piped-frontend
docker build -t piped-frontend:custom .
```

### 4) Подменить образ в твоём docker-compose.yml

В твоём `~/Browser/piped/Piped-Docker/docker-compose.yml` замени сервис `piped-frontend`:

```yaml
services:
  piped-frontend:
    image: piped-frontend:custom         # было 1337kavin/piped-frontend:latest
    restart: unless-stopped
    depends_on:
      - piped
    environment:
      BACKEND_HOSTNAME: pipedapi.ratu.sh
      HTTP_MODE: https
    container_name: piped-frontend
```

### 5) Перезапустить только фронт (или весь стек)

```bash
cd ~/Browser/piped/Piped-Docker
docker compose up -d piped-frontend
# если сменилась статика nginx — можно:
# docker compose up -d
```

### 6) Отключи автообновление фронта в watchtower

Иначе он снова притащит upstream-образ. В твоём `watchtower` уже стоит явный список; просто **не** включай `piped-frontend` туда, либо зафиксируй тег `piped-frontend:custom` — watchtower его не тронет.

---

# Вариант B (быстрый хак, без сборки образа)

Если пока не хочешь собирать фронт, можно «насильно»:

* по умолчанию делать YouTube-ссылку,
* и/или скрыть переключатель на уровне Nginx (проксирующего контейнера) через маленький JS + CSS.

### Идея

Мы подсовываем странице крошечный `custom.js`, который:

* один раз снимет галку (если компонент читает состояние из localStorage — выставим ему «YouTube»),
* спрячем виджет переключателя.

### 1) Создай файлы

В каталоге `~/Browser/piped/Piped-Docker/config` добавь:

`share-tweak.js`:

```js
(function () {
  // Попробуем задать предпочитаемую опцию до инициализации UI
  try {
    // Если фронт использует localStorage — сохраняем «используй оригинальную ссылку»
    // Названия ключей зависят от версии. Часто встречается что-то вроде:
    // 'shareUsePipedLink' / 'pipedShare' / 'usePipedLink'.
    // Сразу зададим несколько безопасных вариантов.
    localStorage.setItem('shareUsePipedLink', 'false');
    localStorage.setItem('pipedShare', '0');
    localStorage.setItem('usePipedLink', 'false');
  } catch (e) {}

  // Подождём загрузки DOM и спрячем элемент чекбокса (селектор подстрахован по тексту)
  const hide = () => {
    // Попробуем найти по тексту «Ссылка Piped» и скрыть ближайший label/строку
    const allLabels = Array.from(document.querySelectorAll('label, .switch, .v-input, .v-list-item'));
    const el = allLabels.find(n => /Ссылка\s*Piped/i.test(n.textContent || ''));
    if (el) {
      el.style.display = 'none';
      return true;
    }
    return false;
  };

  const tryHideLoop = () => {
    if (!hide()) setTimeout(tryHideLoop, 200);
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tryHideLoop);
  } else {
    tryHideLoop();
  }
})();
```

`share-tweak.conf`:

```nginx
# Вставляем наш JS в конец <head> главной страницы
sub_filter_once off;
sub_filter '</head>' '<script src="/__custom/share-tweak.js"></script></head>';
```

### 2) Смонтируй эти файлы в nginx-контейнер и подключи

В твоём `docker-compose.yml` у сервиса `nginx` добавь volume и include:

```yaml
services:
  nginx:
    image: nginx:mainline-alpine
    # ...
    volumes:
      - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./config/pipedapi.conf:/etc/nginx/conf.d/pipedapi.conf:ro
      - ./config/pipedproxy.conf:/etc/nginx/conf.d/pipedproxy.conf:ro
      - ./config/pipedfrontend.conf:/etc/nginx/conf.d/pipedfrontend.conf:ro
      - ./config/ytproxy.conf:/etc/nginx/snippets/ytproxy.conf:ro
      - ./config/share-tweak.js:/usr/share/nginx/html/__custom/share-tweak.js:ro
      - ./config/share-tweak.conf:/etc/nginx/snippets/share-tweak.conf:ro
      - piped-proxy:/var/run/ytproxy
```

А в `config/pipedfrontend.conf` (сервер для `piped.ratu.sh`) добавь строку:

```nginx
server {
    # ... как у тебя сейчас ...
    include /etc/nginx/snippets/share-tweak.conf;
}
```

Перезапусти nginx:

```bash
docker compose up -d nginx
```

Этот способ не меняет исходники и переживёт обновление фронта, но он «хакает» DOM — не такой красивый как сборка, зато быстрый.

---

## Как проверить

1. Открой `https://piped.ratu.sh`, зайди в «Поделиться»: по умолчанию должна быть **YouTube-ссылка**.
2. Если выбрал «полностью убрать» — переключателя не будет видно.
3. Проконтролируй кэш: сделай Ctrl+F5/очисти кэш браузера.

---

Хочешь — могу подготовить минимальный патч для фронта под конкретную версию (дам точный файл и дифф), но и один, и второй способ выше решают задачу.
