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

Если у вас возникнут сложности или потребуется дополнительная обработка ссылок (например, фильтрация по домену или атрибутам), уточните задачу.
