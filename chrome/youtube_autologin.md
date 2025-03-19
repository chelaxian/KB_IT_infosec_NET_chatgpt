# Циклический вход/выход для YouTube

Данный проект позволяет автоматически разлогиниваться и залогиниваться на YouTube по заданному циклу. Скрипт реализован для расширений [Violentmonkey](https://violentmonkey.github.io/) (аналог Tampermonkey) для браузера Chrome. Для автозаполнения данных на странице логина рекомендуется использовать LastPass или аналогичный менеджер паролей.

## Необходимые расширения

1. **Violentmonkey**  
   - [Ссылка на Chrome Web Store](https://chrome.google.com/webstore/detail/violentmonkey/jinjaccalgkegednnccohejagnlnfdag)  
   - Используется для управления пользовательскими скриптами.

2. **LastPass**  
   - [Ссылка на Chrome Web Store](https://chrome.google.com/webstore/detail/lastpass-free-password-ma/hdokiejnpimakedhajhdlcegeplioahd)  
   - Используется для автоматического автозаполнения логина и пароля на странице входа Google.

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
    const INTERVAL = 600000; // 10 минут в миллисекундах
    const WAIT = 5000;       // 5 секунд в миллисекундах

    const LOGOUT_URL = "https://www.youtube.com/logout";
    const LOGIN_URL = "https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F%253FthemeRefresh%253D1&hl=en&ifkv=ASSHykrZmMTbrRwtTdPcCL808H2MXtIBXe4kDNr1IF_omyo6oiVwXg7ubi9zbShFz6v8Ul_ILTxIvQ&passive=true&service=youtube&uilel=3&flowName=GlifWebSignIn&flowEntry=ServiceLogin";
    const HOMEPAGE = "https://www.youtube.com/";
    const NEXTPAGE = "https://www.youtube.com/watch?v=4xDzrJKXOOY";
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
// @name         Auto Press Enter and Tab Alternately
// @namespace    http://example.com/
// @version      1.2
// @description  Эмулирует нажатие клавиш Enter и Tab, чередуя их, начиная с Enter.
// @match        *://*/*
// @exclude      https://www.youtube.com/watch?v=*
// @exclude      https://www.youtube.com/live/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Функция для симуляции нажатия указанной клавиши
    function simulateKey(key, code, keyCode) {
        // Создание события keydown
        const keyDownEvent = new KeyboardEvent('keydown', {
            bubbles: true,
            cancelable: true,
            key: key,
            code: code,
            keyCode: keyCode, // deprecated, но может понадобиться для некоторых случаев
            which: keyCode
        });

        // Создание события keyup
        const keyUpEvent = new KeyboardEvent('keyup', {
            bubbles: true,
            cancelable: true,
            key: key,
            code: code,
            keyCode: keyCode,
            which: keyCode
        });

        // Диспатчим события на активном элементе или document.body, если фокуса нет
        const target = document.activeElement || document.body;
        target.dispatchEvent(keyDownEvent);
        target.dispatchEvent(keyUpEvent);

        console.log(`AutoKeyPress: ${key} key pressed.`);
    }

    // Флаг, определяющий, какую клавишу нажимать следующей
    let pressEnterNext = true;

    // Функция, которая чередует нажатия клавиш
    function alternateKeyPress() {
        if (pressEnterNext) {
            simulateKey('Enter', 'Enter', 13);
        } else {
            simulateKey('Tab', 'Tab', 9);
        }
        pressEnterNext = !pressEnterNext;
    }

    // Устанавливаем интервал в 5000 мс для чередования нажатий
    setInterval(alternateKeyPress, 5000);
})();


```

---

автоматическое нажатие заданных кнопок на странице

```javascript
// ==UserScript==
// @name         AutoClick Next/SignIn Enhanced
// @namespace    http://example.com/
// @version      1.5
// @description  Автоматически нажимает на указанный аккаунт Google и на кнопки с текстами "Next", "Sign in", "Log in", "Login", "Continue", "Reload", "Agree", "Accept".
// @match        *://*/*
// @exclude      https://www.youtube.com/watch?v=*
// @exclude      https://www.youtube.com/live/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Email/аккаунт, на который надо нажимать:
    const userEmail = "300.tpaktop.300@gmail.com";

    // Список слов, при обнаружении которых на кнопках/ссылках делаем клик:
    const targetWords = [
        "next",         // English: "Next"
        "sign in",      // English: "Sign in"
        "log in",       // English: "Log in"
        "login",        // English: "Login"
        "continue",     // English: "Continue"
        "reload",       // English: "Reload"
        "agree",        // English: "Agree"
        "accept"        // English: "Accept"
    ];

    // Функция для имитации клика по элементу
    function simulateClick(element) {
        element.click();
        console.log(`AutoClick: Clicked on element with text "${element.innerText || element.value || element.getAttribute('aria-label') || ''}"`);
    }

    // Основная функция: сначала кликаем по аккаунту (если есть), потом по кнопкам
    function clickTargetElements() {
        // 1) Пытаемся найти и кликнуть нужный аккаунт по data-identifier
        const googleAccLink = document.querySelector(`[role="link"][data-identifier="${userEmail}"]`);
        if (googleAccLink) {
            googleAccLink.click();
            console.log(`AutoClick: Clicked on Google account link with data-identifier="${userEmail}"`);
        }

        // 2) Ищем кнопки/ссылки с целевыми словами
        const clickableElements = document.querySelectorAll(
            'button, input[type="button"], input[type="submit"], a, [role="button"]'
        );
        for (const element of clickableElements) {
            // Пропускаем, если элемент отключен
            if (element.disabled) continue;

            // Получаем текст из innerText, value или aria-label
            let textContent = (element.innerText || element.value || "").toLowerCase().trim();
            if (!textContent) {
                const aria = element.getAttribute('aria-label');
                textContent = aria ? aria.toLowerCase().trim() : "";
            }

            // Проверяем, содержит ли текст одно из целевых слов
            for (const word of targetWords) {
                if (textContent.includes(word)) {
                    simulateClick(element);
                    break; // переходим к следующему элементу
                }
            }
        }
    }

    // Запуск при загрузке страницы
    window.addEventListener('load', clickTargetElements);

    // Периодический запуск (каждые 2 сек) для динамически подгружаемых элементов
    setInterval(clickTargetElements, 2000);
})();
```
