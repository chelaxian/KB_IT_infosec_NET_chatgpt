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
     - `WAIT` – время ожидания между переходами (3000 мс для 3 секунд).
   - Проверьте, что URL-адреса для логина (`LOGIN_URL`), logout (`LOGOUT_URL`) и главной страницы (`HOMEPAGE`) соответствуют вашим требованиям.
   
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
   - Ждет 3 секунды (`WAIT`).
   - Переходит на страницу логина Google (`LOGIN_URL`).
   - Устанавливает состояние цикла в "2".

3. **Шаг 2 (на странице логина):**
   - Ждет 3 секунды (`WAIT`).
   - Переходит на главную страницу YouTube (`HOMEPAGE`).
   - Сбрасывает состояние цикла до "0", после чего цикл повторяется.

Для хранения состояния используется `localStorage` под ключом `ytCycleStep`.

## Финальный скрипт

```javascript
// ==UserScript==
// @name         Циклический вход/выход для YouTube (без проверок, по схеме)
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  По схеме: ждем INTERVAL, переходим на logout, ждем 3 сек, переходим на логин, ждем 3 сек, переходим на главную. Цикл повторяется.
// @match        https://www.youtube.com/*
// @match        https://accounts.google.com/v3/signin/identifier*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // НАСТРАИВАЕМЫЕ ПАРАМЕТРЫ
    const INTERVAL = 300000; // 5 минут в миллисекундах (300000 мс)
    const WAIT = 3000;       // 3 секунды в миллисекундах

    const LOGOUT_URL = "https://www.youtube.com/logout";
    const LOGIN_URL = "https://accounts.google.com/v3/signin/identifier?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F%253FthemeRefresh%253D1&hl=en&ifkv=ASSHykrZmMTbrRwtTdPcCL808H2MXtIBXe4kDNr1IF_omyo6oiVwXg7ubi9zbShFz6v8Ul_ILTxIvQ&passive=true&service=youtube&uilel=3&flowName=GlifWebSignIn&flowEntry=ServiceLogin";
    const HOMEPAGE = "https://www.youtube.com/";

    // Считываем состояние цикла: "0", "1" или "2". Если не задано – по умолчанию "0"
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
    // Если состояние "2": ждём WAIT и переходим на главную страницу, сбрасывая состояние до "0"
    else if (step === "2") {
        console.log(`Шаг 2: через ${WAIT/1000} секунд выполняем переход на главную страницу.`);
        setTimeout(() => {
            localStorage.setItem("ytCycleStep", "0");
            console.log("Переход на главную страницу YouTube.");
            window.location.href = HOMEPAGE;
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
