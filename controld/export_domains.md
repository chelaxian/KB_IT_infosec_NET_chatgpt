# Как использовать скрипт для извлечения доменов из конфигурационного файла JSON

Этот скрипт предназначен для извлечения доменных имен из конфигурационного файла в формате JSON, который был экспортирован из панели управления **Control D**. Скрипт рекурсивно обрабатывает структуру JSON, извлекает все домены, включая wildcard-домены, и сохраняет их в отдельный текстовый файл.

## Требования

Перед использованием убедитесь, что у вас установлены следующие компоненты:

- Python 3.x
- Библиотека `re` (обычно входит в стандартную библиотеку Python)

## Как использовать

1. Скачайте файл конфигурации в формате JSON из панели управления **Control D**.
2. Сохраните скрипт на своем компьютере в файл, например `extract_domains.py`.
3. Откройте терминал (или командную строку) и перейдите в директорию, где находится скрипт.
4. Запустите скрипт с указанием пути к JSON файлу, например:

```bash
python extract_domains.py /path/to/your/file.json
```

Если вы не укажете путь к файлу, скрипт запросит его вручную.

## Как работает скрипт

1. **Чтение JSON файла:**
   Скрипт загружает JSON файл, который должен содержать конфигурацию, экспортированную из панели управления **Control D**.

2. **Извлечение доменов:**
   Скрипт рекурсивно проходит по всему JSON-объекту. Для каждого строки проверяется, соответствует ли она формату домена, используя регулярное выражение, которое поддерживает wildcard-домены (например, `*.example.com`).

3. **Очистка и сохранение доменов:**
   Извлеченные домены сохраняются в отдельный текстовый файл, где каждый домен будет на новой строке.

## Код

```python
import json
import os
import sys
import re

def extract_domains(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        domains = []

        # Рекурсивный поиск доменов с использованием регулярных выражений
        def find_domains(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    find_domains(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_domains(item)
            elif isinstance(obj, str):
                # Регулярное выражение для поддержки wildcard-доменов
                if re.match(r'^\*?[a-zA-Z0-9.-]*\*?\.[a-zA-Z0-9.-]+$', obj):
                    domains.append(obj)

        find_domains(data)
        return sorted(set(domains))
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
        print(f"Ошибка при обработке файла: {e}")
        sys.exit(1)

def save_domains_to_file(domains, original_path):
    folder, original_filename = os.path.split(original_path)
    new_filename = os.path.splitext(original_filename)[0] + '_cleaned.txt'
    save_path = os.path.join(folder, new_filename)

    with open(save_path, 'w', encoding='utf-8') as f:
        for domain in domains:
            f.write(domain + '\n')

    return save_path

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Введите путь до JSON файла: ").strip()

    file_path = os.path.abspath(file_path)

    if not os.path.isfile(file_path):
        print("Указанный файл не найден. Проверьте путь и попробуйте снова.")
        sys.exit(1)

    domains = extract_domains(file_path)

    if not domains:
        print("Доменов не найдено в указанном файле.")
        sys.exit(0)

    print("\nСписок доменов:")
    print("\n".join(domains))

    save_path = save_domains_to_file(domains, file_path)

    print(f"\nДоменный список сохранён в файл: {save_path}")

if __name__ == "__main__":
    main()
```

## Пояснение к коду

1. **Функция `extract_domains(file_path)`**:
   - Загружает JSON файл с заданного пути.
   - Рекурсивно ищет строки, которые соответствуют доменам.
   - Добавляет найденные домены в список `domains` и возвращает уникальные домены, отсортированные по алфавиту.

2. **Функция `save_domains_to_file(domains, original_path)`**:
   - Сохраняет список доменов в текстовый файл, где каждый домен будет на новой строке.
   - Имя файла будет изменено на имя исходного файла с добавлением суффикса `_cleaned`.

3. **Основная функция `main()`**:
   - Обрабатывает аргументы командной строки и вызывает функции для извлечения и сохранения доменов.

## Пример использования

1. Запустите скрипт:

```bash
python extract_domains.py config.json
```

2. В консоли будет выведен список доменов, найденных в файле `config.json`:

```
Список доменов:
example.com
*.example.net
*.domain.org
```

3. Список доменов будет сохранен в файл с именем `config_cleaned.txt`.

## Ошибки и исключения

- Если файл не найден или поврежден, скрипт выведет ошибку и завершит выполнение.
- Если в файле не будут найдены домены, скрипт сообщит об этом и завершит выполнение.

## Заключение

Этот скрипт полезен для быстрого извлечения доменных имен из конфигураций, экспортированных из панели управления **Control D**. Это поможет вам упростить работу с доменами и подготовить их для дальнейшего использования или анализа.
