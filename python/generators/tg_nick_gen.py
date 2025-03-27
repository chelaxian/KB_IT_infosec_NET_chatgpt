import re
import itertools
from math import comb
import time
import random

# === CONFIGURATION ===
ONE_PASS_ONE_TIME_GEN = True  # если True = то выводим всего 1 строку и спрашиваем повторить

nick_length = 32              # длина ника: от 5 до 32
char1 = "I"                   # первый символ
char2 = "l"                   # второй символ
max_results = 0               # максимум кол-ва результатов (0 = без ограничения)
max_file_size = "20GB"        # максимальный размер файла

# Ограничения по количеству символов (или 0 или None)
min_char1_count = 1
max_char1_count = None
min_char2_count = 1
max_char2_count = None

# Ограничения по процентам символов (или None)
max_char1_percent = 0.5       # например: 0.3 = не больше 30%
max_char2_percent = 0.5       # например: None

output_file = "nicknames.txt"
# =======================

def parse_file_size(size_str):
    size_str = size_str.strip().upper()
    match = re.match(r"^(\d+(?:\.\d+)?)([KMG]?B)$", size_str)
    if not match:
        raise ValueError("Некорректный формат размера файла. Пример: 100KB, 10MB, 1GB")
    num, unit = match.groups()
    num = float(num)
    multiplier = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
    }[unit]
    return int(num * multiplier)

def compute_max_results_by_size(max_size_bytes, line_length):
    return max_size_bytes // line_length

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

if not (5 <= nick_length <= 32):
    raise ValueError("Длина ника должна быть от 5 до 32 символов.")

line_length = nick_length + 1
max_size_bytes = parse_file_size(max_file_size)
max_by_size = compute_max_results_by_size(max_size_bytes, line_length)

c1_min = min_char1_count or 0
c1_max = nick_length if max_char1_count is None else min(max_char1_count, nick_length)
if max_char1_percent is not None:
    c1_max = min(c1_max, int(nick_length * max_char1_percent))
if max_char2_percent is not None:
    c1_min = max(c1_min, nick_length - int(nick_length * max_char2_percent))

valid_counts = []
for count_char1 in range(c1_min, c1_max + 1):
    count_char2 = nick_length - count_char1
    if count_char2 < (min_char2_count or 0):
        continue
    if max_char2_count is not None and count_char2 > max_char2_count:
        continue
    valid_counts.append(count_char1)

total_combinations = sum(comb(nick_length, c1) for c1 in valid_counts)
final_limit = min(
    total_combinations,
    max_results if max_results else total_combinations,
    max_by_size
)
estimated_file_size = final_limit * line_length
estimated_time_sec = final_limit / 50000

min_c2 = nick_length - c1_max
max_c2 = nick_length - c1_min
if min_char2_count is not None:
    min_c2 = max(min_c2, min_char2_count)
if max_char2_count is not None:
    max_c2 = min(max_c2, max_char2_count)

print("\n⚙️ Параметры генерации:")
print(f"• Длина ника: {nick_length}")
print(f"• Символы: char1 = '{char1}', char2 = '{char2}'")
print(f"• Допустимое кол-во '{char1}': от {c1_min} до {c1_max}")
print(f"• Допустимое кол-во '{char2}': от {min_c2} до {max_c2}")
print(f"• Теоретически допустимых строк: {total_combinations}")
print(f"• Будет сгенерировано: {final_limit}")
print(f"• Примерный размер файла: {format_bytes(estimated_file_size)}")
print(f"• Примерное время генерации: {estimated_time_sec:.1f} сек")

if not ONE_PASS_ONE_TIME_GEN:
    def is_yes(s):
        return s.strip().lower() in ("", "y", "yes", "д", "да")

    proceed = input("\n🔄 Продолжить генерацию? (Y/Д/Yes/Да/N/Н/No/Нет, по умолчанию — Да): ").strip().lower()
    if not is_yes(proceed):
        print("⛔ Генерация отменена.")
        exit()

    written = 0
    start_time = time.time()

    with open(output_file, "w", encoding="utf-8") as f:
        for count_char1 in valid_counts:
            for positions in itertools.combinations(range(nick_length), count_char1):
                nickname = [char2] * nick_length
                for pos in positions:
                    nickname[pos] = char1
                f.write("".join(nickname) + "\n")
                written += 1
                if written >= final_limit:
                    break
            if written >= final_limit:
                break

    duration = time.time() - start_time
    print(f"✅ Генерация завершена. Сохранено {written} строк в файл: {output_file}")
    print(f"⏱️ Время генерации: {duration:.2f} сек")

else:
    from random import choice, sample

    def generate_one():
        count_char1 = choice(valid_counts)
        positions = sample(range(nick_length), count_char1)
        nickname = [char2] * nick_length
        for pos in positions:
            nickname[pos] = char1
        return "".join(nickname)

    def is_yes(s):
        return s.strip().lower() in ("", "y", "yes", "д", "да")

    while True:
        print("\n🎲 Случайный ник: " + generate_one())
        again = input("🔁 Повторить генерацию только 1 строки? (Y/Д/Yes/Да/N/Н/No/Нет, по умолчанию — Да): ")
        if not is_yes(again):
            print("👋 Выход.")
            break
