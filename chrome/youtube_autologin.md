# Автоматизация автообновления куки на YouTube

Понадобятся следующие расширения:
- [LastPass](https://chromewebstore.google.com/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd)
- [Violentmonkey](https://chromewebstore.google.com/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag)
- [Accept all cookies](https://chromewebstore.google.com/detail/accept-all-cookies/ofpnikijgfhlmmjlpkfaifhhdonchhoi)
- [Cookie AutoDelete](https://chromewebstore.google.com/detail/cookie-autodelete/fhcgjolkccmbidfldomjliifgaodjagh)
- (необязательно) [Auto Refresh Plus | Page Monitor](https://chromewebstore.google.com/detail/auto-refresh-plus-page-mo/hgeljhfekpckiiplhkigfehkdpldcggm)
- (необязательно) [uBlock Origin](https://chromewebstore.google.com/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm)
- (необязательно) [SponsorBlock для YouTube](https://chromewebstore.google.com/detail/sponsorblock-%D0%B4%D0%BB%D1%8F-youtube/mnjggcdmjocbbbhaepdhchncahnbgone)

# Циклический вход/выход для YouTube

Данный проект позволяет автоматически разлогиниваться и залогиниваться на YouTube по заданному циклу. Скрипт реализован для расширений [Violentmonkey](https://violentmonkey.github.io/) (аналог Tampermonkey) для браузера Chrome. Для автозаполнения данных на странице логина рекомендуется использовать LastPass или аналогичный менеджер паролей.

## Установка и настройка

### 1. Установка Violentmonkey и скрипта

1. **Установка Violentmonkey:**
   - Перейдите по [ссылке](https://chrome.google.com/webstore/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag) и установите расширение в Chrome.
   
2. **Создание нового скрипта:**
   - Нажмите на иконку Violentmonkey в браузере и выберите "Создать новый скрипт" (или "New script").
   - Удалите содержимое шаблона и вставьте финальный скрипт, приведённый в разделе "Финальный скрипт" ниже.

3. **Настройка скрипта:**
   - В начале скрипта можно отредактировать константы:
     - `INTERVAL` – интервал ожидания на главной странице YouTube (например, 300000 мс для 5 минут).
     - `WAIT` – время ожидания между переходами (5000 мс для 5 секунд).
   - Проверьте, что URL-адреса для логина (`LOGIN_URL`), logout (`LOGOUT_URL`) и главной страницы (`HOMEPAGE`) и следующей страницы (`NEXTPAGE`) соответствуют вашим требованиям.
   
4. **Сохраните скрипт** и убедитесь, что он активирован.

### 2. Установка и настройка LastPass

1. **Установка LastPass:**
   - Перейдите по [ссылке](https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd) и установите расширение в Chrome.

2. **Настройка аккаунта:**
   - Нажмите на иконку LastPass в панели инструментов браузера.
   - Зарегистрируйтесь или выполните вход в уже существующий аккаунт LastPass.

3. **Сохранение учетных данных:**
   - Перейдите на страницу входа Google для YouTube (используемый URL входит в скрипт).
   - Введите свои учетные данные и, когда браузер предложит сохранить пароль, согласитесь. LastPass сохранит их для автозаполнения при последующих входах.

4. **Включение автологина:**
   - **Очень важно!** По умолчанию автологин в LastPass отключен.
   - Чтобы включить автологин:
     - Щёлкните правой кнопкой мыши по иконке LastPass в панели инструментов Chrome и выберите **Options** (Настройки).
     - Перейдите на вкладку **General** и установите галочку **Automatically fill login information**.
     - Затем перейдите во вкладку **Advanced** и отметьте опцию **Log in to sites automatically within this many seconds since last login** (укажите нужное время, например, 5-10 секунд).
   - Эти настройки позволят LastPass автоматически заполнять форму логина и инициировать вход.

5. **Проверка автозаполнения:**
   - Для проверки работы LastPass нажмите на иконку LastPass, найдите сохранённую запись для `google.com` и используйте кнопку «Launch» (Запуск), чтобы убедиться, что автозаполнение срабатывает корректно.

## Как работает скрипт

Скрипт выполняет следующие шаги в циклической последовательности:

1. **Шаг 0 (на главной странице YouTube):**
   - Ждет заданный интервал (`INTERVAL`, например, 5 минут).
   - Переходит на страницу logout (`https://www.youtube.com/logout`).
   - Устанавливает состояние цикла в "1" (сохраняется в `localStorage`).

2. **Шаг 1 (на странице logout):**
   - Ждет 5 секунд (`WAIT`).
   - Переходит на страницу логина Google (`LOGIN_URL`).
   - Устанавливает состояние цикла в "2".

3. **Шаг 3 (на странице логина):**
   - Ждет 10 секунд (`WAIT`).
   - Переходит на главную страницу YouTube (`HOMEPAGE`).
   - Устанавливает состояние цикла в "3".
  
3. **Шаг 4 (на главной странице):**
   - Ждет 5 секунд (`WAIT`).
   - Переходит на страницу YouTube LoFi Girl (`NEXTPAGE`).
   - Сбрасывает состояние цикла до "0", после чего цикл повторяется.

Для хранения состояния используется `localStorage` под ключом `ytCycleStep`.
<img width="657" height="260" alt="image" src="https://github.com/user-attachments/assets/7014dd43-04cb-4553-b1d3-2f38591f088f" />

## Финальный скрипт

```javascript
// ==UserScript==
// @name         Циклический вход/выход для YouTube (без проверок, по схеме)
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  По схеме: ждем INTERVAL, переходим на logout, ждем 2 сек, переходим на логин, ждем 2 сек, переходим на главную ждем 2 сек, переходим на LoFi Girl. Цикл повторяется.
// @match        https://www.youtube.com/*
// @match        https://accounts.google.com/v3/signin/identifier*
// @grant        none
// ==/UserScript==
(function() {
    'use strict';
    // НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ
    const INTERVAL = 6000000; // 100 минут в миллисекундах
    const WAIT = 5000;       // 5 секунд в миллисекундах
    const LOGOUT_URL = "https://www.youtube.com/logout";
    const LOGIN_URL = "https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F%253FthemeRefresh%253D1&hl=en&ifkv=ASSHykrZmMTbrRwtTdPcCL808H2MXtIBXe4kDNr1IF_omyo6oiVwXg7ubi9zbShFz6v8Ul_ILTxIvQ&passive=true&service=youtube&uilel=3&flowName=GlifWebSignIn&flowEntry=ServiceLogin";
    const HOMEPAGE = "https://www.youtube.com/";
    const NEXTPAGE = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=WL";
    // Считываем состояние цикла: "0", "1" или "2" или "3". Если не задано – по умолчанию "0"
    let step = localStorage.getItem("ytCycleStep") || "0";
    console.log("Запущен цикл. Текущий шаг:", step, " | Текущий URL:", window.location.href);
    // Если состояние "0": ждём INTERVAL и переходим на logout, устанавливая состояние "1"
    if (step === "0") {
        console.log(`Шаг 0: через ${INTERVAL/1000} секунд выполняем переход на logout.`);
        setTimeout(() => {
            localStorage.setItem("ytCycleStep", "1");
            console.log("Переход на logout.");
            window.location.href = LOGOUT_URL;
        }, INTERVAL);
    }
    // Если состояние "1": ждём WAIT и переходим на страницу логина, устанавливая состояние "2"
    else if (step === "1") {
        console.log(`Шаг 1: через ${WAIT/1000} секунд выполняем переход на логин.`);
        setTimeout(() => {
            localStorage.setItem("ytCycleStep", "2");
            console.log("Переход на страницу логина.");
            window.location.href = LOGIN_URL;
        }, WAIT);
    }
    // Если состояние "2": ждём WAIT и переходим на главную страницу, устанавливая состояние "3"
    else if (step === "2") {
        console.log(`Шаг 2: через ${2*WAIT/1000} секунд выполняем переход на главную страницу.`);
        setTimeout(() => {
            localStorage.setItem("ytCycleStep", "3");
            console.log("Переход на главную страницу YouTube.");
            window.location.href = HOMEPAGE;
        }, 2 * WAIT);
    }
    // Если состояние "3": ждём WAIT и переходим на следующую страницу, сбрасывая состояние до "0"
    else if (step === "3") {
        console.log(`Шаг 3: через ${WAIT/1000} секунд выполняем переход на следующую страницу.`);
        setTimeout(() => {
            localStorage.setItem("ytCycleStep", "0");
            console.log("Переход на страницу YouTube - LoFi Girl.");
            window.location.href = NEXTPAGE;
        }, WAIT);
    }
})();
```
### 3. Установка и настройка Accept all cookies

Просто установить и включить, ничего не настраивать

### 4. Установка и настройка Cookie AutoDelete

Установить, исключить из автоочистки `google.com` и включить автоочистку на всех страницах при смене домена, релоаде, открытии, закрытии

## Заключение

После установки и настройки скрипта, он будет выполнять заданный цикл:
1. Ждать 5 минут на YouTube.
2. Переходить на страницу logout.
3. Ждать 3 секунды.
4. Переходить на страницу логина Google (при этом LastPass автозаполнит учетные данные, если настроено).
5. Ждать 3 секунды.
6. Переходить на главную страницу YouTube и начинать цикл заново.

**Важно:**  
Убедитесь, что в настройках LastPass включены следующие опции:
- **Options → General:** поставить галочку на **Automatically fill login information**.
- **Options → Advanced:** поставить галочку на **Log in to sites automatically within this many seconds since last login** (и указать нужное время).


---

автонажатие Enter, Tab, Enter

```javascript
// ==UserScript==
// @name         Auto Press Enter and Tab Alternately (Fixed)
// @namespace    http://example.com/
// @version      1.3
// @description  Эмулирует нажатие Enter и Tab (чередуя), начиная с Enter, максимально близко к реальному поведению.
// @match        *://*/*
// @grant        none
// ==/UserScript==
(function() {
    'use strict';
    let pressEnterNext = true;

    // Функция имитации Enter
    function simulateEnter() {
        const active = document.activeElement;
        if (!active) return;
        if (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA') {
            // Вызвать submit, если поле внутри формы
            const form = active.form;
            if (form) {
                form.requestSubmit ? form.requestSubmit() : form.submit();
                console.log('AutoKeyPress: Submit form by Enter');
            } else {
                // Иначе вставить символ новой строки (для textarea)
                if (active.tagName === 'TEXTAREA') {
                    active.value += '\n';
                    active.dispatchEvent(new Event('input', { bubbles: true }));
                }
                console.log('AutoKeyPress: Enter pressed in input/textarea');
            }
        } else if (active.tagName === 'BUTTON' || active.type === 'submit') {
            active.click();
            console.log('AutoKeyPress: Enter triggered button click');
        } else {
            // Попытаться эмулировать нажатие Enter как синтетическим событием (на всякий случай)
            active.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
            active.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
            console.log('AutoKeyPress: Synthetic Enter on generic element');
        }
    }

    // Реализация Tab — переход фокуса к следующему focusable элементу
    function simulateTab() {
        const focusable = Array.from(document.querySelectorAll('a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'))
            .filter(el => !el.disabled && el.offsetParent !== null); // только видимые и активные
        const active = document.activeElement;
        const idx = focusable.indexOf(active);
        const next = focusable[(idx + 1) % focusable.length];
        if (next) next.focus();
        console.log('AutoKeyPress: Tab moved focus');
    }

    function alternateKeyPress() {
        if (pressEnterNext) simulateEnter();
        else simulateTab();
        pressEnterNext = !pressEnterNext;
    }

    setInterval(alternateKeyPress, 5000);
})();
```

---

автоматическое нажатие заданных кнопок на странице

```javascript
// ==UserScript==
// @name         AutoClick Next/SignIn Google/YT/youtu.be (Safe)
// @namespace    http://example.com/
// @version      1.9
// @description  Автоматически нажимает на нужный Google-аккаунт и спецкнопки только на Google, YouTube и youtu.be. Исключает кнопки голосового поиска и экранной клавиатуры.
// @match        *://*/*
// @grant        none
// ==/UserScript==
(function() {
    'use strict';

    const userEmails = [
        "tatapepeof@gmail.com",
        "300.tpaktop.300@gmail.com",
        "1560step@gmail.com"
    ];

    const targetWords = [
        "sign in", "next", "log in", "login", "continue", "reload", "agree", "accept"
    ];

    // Запрет на клики по элементам голосового поиска и экранной клавиатуры
    const forbiddenSelectors = [
        '[aria-label*="Голосовой поиск"]',
        '[aria-label*="voice search"]',
        '.voice-search-button',
        '.vk-keyboard',
        '[aria-label*="Экранная клавиатура"]'
    ];

    function isForbidden(element) {
        for (const sel of forbiddenSelectors) {
            if (element.matches && element.matches(sel)) return true;
        }
        return false;
    }

    const host = window.location.hostname;
    const isGoogleOrYouTube = (
        /\.google\./i.test(host) ||
        /\.youtube\./i.test(host) ||
        host === 'youtube.com' ||
        host === 'google.com' ||
        host === 'youtu.be'
    );

    if (!isGoogleOrYouTube) return;

    function simulateClick(element) {
        element.click();
        console.log(`AutoClick: Clicked: "${element.innerText || element.value || element.getAttribute('aria-label') || ''}"`);
    }

    function clickTargetElements() {
        for (const email of userEmails) {
            const accLink = document.querySelector(`[role="link"][data-identifier="${email}"]`);
            if (accLink) {
                simulateClick(accLink);
                return; // Один клик за запуск
            }
        }

        const clickableButtons = document.querySelectorAll(
            'button, input[type="button"], input[type="submit"], [role="button"]'
        );

        for (const element of clickableButtons) {
            if (element.disabled) continue;
            if (isForbidden(element)) continue; // Пропускаем запрещённые элементы

            let textContent = (element.innerText || element.value || "").toLowerCase().trim();
            if (!textContent) {
                const aria = element.getAttribute('aria-label');
                textContent = aria ? aria.toLowerCase().trim() : "";
            }

            for (const word of targetWords) {
                if (textContent.includes(word)) {
                    simulateClick(element);
                    break;
                }
            }
        }
    }

    window.addEventListener('load', clickTargetElements);
    setInterval(clickTargetElements, 2000);

})();
```
---

автоматическое нажатие Sign in

```javascript
// ==UserScript==
// @name         YouTube Auto Sign-In Clicker (Fixed)
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Автоматически нажимает кнопку "Sign in" на YouTube при появлении запроса "confirm you're not a bot"
// @author       Кожаный мешок
// @match        https://www.youtube.com/*
// @grant        none
// ==/UserScript==
(function() {
    'use strict';
    let clicked = false;
    function clickSignInButton() {
        if (clicked) return;
        // Более точный поиск кнопки "Sign in"
        const button = Array.from(document.querySelectorAll('ytd-button-renderer,button'))
            .map(el => el.querySelector('a,button') || el)
            .find(btn =>
                btn &&
                /sign in/i.test(btn.textContent) &&
                btn.offsetParent !== null // видимость
            );
        if (button) {
            console.log('[YouTube AutoLogin] Нажимаем кнопку "Sign in"...');
            clicked = true;
            button.click();
        } else {
            // Лог только при загрузке, чтобы не спамить при каждом интервале
            if (document.readyState === 'complete') {
                console.log('[YouTube AutoLogin] Кнопка "Sign in" не найдена.');
            }
        }
    }
    // Проверка каждую минуту
    setInterval(clickSignInButton, 60 * 1000);
    // Срабатывание сразу после загрузки
    window.addEventListener('load', () => {
        setTimeout(clickSignInButton, 3500);
    });
})();

```
