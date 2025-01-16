https://habr.com/ru/articles/799751/

настройки ([раз](https://habr.com/ru/articles/727868/), [два](https://habr.com/ru/articles/731608/), [три](https://habr.com/ru/articles/735536/), [четыре](https://habr.com/ru/articles/728836/), [пять](https://habr.com/ru/articles/728696/), [шесть](https://habr.com/ru/articles/770400/), [семь](https://habr.com/ru/articles/776256/), [восемь](https://habr.com/ru/articles/777656/), [девять](https://habr.com/ru/articles/761798/), [десять](https://habr.com/ru/articles/778134/)

Это статья "четыре" из приведенного в начале списка.
Сохранил в веб архив
https://archive.ph/48HMR

Всё сохранено
https://web.archive.org/web/20230000000000*/https://habr.com/ru/users/MiraclePtr/publications/articles/
https://miracleptr.wordpress.com/2023/10/29/faq-по-shadowsocks-xray-xtls-reality-nekobox-etc-для-обхода-блокировок/

А это на всякий случай ссылка на архивную копию статьи на wayback machine, xпока доступная без VPN:
https://web.archive.org/web/20250108112019/https://habr.com/ru/articles/799751/

---

Лет 15 использую расширение браузера ScrapBook (сейчас другой разработчик и наименование другое - WebScrapBook). Сохраняет web-страницы: отдельные, с заданной глубиной вложенности, по маске... Все вырезки держу в отдельном каталоге, который автоматически синхронизируется с моими рабочими компами. Можно просматривать вырезки по сети на встроенном web-сервере (python), но только просматривать, а не дополнять - поэтому синхронизирую с компами.
![image](https://github.com/user-attachments/assets/6c776319-7d36-423d-afe1-7e0219128a95)
Сохраненные страницы можно редактировать - убирать лишние блоки, выделять текст маркерами, создавать заметки к частям текста...

---

Для тех, кому, также как мне, лень вручную очищать такие полезные статьи, чтобы сохранить в PDF - написал bookmarklet - он оставит только статью и комментарии, а также раскроет все спойлеры - останется только отправить на печать в PDF-принтер.
```javascript
javascript:(function(){( () => {document.querySelectorAll( "details" ).forEach( i => i.setAttribute( "open", "" ) ); const dels = [".tm-base-layout__header",".tm-header",".tm-page__sidebar",".tm-comment-form",".tm-block_spacing-bottom",".tm-comment-navigation",".tm-footer-menu",".tm-footer",".tm-article-sticky-panel",];let el;for ( const s of dels ) {const els = document.querySelectorAll( s );if ( els ) for ( el of els ) el.remove();}el = document.querySelector( ".tm-page__main" );el.style.maxWidth = "100%";} )()})()
```

---

https://webtopdf.com/ru/
Тут неплохо в пдф сконвертировалось
Вот только спойлеры не раскрываются

Расширение SinglePage раскрывает спойлеры при конвертации

---

PDF не лучшее решение для сохранения страниц, например сожрутся строки с горизонтальной прокруткой.
лучшее решение на мой взгляд - https://github.com/gildas-lormeau/SingleFile
заодно подтягивает все фреймы, lazy картинки. На выходе удобный HTML все-в-одном, при желании еще и сжатый.

да, это расширение сохраняет норм, в отличие от pdf.

только нижняя панель с ретингом статьи не убирается. чтобы ее убрать, нужно в содержимом файла заменить

```
.tm-article-sticky-panel{position:sticky;bottom
```
на
```
.tm-article-sticky-panel{bottom
```

---

https://habr.com/ru/articles/799751/comments

---

Сохранил в веб архив

https://archive.ph/48HMR

---

Рекомендую сделать копию статьи на [телеграф](https://telegra.ph/)

---

Кстати, если сделать копию страницы с каким-то предсказуемым названием (например "Обход блокировок"), то через nudecrawler можно будет попробовать найти, даже не имея закладок - просто по заглавию (адрес отражается в названии).

```
$ docker run --rm -v /tmp/run:/work yaroslaff/nudecrawler nudecrawler --total 0 -a "обход блокировок"
# No cache file /work/cache.json, start with empty cache
Loading nudenet classifier....
INTERESTING (ALL) https://telegra.ph/obhod-blokirovok-03-19 (0.0s)
  Total images: 0

INTERESTING (ALL) https://telegra.ph/obhod-blokirovok-03-18 (0.0s)
  Total images: 0

INTERESTING (ALL) https://telegra.ph/obhod-blokirovok-03-17 (0.0s)
  Total images: 0

INTERESTING (ALL) https://telegra.ph/obhod-blokirovok-03-17-2 (0.0s)
  Total images: 0

INTERESTING (ALL) https://telegra.ph/obhod-blokirovok-03-13 (0.47s)
  Total images: 1
```

Самостоятельный поиск - хорошая штука, когда обычный поиск недоступен или фильтруется.

---

Ещё вы можете выложить эту же самую статью (либо в markdown формате, либо в PDF) на github/gitlab либо вообще magnet-ссылкой на торрент.

P.S. Я вообще все свои статьи так дублирую, потому что они мне дороги и я не хочу зависеть от администрации хабра. Мой репозиторий для примера: https://github.com/Kright/my-articles

---

Вот тут беру,всё работает:https://bridges.torproject.org/

---

https://mega.nz/folder/c7sAARKb#k_erI9nbPP2Ziavndw17gg

Ссылка на мегу (с обновленным файлом)

---


