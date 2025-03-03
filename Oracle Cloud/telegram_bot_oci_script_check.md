
```python
import json
import re
import os
import logging
from datetime import time as dtime

from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Задайте здесь ваш токен и ID администратора (только этот пользователь может отдавать команды)
TOKEN = "1111111111:AAAAAAAAAAAAAAAAAAAAAAA"
ADMIN_ID = 1111111  # замените на реальный Telegram ID администратора

# Путь к файлу с логом
FILE_PATH = "/home/ubuntu/oci-arm-host-capacity/oci.log"

# Глобальная переменная для хранения последнего отправленного статуса (чтобы не спамить)
last_notified_status = None

# Стандартное сообщение, которое считается "не готовностью"
DEFAULT_OBJ = {"code": "InternalError", "message": "Out of host capacity."}


def restricted(func):
    """Декоратор для ограничения команд только администратору."""
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            logger.info("Пользователь %s не является админом. Команда отклонена.", user_id)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped


def extract_json_objects(file_content: str):
    """
    Извлекает все JSON-объекты из текста.
    Предполагается, что объекты начинаются символом '{' и заканчиваются '}'.
    """
    pattern = re.compile(r'\{.*?\}', re.DOTALL)
    objs = []
    for match in pattern.finditer(file_content):
        obj_str = match.group()
        try:
            obj = json.loads(obj_str)
            objs.append(obj)
        except Exception as e:
            logger.error("Ошибка при парсинге JSON: %s", e)
    return objs


def check_file_status() -> str:
    """
    Анализирует файл и возвращает статус:
    - "limit_exceeded" – если встречается объект с кодом LimitExceeded
    - "failure" – если встречается объект с кодом InvalidParameter или все объекты стандартные
    - "success" – если хотя бы один объект не равен DEFAULT_OBJ и не является LimitExceeded/InvalidParameter
    """
    if not os.path.exists(FILE_PATH):
        logger.error("Файл %s не найден", FILE_PATH)
        return "failure"
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except Exception as e:
        logger.error("Ошибка чтения файла: %s", e)
        return "failure"

    objs = extract_json_objects(content)
    for obj in objs:
        if obj.get("code") == "LimitExceeded":
            return "limit_exceeded"
    for obj in objs:
        if obj.get("code") == "InvalidParameter":
            return "failure"
    for obj in objs:
        if obj != DEFAULT_OBJ:
            return "success"
    return "failure"


def count_json_objects() -> int:
    """Подсчитывает количество JSON-объектов в файле."""
    if not os.path.exists(FILE_PATH):
        return 0
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except Exception as e:
        return 0
    objs = extract_json_objects(content)
    return len(objs)


def count_too_many_requests() -> int:
    """Подсчитывает количество JSON-объектов с ошибкой TooManyRequests."""
    if not os.path.exists(FILE_PATH):
        return 0
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except Exception as e:
        return 0
    objs = extract_json_objects(content)
    count = 0
    for obj in objs:
        if obj.get("code") == "TooManyRequests" or ("Too many requests" in obj.get("message", "")):
            count += 1
    return count


@restricted
async def log_msg(update: Update, context: CallbackContext) -> None:
    """
    Отправляет содержимое лога, разделённое на сообщения так,
    чтобы каждое сообщение содержало целые JSON-блоки и не превышало лимит.
    """
    if not os.path.exists(FILE_PATH):
        await update.message.reply_text("Файл не найден.")
        return
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except Exception as e:
        await update.message.reply_text(f"Ошибка чтения файла: {e}")
        return

    objs = extract_json_objects(content)
    if not objs:
        await update.message.reply_text("JSON объекты не найдены в файле.")
        return

    chunks = []
    current_chunk = ""
    # Учтём, что маркеры кода занимают символы: "```json\n" и "\n```"
    max_length = 4096 - len("```json\n" + "\n```")  # = 4084
    for obj in objs:
        block = json.dumps(obj, indent=4, ensure_ascii=False)
        new_chunk = block if not current_chunk else current_chunk + "\n" + block
        if len(new_chunk) <= max_length:
            current_chunk = new_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = block
    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        text = f"```json\n{chunk}\n```"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


@restricted
async def log_file(update: Update, context: CallbackContext) -> None:
    """Отправляет файл лога как документ."""
    if not os.path.exists(FILE_PATH):
        await update.message.reply_text("Файл не найден.")
        return
    await update.message.reply_document(document=open(FILE_PATH, "rb"))


@restricted
async def status(update: Update, context: CallbackContext) -> None:
    """
    Анализирует лог-файл, возвращает статус, а также:
    - количество JSON-блоков
    - общее время работы: 
         общее время = (количество блоков * 1 минута) + (количество блоков с Too many requests * 5 минут)
      Результат форматируется в днях, часах и минутах.
    """
    st = check_file_status()
    total_blocks = count_json_objects()
    too_many = count_too_many_requests()
    total_minutes = total_blocks + (too_many * 5)
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60
    time_str = f"{days} дней, {hours} часов, {minutes} минут"

    if st == "limit_exceeded":
        status_msg = "❌ LimitExceeded"
    elif st == "success":
        status_msg = "✅ Успех!"
    else:
        status_msg = "❌ Неудача"

    reply = (
        f"Статус: {status_msg}\n"
        f"Количество JSON блоков: {total_blocks}\n"
        f"Общее время работы: {time_str}"
    )
    await update.message.reply_text(reply)


async def start(update: Update, context: CallbackContext) -> None:
    """Выводит меню доступных команд."""
    text = (
        "Добро пожаловать!\n"
        "Доступные команды:\n"
        "/log_msg - бот отправляет лог в виде сообщения\n"
        "/log_file - бот отправляет файл как документ\n"
        "/status - бот анализирует файл и отправляет статус"
    )
    await update.message.reply_text(text)


async def daily_status(context: CallbackContext) -> None:
    """
    Ежедневно в 10:00 отправляет пользователю статус с эмодзи,
    количеством JSON-блоков и общим временем работы.
    """
    st = check_file_status()
    total_blocks = count_json_objects()
    too_many = count_too_many_requests()
    total_minutes = total_blocks + (too_many * 5)
    days = total_minutes // (24 * 60)
    hours = (total_minutes % (24 * 60)) // 60
    minutes = total_minutes % 60
    time_str = f"{days} дней, {hours} часов, {minutes} минут"

    if st == "limit_exceeded":
        status_msg = "❌ LimitExceeded"
    elif st == "success":
        status_msg = "✅ Успех!"
    else:
        status_msg = "❌ Неудача"

    message = (
        f"Дневной статус:\n"
        f"{status_msg}\n"
        f"Количество JSON блоков: {total_blocks}\n"
        f"Общее время работы: {time_str}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=message)


async def periodic_check(context: CallbackContext) -> None:
    """
    Периодическая проверка каждые 1 минуту.
    Если статус изменился на 'success', бот уведомляет администратора.
    """
    global last_notified_status
    st = check_file_status()
    if st == "success" and last_notified_status != "success":
        await context.bot.send_message(chat_id=ADMIN_ID, text="✅ Ура! ВМ готова!")
        last_notified_status = "success"
    else:
        last_notified_status = st


async def set_commands(context: CallbackContext) -> None:
    """Устанавливает меню команд для бота."""
    commands = [
        BotCommand("start", "Показать меню команд"),
        BotCommand("log_msg", "бот отправляет лог в виде сообщения"),
        BotCommand("log_file", "бот отправляет файл как документ"),
        BotCommand("status", "бот анализирует файл и отправляет статус")
    ]
    await context.bot.set_my_commands(commands)


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("log_msg", log_msg))
    application.add_handler(CommandHandler("log_file", log_file))
    application.add_handler(CommandHandler("status", status))

    # Устанавливаем меню команд при запуске (run_once вызовет функцию сразу после старта)
    application.job_queue.run_once(set_commands, when=0)

    # Запускаем периодическую проверку файла каждые 1 минуту
    application.job_queue.run_repeating(periodic_check, interval=60, first=0)

    # Ежедневная проверка в 10:00 утра
    application.job_queue.run_daily(daily_status, time=dtime(hour=10, minute=0, second=0))

    application.run_polling()


if __name__ == '__main__':
    main()

```

---
Ниже приведён пример unit-файла для systemd, который будет автоматически запускать вашего бота:

```ini
[Unit]
Description=OCI Telegram Bot Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/BOT/Telegram/OCI_BOT
ExecStart=/home/ubuntu/BOT/Telegram/OCI_BOT/venv/bin/python3 /home/ubuntu/BOT/Telegram/OCI_BOT/oci_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Инструкция по установке:

1. **Создайте файл сервиса:**

   ```bash
   sudo nano /etc/systemd/system/oci_bot.service
   ```

   Вставьте в него приведённое содержимое и сохраните файл.

2. **Перезагрузите демона systemd:**

   ```bash
   sudo systemctl daemon-reload
   ```

3. **Включите автозапуск сервиса:**

   ```bash
   sudo systemctl enable oci_bot.service
   ```

4. **Запустите сервис:**

   ```bash
   sudo systemctl start oci_bot.service
   ```

5. **Проверьте статус сервиса:**

   ```bash
   sudo systemctl status oci_bot.service
   ```

Эти шаги обеспечат автозапуск вашего Telegram-бота при старте системы.
