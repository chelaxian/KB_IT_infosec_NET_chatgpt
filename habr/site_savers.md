https://habr.com/ru/articles/799751/

настройки ([раз](https://habr.com/ru/articles/727868/), [два](https://habr.com/ru/articles/731608/), [три](https://habr.com/ru/articles/735536/), [четыре](https://habr.com/ru/articles/728836/), [пять](https://habr.com/ru/articles/728696/), [шесть](https://habr.com/ru/articles/770400/), [семь](https://habr.com/ru/articles/776256/), [восемь](https://habr.com/ru/articles/777656/), [девять](https://habr.com/ru/articles/761798/), [десять](https://habr.com/ru/articles/778134/)

Это статья "четыре" из приведенного в начале списка.
Ее бывший адрес https://habr.com/ru/articles/728836/
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

