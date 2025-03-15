Ниже приведён пример скрипта для Violentmonkey, который каждые 5 секунд эмулирует нажатие клавиши Enter на странице.

```js
// ==UserScript==
// @name         Auto Press Enter Every 5 Seconds
// @namespace    http://example.com/
// @version      1.0
// @description  Эмулирует нажатие клавиши Enter каждые 5 секунд.
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Function to simulate Enter key press
    function pressEnter() {
        // Create keydown event for Enter key
        const keyDownEvent = new KeyboardEvent('keydown', {
            bubbles: true,
            cancelable: true,
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,    // deprecated but still used in some cases
            which: 13
        });
        
        // Create keyup event for Enter key
        const keyUpEvent = new KeyboardEvent('keyup', {
            bubbles: true,
            cancelable: true,
            key: 'Enter',
            code: 'Enter',
            keyCode: 13,
            which: 13
        });
        
        // Dispatch events on the currently focused element, 
        // or fallback to document.body if нет фокуса
        const target = document.activeElement || document.body;
        target.dispatchEvent(keyDownEvent);
        target.dispatchEvent(keyUpEvent);
        
        console.log('AutoPressEnter: Enter key pressed.');
    }

    // Set interval to press Enter every 5 seconds (5000 мс)
    setInterval(pressEnter, 5000);
})();
```

### Объяснение:
1. **Метаданные UserScript**  
   - `@match *://*/*` – скрипт будет запускаться на всех сайтах. При необходимости можно сузить диапазон доменов.  
   - `@grant none` – скрипт не использует никаких специальных API.

2. **Функция pressEnter()**  
   - Создаёт два события: `keydown` и `keyup` для клавиши Enter (код 13).
   - События диспатчатся на элементе, который в данный момент находится в фокусе. Если фокуса нет, используется `document.body`.

3. **setInterval**  
   - Каждые 5000 мс (5 секунд) функция `pressEnter()` выполняется, что приводит к эмуляции нажатия Enter.

Сохраните скрипт в Violentmonkey, и он будет автоматически имитировать нажатие Enter на странице каждые 5 секунд.
