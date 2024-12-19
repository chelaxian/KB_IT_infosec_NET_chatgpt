<details><summary>Chrome Dev Tools</summary>
Чтобы сохранить все ссылки (теги `<a>` с атрибутом `href`) из вкладки **Elements** в Google Chrome DevTools, выполните следующие шаги:

1. **Откройте DevTools**:
   - Нажмите **F12** или щелкните правой кнопкой мыши на странице и выберите **Inspect** (Инспектировать).

2. **Перейдите на вкладку Console**:
   - В верхней части DevTools переключитесь на вкладку **Console**.

3. **Вставьте следующий код**:
   Скопируйте и вставьте приведенный ниже JavaScript-код в консоль:

   ```javascript
   // Получаем все элементы <a> на странице
   const links = Array.from(document.querySelectorAll('a'));

   // Извлекаем href атрибуты и фильтруем только уникальные ссылки
   const hrefs = [...new Set(links.map(a => a.href).filter(href => href))];

   // Выводим ссылки в консоль
   console.log(hrefs);

   // Сохраняем ссылки в виде файла
   const blob = new Blob([hrefs.join('\n')], { type: 'text/plain' });
   const a = document.createElement('a');
   a.href = URL.createObjectURL(blob);
   a.download = 'links.txt';
   document.body.appendChild(a);
   a.click();
   document.body.removeChild(a);
   console.log('Ссылки сохранены в файле links.txt');
   ```

4. **Запустите код**:
   - Нажмите **Enter**, чтобы выполнить код.
   - Ссылки автоматически сохранятся в файл `links.txt`, который будет загружен на ваш компьютер.

5. **Результат**:
   - Все уникальные ссылки с текущей страницы будут сохранены в текстовый файл.

---

Чтобы сохранить все изображения со страницы, извлечь их ссылки и сохранить их, можно использовать следующий подход:

### Шаги:

1. **Откройте DevTools**:
   - Нажмите **F12** или щелкните правой кнопкой мыши на странице и выберите **Inspect** (Инспектировать).

2. **Перейдите на вкладку Console**:
   - В верхней части DevTools переключитесь на вкладку **Console**.

3. **Используйте JavaScript для извлечения ссылок**:
   Вставьте следующий код в консоль:

   ```javascript
   // Получаем все элементы <img> на странице
   const images = Array.from(document.querySelectorAll('img'));

   // Извлекаем атрибуты src и фильтруем только уникальные ссылки
   const imageSrcs = [...new Set(images.map(img => img.src).filter(src => src))];

   // Выводим ссылки на изображения в консоль
   console.log(imageSrcs);

   // Сохраняем ссылки на изображения в файл
   const blob = new Blob([imageSrcs.join('\n')], { type: 'text/plain' });
   const a = document.createElement('a');
   a.href = URL.createObjectURL(blob);
   a.download = 'images_links.txt';
   document.body.appendChild(a);
   a.click();
   document.body.removeChild(a);
   console.log('Ссылки на изображения сохранены в файле images_links.txt');
   ```

4. **Запустите код**:
   - Нажмите **Enter**, чтобы выполнить код.
   - Ссылки на изображения будут сохранены в файл `images_links.txt`, который автоматически загрузится на ваш компьютер.

5. **Скачайте изображения**:
   - Используйте утилиту для массовой загрузки изображений, например, **wget** или **curl**. Для этого выполните следующую команду в терминале (Linux/MacOS) или командной строке (Windows):

     ```bash
     wget -i images_links.txt -P ./images
     ```

     - `-i images_links.txt` — файл со списком ссылок.
     - `-P ./images` — каталог, куда будут сохранены изображения.

   Для Windows убедитесь, что `wget` установлен (можно скачать из [GNU Wget](https://eternallybored.org/misc/wget/)).

---

### Если вы хотите сразу скачать все изображения без сохранения списка:

Используйте следующий код:

```javascript
// Получаем все изображения на странице
const images = Array.from(document.querySelectorAll('img'));

// Загружаем каждое изображение
images.forEach((img, index) => {
    const a = document.createElement('a');
    a.href = img.src;
    a.download = `image_${index + 1}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

console.log('Все изображения начали загружаться');
```

Этот скрипт создаст автоматическую загрузку всех изображений по очереди.
</details>
---

### Получить ссылки на посты с фото

```javascript
// Получаем все изображения на странице
const imageUrls = Array.from(document.querySelectorAll('img')).map(img => img.src);

// Функция для удаления хвостов из ссылок на изображения
const cleanImageUrls = imageUrls.map(url => {
    const [baseUrl] = url.split('?'); // Разделяем строку по знаку '?'
    return baseUrl;
});

// Выводим очищенные ссылки на изображения в консоль
console.log(cleanImageUrls);

// Опционально: сохраняем результат в текстовый файл
const blob = new Blob([cleanImageUrls.join('\n')], { type: 'text/plain' });
const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = 'clean_image_urls.txt';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
console.log('Ссылки на изображения без параметров сохранены в clean_image_urls.txt');

```

Теперь скрипт ищет только ссылки на изображения (теги `<img>`), удаляет из них всё, что находится после знака `?` (включая сам знак), и сохраняет очищенные ссылки в файл `clean_image_urls.txt`. Выполните скрипт в консоли DevTools, чтобы обработать все ссылки на изображения на текущей странице. 

---

### Получить ссылки на посты с видео

Вот JavaScript-код для Chrome, который находит все такие ссылки на странице, добавляет к ним полный домен и сохраняет их в файл:

```javascript
// Получаем все ссылки на посты
const postLinks = Array.from(document.querySelectorAll('a.MediaAlbumGalleryItem_wrapper_oDaL_'))
    .map(a => a.getAttribute('href')) // Получаем href из каждой ссылки
    .filter(href => href && href.includes('/posts/')) // Фильтруем только ссылки на посты

// Получаем текущий домен сайта
const domain = window.location.origin; // Это вернет что-то вроде https://example.com

// Формируем полный URL для каждой ссылки
const fullUrls = postLinks.map(href => domain + href);

// Выводим результат в консоль
console.log(fullUrls);

// Опционально: сохраняем результат в текстовый файл
const blob = new Blob([fullUrls.join('\n')], { type: 'text/plain' });
const a = document.createElement('a');
a.href = URL.createObjectURL(blob);
a.download = 'post_links.txt';
document.body.appendChild(a);
a.click();
document.body.removeChild(a);

console.log('Ссылки на посты сохранены в post_links.txt');
```

### Что делает скрипт:
1. **Находит все ссылки на посты**: Ищет все элементы `<a>`, которые имеют класс `MediaAlbumGalleryItem_wrapper_oDaL_`, и извлекает атрибут `href`.
2. **Фильтрует только те ссылки**, которые содержат `/posts/`, чтобы исключить остальные ссылки.
3. **Добавляет полный домен**: Использует `window.location.origin`, чтобы получить текущий домен (например, `https://example.com`) и формирует полный URL для каждой ссылки.
4. **Сохраняет результат** в текстовый файл `post_links.txt`, содержащий список всех ссылок на посты.

### Как использовать:
1. Откройте **DevTools** (F12) в Chrome.
2. Перейдите на вкладку **Console**.
3. Вставьте код и нажмите **Enter**.
4. Ссылки будут выведены в консоль и сохранены в файл `post_links.txt`.

---
### Cookie-Editor
https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
```
Export - Netscape - Save as "cookie.txt"
```

### yt-dlp
https://github.com/yt-dlp/yt-dlp
```
yt-dlp.exe --cookies cookie.txt -a post_links.txt
```
```
-a "C:\Users\test\Desktop\youtubeDL_list.txt"

-a, --batch-file FILE           File containing URLs to download ("-" for
                                stdin), one URL per line. Lines starting
                                with "#", ";" or "]" are considered as
                                comments and ignored
```
---
<details><summary>Free Download Manager (FDM)</summary>
Чтобы использовать **Free Download Manager (FDM)** для массовой загрузки изображений по списку ссылок из текстового файла, выполните следующие шаги:

---

### **1. Убедитесь, что FDM установлен**
Если программа еще не установлена, скачайте и установите её:
- Официальный сайт: [Free Download Manager](https://www.freedownloadmanager.org/)

---

### **2. Подготовьте текстовый файл**
- Убедитесь, что ваш файл `links.txt` содержит ссылки на изображения. Каждая ссылка должна быть на новой строке.

Пример:
```text
https://example.com/image1.jpg
https://example.com/image2.png
https://example.com/image3.gif
```

---

### **3. Импорт файла ссылок в FDM**
1. Откройте **Free Download Manager**.
2. Перейдите в меню: **Файл → Импортировать ссылки из файла**.
3. Выберите ваш файл `links.txt` и нажмите **Открыть**.

---

### **4. Настройте параметры загрузки**
- После импорта ссылок откроется окно настройки загрузки:
  - Укажите папку, куда будут сохраняться файлы.
  - Убедитесь, что все ссылки активны (отмечены галочкой).
  - Настройте параллельное количество загрузок (например, 3–5 одновременно).

---

### **5. Начните загрузку**
- Нажмите **ОК** или **Начать**, чтобы запустить процесс скачивания.
- FDM автоматически скачает все файлы из списка.

---

### **Дополнительно: Проверка и фильтрация**
- Если в файле есть нерабочие ссылки, FDM пропустит их и отметит как ошибочные.
- Вы можете настроить фильтры для типов файлов, чтобы загружать только изображения, например `.jpg`, `.png`.

---

Этот метод удобен для массовой загрузки и подходит для всех видов файлов, включая изображения. 
</details>
