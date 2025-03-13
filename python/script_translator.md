Для корректной работы скрипта необходимо установить все зависимости. Используйте следующие команды:

### Установка зависимостей:
```bash
pip install googletrans==4.0.0-rc1 deep-translator
```

### Дополнительно, если нужно:
```bash
pip install argparse
pip install tokenize
```

Если у вас возникают проблемы с googletrans, попробуйте альтернативную команду:
```bash
pip install googletrans==4.0.0-rc1 --no-cache-dir
```

### Объяснение зависимостей:
- `googletrans==4.0.0-rc1` — основной переводчик.
- `deep-translator` — fallback переводчик, если googletrans не сработает.
- `argparse` (обычно встроен) — обработка аргументов командной строки.
- `tokenize` (встроен в Python) — обработка токенов кода.

Теперь скрипт должен работать без проблем! 🚀

---

```python
#!/usr/bin/env python3
import sys
import ast
import tokenize
import io
import re
import argparse
from googletrans import Translator
from json.decoder import JSONDecodeError

# Попытка импортировать fallback-переводчик из deep_translator
try:
    from deep_translator import GoogleTranslator as DeepGoogleTranslator
except ImportError:
    DeepGoogleTranslator = None

# Mapping of common language names to language codes
LANG_MAP = {
    'english': 'en',
    'russian': 'ru',
    'chinese': 'zh-cn',
}

# Dictionary of common symbols and their required import statements
COMMON_IMPORTS = {
    'logging': 'import logging',
    'Translator': 'from googletrans import Translator',
    'ast': 'import ast',
    'tokenize': 'import tokenize',
    'io': 'import io',
    'argparse': 'import argparse'
}

# List of function/method names considered as output functions
OUTPUT_METHODS = {
    "print",
    "send_message",
    "reply_text",
    "answer",
    "edit_message_text",
    "reply",
    "send"
}

def is_output_function(call_node):
    if isinstance(call_node.func, ast.Name) and call_node.func.id in OUTPUT_METHODS:
        return True
    if isinstance(call_node.func, ast.Attribute) and call_node.func.attr in OUTPUT_METHODS:
        return True
    return False

def get_output_string_positions(source):
    positions = set()
    try:
        tree = ast.parse(source)
    except Exception as e:
        print("Error parsing the source file:", e)
        return positions

    class OutputStringVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if is_output_function(node):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        positions.add((arg.lineno, arg.col_offset))
                    elif isinstance(arg, ast.Str):
                        positions.add((arg.lineno, arg.col_offset))
            self.generic_visit(node)

    OutputStringVisitor().visit(tree)
    return positions

def is_f_string(token_string):
    m = re.match(r'(?i)^([urbf]+)', token_string)
    if m:
        prefix = m.group(1)
        return 'f' in prefix.lower()
    return False

def safe_detect(text, translator, target_lang):
    try:
        return translator.detect(text)
    except (AttributeError, JSONDecodeError, ValueError):
        return type('DummyDetection', (), {'lang': target_lang})()

def force_translate_text(text, target_lang, translator, retries=2):
    """
    Если целевой язык английский и deep_translator установлен, используем его,
    чтобы гарантированно перевести текст с русского на английский.
    """
    if target_lang == 'en' and DeepGoogleTranslator is not None:
        try:
            return DeepGoogleTranslator(source='ru', target='en').translate(text)
        except Exception as fe:
            print("Fallback translation error:", fe)
            return text
    else:
        # Для остальных языков используем googletrans
        try:
            result = translator.translate(text, dest=target_lang)
            return result.text
        except Exception as e:
            print("Googletrans exception:", e)
            return text

def translate_text(text, target_lang, translator, force=False):
    if not text.strip():
        return text
    if force:
        return force_translate_text(text, target_lang, translator)
    else:
        detected = safe_detect(text, translator, target_lang)
        if detected.lang == target_lang:
            return text
        try:
            return translator.translate(text, dest=target_lang).text
        except Exception as e:
            print("Translation error:", e)
            return text

def translate_f_string_literal(token_string, target_lang, translator):
    prefix_match = re.match(r'(?i)^([urbf]+)', token_string)
    prefix = prefix_match.group(1) if prefix_match else ''
    rest = token_string[len(prefix):]
    if rest.startswith('"""') or rest.startswith("'''"):
        quotes = rest[:3]
        end_quotes = quotes
        content = rest[3:-3]
    else:
        quotes = rest[0]
        end_quotes = quotes
        content = rest[1:-1]
    parts = re.split(r'(\{[^{}]*\})', content)
    new_parts = []
    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            new_parts.append(part)
        else:
            new_parts.append(translate_text(part, target_lang, translator))
    new_content = "".join(new_parts)
    return prefix + quotes + new_content + end_quotes

def translate_string_literal(token_string, target_lang, translator):
    if is_f_string(token_string):
        return translate_f_string_literal(token_string, target_lang, translator)
    prefix_re = re.compile(r'^([rRuU]{0,2})')
    m = prefix_re.match(token_string)
    prefix = m.group(0) if m else ''
    rest = token_string[len(prefix):]
    if rest.startswith('"""') or rest.startswith("'''"):
        quotes = rest[:3]
        content = rest[3:-3]
        new_content = translate_text(content, target_lang, translator)
        return prefix + quotes + new_content + quotes
    else:
        quotes = rest[0]
        content = rest[1:-1]
        new_content = translate_text(content, target_lang, translator)
        return prefix + quotes + new_content + quotes

def translate_source(source, target_lang):
    output_positions = get_output_string_positions(source)
    translator = Translator(service_urls=['translate.googleapis.com'])
    translator.raise_Exception = False
    result_tokens = []
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    for token in tokens:
        token_type = token.type
        token_string = token.string
        start_line, start_col = token.start
        if token_type == tokenize.COMMENT:
            comment_text = token_string[1:].lstrip()
            # Если комментарий состоит только из '#' и пробелов (3+ символов), оставляем его без перевода
            if re.fullmatch(r'[#\s]{3,}', comment_text):
                new_token_string = token_string
            elif comment_text.strip():
                new_comment = translate_text(comment_text, target_lang, translator, force=True)
                new_token_string = '#' + ' ' + new_comment
            else:
                new_token_string = token_string
            token = tokenize.TokenInfo(token_type, new_token_string, token.start, token.end, token.line)
        elif token_type == tokenize.STRING:
            if (start_line, start_col) in output_positions or is_f_string(token_string):
                new_token_string = translate_string_literal(token_string, target_lang, translator)
                token = tokenize.TokenInfo(token_type, new_token_string, token.start, token.end, token.line)
        result_tokens.append(token)
    new_source = tokenize.untokenize(result_tokens)
    return new_source

# ---------------------------------------
# Code cleanup functions
# ---------------------------------------

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.import_nodes = []
        self.assignment_nodes = []
        self.defined_names = set()
        self.used_names = set()

    def visit_Import(self, node):
        names = []
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            names.append(name)
            self.defined_names.add(name)
        self.import_nodes.append((node.lineno, getattr(node, "end_lineno", node.lineno), names))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        names = []
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            names.append(name)
            self.defined_names.add(name)
        self.import_nodes.append((node.lineno, getattr(node, "end_lineno", node.lineno), names))
        self.generic_visit(node)

    def visit_Assign(self, node):
        targets = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                targets.append(target.id)
                self.defined_names.add(target.id)
        if targets:
            self.assignment_nodes.append((node.lineno, getattr(node, "end_lineno", node.lineno), targets))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

def cleanup_code(source):
    try:
        tree = ast.parse(source)
    except Exception as e:
        print("Error parsing source for cleanup:", e)
        return source

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    unused_import_ranges = []
    for start, end, names in analyzer.import_nodes:
        if not any(name in analyzer.used_names for name in names):
            unused_import_ranges.append((start, end))

    unused_assign_ranges = []
    for start, end, names in analyzer.assignment_nodes:
        if not any(name in analyzer.used_names for name in names):
            unused_assign_ranges.append((start, end))

    lines = source.splitlines()
    lines_to_remove = set()
    for start, end in unused_import_ranges + unused_assign_ranges:
        for i in range(start, end + 1):
            lines_to_remove.add(i)
    cleaned_lines = [line for idx, line in enumerate(lines, start=1) if idx not in lines_to_remove]
    cleaned_source = "\n".join(cleaned_lines)
    cleaned_source = re.sub(r'\n\s*\n+', '\n\n', cleaned_source)

    missing_imports = []
    for key, imp_line in COMMON_IMPORTS.items():
        if key not in analyzer.defined_names and key in analyzer.used_names:
            missing_imports.append(imp_line)

    final_lines = cleaned_source.splitlines()
    insert_idx = 0
    if final_lines and final_lines[0].startswith("#!"):
        insert_idx = 1
    if len(final_lines) > insert_idx:
        try:
            mod = ast.parse("\n".join(final_lines[insert_idx:]))
            if (mod.body and isinstance(mod.body[0], ast.Expr) and 
                isinstance(mod.body[0].value, (ast.Str, ast.Constant))):
                insert_idx += 1
        except Exception:
            pass

    existing_imports = set()
    for line in final_lines:
        m = re.match(r'^\s*(import|from)\s+(\S+)', line)
        if m:
            existing_imports.add(line.strip())
    for imp in missing_imports:
        if imp not in existing_imports:
            final_lines.insert(insert_idx, imp)
            insert_idx += 1

    final_source = "\n".join(final_lines)
    final_source = re.sub(r'(\S)\n(def |class )', r'\1\n\n\2', final_source)
    return final_source

def main():
    parser = argparse.ArgumentParser(
        description="Translate UI-related text in a Python script and cleanup code (remove unused imports/vars, extra blank lines).",
        epilog="Usage example:\n  python translator.py -f my_script.py -l english\n  python translator.py -f another_script.py -l russian"
    )
    parser.add_argument('-f', required=True, help='Python script filename')
    parser.add_argument('-l', required=True, help='Target language (e.g., english, russian, chinese)')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    filename = args.f
    target_lang = LANG_MAP.get(args.l.lower(), args.l.lower())

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print("Error reading file:", e)
        sys.exit(1)

    translated_source = translate_source(source, target_lang)
    final_source = cleanup_code(translated_source)
    output_filename = filename + ".translated.py"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_source)
        print("Translated and cleaned file saved as:", output_filename)
    except Exception as e:
        print("Error writing output file:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
```
