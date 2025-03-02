
```python
import json
import re
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue, filters, MessageHandler
import logging

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
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            logger.info("Пользователь %s не является админом. Команда отклонена.", user_id)
            return
        return func(update, context, *args, **kwargs)
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
    # Если объект с LimitExceeded найден, возвращаем соответствующий статус
    for obj in objs:
        if obj.get("code") == "LimitExceeded":
            return "limit_exceeded"
    # Если объект с InvalidParameter найден, считаем это за неудачу
    for obj in objs:
        if obj.get("code") == "InvalidParameter":
            return "failure"
    # Если найден хотя бы один объект, отличный от стандартного, считаем это успехом
    for obj in objs:
        if obj != DEFAULT_OBJ:
            return "success"
    return "failure"

@restricted
async def log_msg(update: Update, context: CallbackContext) -> None:
    if not os.path.exists(FILE_PATH):
        await update.message.reply_text("Файл не найден.")
        return
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read()
    except Exception as e:
        await update.message.reply_text(f"Ошибка чтения файла: {e}")
        return

    max_chunk = 4000
    chunks = [content[i:i+max_chunk] for i in range(0, len(content), max_chunk)]
    for chunk in chunks:
        text = f"```json\n{chunk}\n```"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@restricted
async def log_file(update: Update, context: CallbackContext) -> None:
    if not os.path.exists(FILE_PATH):
        await update.message.reply_text("Файл не найден.")
        return
    await update.message.reply_document(document=open(FILE_PATH, "rb"))

@restricted
async def status(update: Update, context: CallbackContext) -> None:
    st = check_file_status()
    if st == "limit_exceeded":
        await update.message.reply_text("❌ LimitExceeded")
    elif st == "success":
        await update.message.reply_text("✅ Успех!")
    else:
        await update.message.reply_text("❌ неудача")

async def periodic_check(context: CallbackContext) -> None:
    global last_notified_status
    st = check_file_status()
    chat_id = ADMIN_ID
    if st == "success":
        if last_notified_status != "success":
            await context.bot.send_message(chat_id=chat_id, text="✅ Ура! ВМ готова!")
            last_notified_status = "success"
    else:
        last_notified_status = st

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команды (только для администратора)
    application.add_handler(CommandHandler("log_msg", log_msg))
    application.add_handler(CommandHandler("log_file", log_file))
    application.add_handler(CommandHandler("status", status))

    # Запускаем периодическую проверку файла каждые 5 минут
    application.job_queue.run_repeating(periodic_check, interval=300, first=0)

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
