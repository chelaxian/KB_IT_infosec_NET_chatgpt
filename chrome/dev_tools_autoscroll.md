video

```javascript
(async function () {
    // Принудительный скролл до конца страницы для загрузки всех постов
    async function autoScrollToBottom() {
        return new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 300;
            const timer = setInterval(() => {
                const scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if (totalHeight >= scrollHeight - window.innerHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 200);
        });
    }

    console.log('[*] Прокрутка страницы для подгрузки постов...');
    await autoScrollToBottom();
    console.log('[+] Прокрутка завершена. Поиск ссылок...');

    // Получаем все элементы со ссылками на посты
    const postLinks = Array.from(document.querySelectorAll('a[href*="/posts/"]'))
        .map(a => a.getAttribute('href'))
        .filter(href => href && href.includes('/posts/') && href.includes('/media/'));

    const domain = window.location.origin;
    const fullUrls = [...new Set(postLinks.map(href => domain + href))]; // удаление дубликатов

    if (fullUrls.length === 0) {
        console.warn('[!] Не найдено ни одной ссылки формата /posts/.../media/...');
        return;
    }

    // Сохраняем в файл
    const blob = new Blob([fullUrls.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'boosty_media_links.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    console.log(`[✓] Найдено ${fullUrls.length} ссылок. Сохранено в boosty_media_links.txt`);
})();

```

photo

```javascript
(async function () {
    // Прокручиваем страницу, чтобы загрузить все изображения
    async function autoScrollToBottom() {
        return new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 300;
            const timer = setInterval(() => {
                const scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if (totalHeight >= scrollHeight - window.innerHeight) {
                    clearInterval(timer);
                    resolve();
                }
            }, 200);
        });
    }

    console.log('[*] Прокрутка страницы для загрузки всех изображений...');
    await autoScrollToBottom();
    console.log('[+] Прокрутка завершена. Сбор ссылок на изображения...');

    // Получаем все <img> элементы и извлекаем src
    const rawImageUrls = Array.from(document.querySelectorAll('img')).map(img => img.src);

    // Очищаем от параметров (например, ?width=...)
    const cleanImageUrls = rawImageUrls
        .filter(Boolean)
        .map(url => url.split('?')[0])
        .filter((url, idx, self) => self.indexOf(url) === idx); // Удаляем дубликаты

    if (cleanImageUrls.length === 0) {
        console.warn('[!] Не найдено изображений.');
        return;
    }

    // Сохраняем в текстовый файл
    const blob = new Blob([cleanImageUrls.join('\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'boosty_image_urls.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    console.log(`[✓] Найдено ${cleanImageUrls.length} изображений. Сохранено в boosty_image_urls.txt`);
})();

```
