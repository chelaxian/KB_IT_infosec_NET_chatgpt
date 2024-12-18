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

---

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

