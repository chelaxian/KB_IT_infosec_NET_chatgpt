import os
import subprocess
from OpenSSL import crypto
from shutil import copyfile

# 0 =======================================================================================
def find_cert_files():
    """Находит все файлы сертификатов и ключей в текущей директории."""
    extensions = [
        '.pem', '.crt', '.cer', '.der', '.pfx', '.p12', '.p7b', '.p7c', '.key', 
        '.rsa', '.pvk', '.ppk', '.ssh', '.pub', '.openssh', '.cert', '.p8'
    ]
    files = [f for f in os.listdir('.') if os.path.isfile(f) and any(f.lower().endswith(ext) for ext in extensions)]
    return files

def display_files(files):
    """Отображает список файлов и предлагает пользователю выбрать один из них."""
    if not files:
        print("Сертификаты или ключи не найдены в текущей директории.")
        return None

    print("Найдены следующие файлы сертификатов и ключей:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    choice = input("Выберите номер файла: ")
    try:
        return files[int(choice) - 1]
    except (IndexError, ValueError):
        print("Неверный выбор.")
        return None

# 0 =======================================================================================

def is_cer_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате CER."""
    # CER может быть как в формате DER, так и в формате PEM
    return is_der_format(cert_path) or is_pem_format(cert_path)

def is_crt_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате CRT."""
    # CRT может быть как в формате PEM, так и в формате DER
    return is_pem_format(cert_path) or is_der_format(cert_path)

def is_key_format(cert_path):
    """Проверяет, является ли файл ключом в формате PEM или DER."""
    try:
        with open(cert_path, "rb") as key_file:
            key_data = key_file.read()
            # Проверка на PEM-заголовок для ключей
            if b'-----BEGIN' in key_data and b'PRIVATE KEY-----' in key_data:
                return True
            # Проверка с использованием openssl на DER-формат
            result = subprocess.run(['openssl', 'rsa', '-inform', 'DER', '-in', cert_path, '-noout'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
    except Exception:
        return False

def is_pem_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате PEM."""
    try:
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
            return b'-----BEGIN CERTIFICATE-----' in cert_data
    except Exception:
        return False

def is_der_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате DER с помощью команды openssl."""
    try:
        result = subprocess.run(['openssl', 'x509', '-inform', 'DER', '-in', cert_path, '-noout', '-text'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def is_p7b_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате PKCS#7 (P7B/P7C)."""
    try:
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()
            # Проверка на наличие PEM-заголовков PKCS#7
            if b'-----BEGIN PKCS7-----' in cert_data and b'-----END PKCS7-----' in cert_data:
                return True
            # Проверка с использованием openssl на DER-формат для PKCS#7
            result = subprocess.run(['openssl', 'pkcs7', '-inform', 'DER', '-in', cert_path, '-noout', '-print_certs'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
    except Exception:
        return False

def is_p7c_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате PKCS#7 (P7C)."""
    return is_p7b_format(cert_path)  # P7B и P7C имеют одинаковую структуру, разница только в расширении

def is_pfx_format(cert_path):
    """Проверяет, является ли файл сертификатом в формате PFX/P12 с помощью команды openssl."""
    try:
        result = subprocess.run(['openssl', 'pkcs12', '-in', cert_path, '-noout'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def determine_format(filename):
    """Определяет формат сертификата по расширению и проверяет его корректность."""
    extension = filename.lower().split('.')[-1]

    if extension == 'pem':
        return 'PEM' if is_pem_format(filename) else None
    elif extension == 'der':
        return 'DER' if is_der_format(filename) else None
    elif extension == 'p7b':
        return 'P7B' if is_p7b_format(filename) else None
    elif extension == 'p7c':
        return 'P7C' if is_p7c_format(filename) else None
    elif extension == 'crt':
        return 'CRT' if is_crt_format(filename) else None
    elif extension == 'cer':
        return 'CER' if is_cer_format(filename) else None
    elif extension == 'pfx':
        return 'PFX' if is_pfx_format(filename) else None
    elif extension == 'p12':
        return 'P12' if is_pfx_format(filename) else None
    elif extension == 'key':
        return 'KEY' if is_key_format(filename) else None
    elif extension in ['rsa', 'pvk', 'ppk', 'ssh', 'pub', 'openssh']:
        return 'KEY'  # Секретные и публичные ключи различных форматов
    elif extension == 'cert':
        return 'CERT' if is_pem_format(filename) else None  # Файлы CERT обычно в формате PEM
    elif extension == 'p8':
        return 'P8'  # Файлы PKCS8, возможно, содержат ключи, их нужно проверять отдельно
    else:
        print(f"Неизвестное расширение файла: {extension}")
        return None


# 1 =======================================================================================
        
def split_pfx(pfx_file):
    """Разбивает PFX/P12 на закрытый ключ и сертификат."""
    password = input('Введите пароль для PFX/P12: ')
    private_key_file = 'private.key'
    cert_file = 'public.crt'
    
    try:
        # Извлечение закрытого ключа
        subprocess.run(['openssl', 'pkcs12', '-in', pfx_file, '-nocerts', '-out', private_key_file, '-nodes', '-passin', f'pass:{password}'], check=True)
        # Извлечение сертификата
        subprocess.run(['openssl', 'pkcs12', '-in', pfx_file, '-clcerts', '-nokeys', '-out', cert_file, '-passin', f'pass:{password}'], check=True)
        print(f'Закрытый ключ и сертификат успешно извлечены: {private_key_file}, {cert_file}')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при разбиении PFX/P12: {e}')
        

# 2 =======================================================================================
def convert_certificate(input_file):
    """Конвертирует сертификат в указанный формат."""
    formats = ['PEM', 'DER', 'PFX', 'P12', 'P7B', 'P7C', 'CRT', 'CER']
    print("Выберите формат для преобразования:")
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt}")

    choice = input("Выберите номер формата: ")
    try:
        output_format = formats[int(choice) - 1]
    except (IndexError, ValueError):
        print("Неверный выбор.")
        return None

    input_format = determine_format(input_file)
    if not input_format:
        print(f"Файл {input_file} не является допустимым сертификатом.")
        return None

    # Устанавливаем имя выходного файла
    output_file = os.path.splitext(input_file)[0] + '.' + output_format.lower()

    # Если файл существует, удаляем его
    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        # Логика для конвертации
        if input_format == output_format:
            print(f"Файл уже в формате {output_format}.")
            return None
        elif input_format == 'PEM' and output_format == 'DER':
            subprocess.run(['openssl', 'x509', '-in', input_file, '-outform', 'der', '-out', output_file], check=True)
        elif input_format == 'DER' and output_format == 'PEM':
            subprocess.run(['openssl', 'x509', '-in', input_file, '-inform', 'der', '-out', output_file, '-outform', 'pem'], check=True)
        elif input_format == 'PEM' and output_format == 'PFX':
            key_file = input("Введите путь к приватному ключу (private key): ")
            subprocess.run(['openssl', 'pkcs12', '-export', '-out', output_file, '-inkey', key_file, '-in', input_file], check=True)
        elif input_format == 'PEM' and output_format == 'P7B':
            subprocess.run(['openssl', 'crl2pkcs7', '-nocrl', '-certfile', input_file, '-out', output_file], check=True)
        elif input_format == 'PEM' and output_format == 'P7C':
            subprocess.run(['openssl', 'crl2pkcs7', '-nocrl', '-certfile', input_file, '-out', output_file], check=True)
        elif input_format == 'PEM' and output_format in ['CRT', 'CER']:
            # Конвертация из PEM в CRT или CER (просто копирование файла)
            copyfile(input_file, output_file)
            print(f"Файл сохранен как {output_file}")
        elif input_format == 'DER' and output_format == 'PFX':
            key_file = input("Введите путь к приватному ключу (private key): ")
            subprocess.run(['openssl', 'pkcs12', '-export', '-in', input_file, '-inkey', key_file, '-out', output_file], check=True)
        elif input_format == 'DER' and output_format == 'P7B':
            subprocess.run(['openssl', 'crl2pkcs7', '-nocrl', '-certfile', input_file, '-out', output_file], check=True)
        elif input_format in ['PFX', 'P12'] and output_format == 'PEM':
            subprocess.run(['openssl', 'pkcs12', '-in', input_file, '-out', output_file, '-nodes'], check=True)
        elif input_format in ['P7B', 'P7C'] and output_format == 'PEM':
            subprocess.run(['openssl', 'pkcs7', '-print_certs', '-in', input_file, '-out', output_file], check=True)
        elif input_format == 'P7B' and output_format == 'DER':
            subprocess.run(['openssl', 'pkcs7', '-inform', 'PEM', '-outform', 'DER', '-in', input_file, '-out', output_file], check=True)
        elif input_format in ['PFX', 'P12'] and output_format == 'DER':
            subprocess.run(['openssl', 'pkcs12', '-in', input_file, '-out', output_file, '-nodes', '-outform', 'DER'], check=True)
        elif input_format == 'P7B' and output_format == 'PFX':
            temp_pem = "temp.pem"
            subprocess.run(['openssl', 'pkcs7', '-print_certs', '-in', input_file, '-out', temp_pem], check=True)
            key_file = input("Введите путь к приватному ключу (private key): ")
            subprocess.run(['openssl', 'pkcs12', '-export', '-in', temp_pem, '-inkey', key_file, '-out', output_file], check=True)
            os.remove(temp_pem)
        elif input_format in ['CRT', 'CER'] and output_format == 'PEM':
            subprocess.run(['openssl', 'x509', '-in', input_file, '-inform', 'der', '-out', output_file, '-outform', 'pem'], check=True)
        elif input_format in ['CRT', 'CER'] and output_format == 'DER':
            subprocess.run(['openssl', 'x509', '-in', input_file, '-inform', 'pem', '-out', output_file, '-outform', 'der'], check=True)
        elif (input_format == 'PFX' and output_format == 'P12') or (input_format == 'P12' and output_format == 'PFX'):
            # PFX в P12 или P12 в PFX - просто смена расширения
            copyfile(input_file, output_file)
            print(f"Файл сохранен как {output_file}")
        elif (input_format == 'P7B' and output_format == 'P7C') or (input_format == 'P7C' and output_format == 'P7B'):
            # P7B в P7C или P7C в P7B - просто смена расширения
            copyfile(input_file, output_file)
            print(f"Файл сохранен как {output_file}")
        elif (input_format == 'CER' and output_format == 'CRT') or (input_format == 'CRT' and output_format == 'CER'):
            # CER в CRT или CRT в CER - просто смена расширения
            copyfile(input_file, output_file)
            print(f"Файл сохранен как {output_file}")
        elif input_format == 'KEY' and output_format == 'PEM':
            # Преобразование закрытого ключа из DER в PEM
            subprocess.run(['openssl', 'rsa', '-inform', 'DER', '-in', input_file, '-out', output_file, '-outform', 'PEM'], check=True)
            print(f"Ключ преобразован и сохранен в {output_file}")
        elif input_format == 'KEY' and output_format == 'DER':
            # Преобразование закрытого ключа из PEM в DER
            subprocess.run(['openssl', 'rsa', '-in', input_file, '-outform', 'DER', '-out', output_file], check=True)
            print(f"Ключ преобразован и сохранен в {output_file}")
        else:
            print(f'Невозможно преобразовать из {input_format} в {output_format}.')
            return None

        print(f'Сертификат преобразован и сохранен в {output_file}')
        return output_file

    except subprocess.CalledProcessError as e:
        print(f'Ошибка преобразования сертификата: {e}')
    except FileNotFoundError:
        print(f"Не удалось найти файл {input_file} для переименования.")
    return None


# 3 =======================================================================================

def merge_pem_to_pfx(cert_file, key_file):
    """Собирает два файла в контейнер PFX/P12."""
    password = input('Введите пароль для нового PFX/P12 контейнера: ')
    output_name = input('Введите желаемое имя для файла: ') or 'output'
    
    # Меню выбора формата
    print("Выберите формат файла:")
    print("1. PFX")
    print("2. P12")
    format_choice = input("Выберите номер формата: ")

    if format_choice == '1':
        output_format = 'pfx'
    elif format_choice == '2':
        output_format = 'p12'
    else:
        print("Неверный выбор формата.")
        return

    output_pfx = f'{output_name}.{output_format}'

    try:
        # Убедимся, что файл ключа существует и читается
        if not os.path.isfile(key_file):
            print(f"Файл закрытого ключа {key_file} не найден.")
            return
        if not os.path.isfile(cert_file):
            print(f"Файл сертификата {cert_file} не найден.")
            return

        # Команда для создания контейнера PFX/P12
        subprocess.run(['openssl', 'pkcs12', '-export', '-out', output_pfx,
                        '-inkey', key_file, '-in', cert_file,
                        '-password', f'pass:{password}'], check=True)
        print(f'Контейнер {output_format.upper()} успешно создан: {output_pfx}')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при создании {output_format.upper()}: {e}')
    except Exception as e:
        print(f'Общая ошибка: {e}')

# 4 =======================================================================================
def change_cert_format(cert_path):
    """
    Конвертирует сертификат из одного формата в другой (PEM <-> DER).
    """
    try:
        if is_pem_format(cert_path):
            print("Сертификат в формате PEM. Преобразуем в DER.")
            output_path = f"{os.path.splitext(cert_path)[0]}_converted.der"
            subprocess.run(['openssl', 'x509', '-in', cert_path, '-outform', 'DER', '-out', output_path], check=True)
            print(f"Сертификат сохранен в формате DER как {output_path}")

        elif is_der_format(cert_path):
            print("Сертификат в формате DER. Преобразуем в PEM.")
            output_path = f"{os.path.splitext(cert_path)[0]}_converted.pem"
            subprocess.run(['openssl', 'x509', '-inform', 'DER', '-in', cert_path, '-out', output_path, '-outform', 'PEM'], check=True)
            print(f"Сертификат сохранен в формате PEM как {output_path}")

        else:
            print("Файл не является допустимым сертификатом в формате PEM или DER.")
            return

    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации сертификата: {e}")
        print("Проверьте, является ли файл действительно сертификатом в формате DER или PEM и доступен ли он для чтения.")
    except Exception as e:
        print(f"Ошибка: {e}")

# 5 =======================================================================================
def split_certificate_chain(cert_path):
    """
    Разбивает цепочку сертификатов в файле PEM на отдельные сертификаты.
    """
    try:
        with open(cert_path, "rb") as cert_file:
            cert_data = cert_file.read()

        if b"-----BEGIN CERTIFICATE-----" not in cert_data:
            print("Ошибка: Файл не является сертификатом в формате PEM.")
            return

        certificates = cert_data.split(b"-----END CERTIFICATE-----")
        output_files = []

        for i, cert in enumerate(certificates):
            if b"-----BEGIN CERTIFICATE-----" in cert:
                cert += b"-----END CERTIFICATE-----\n"
                output_path = f"{os.path.splitext(cert_path)[0]}_split_{i+1}.pem"
                with open(output_path, "wb") as output_file:
                    output_file.write(cert)
                output_files.append(output_path)

        if output_files:
            print(f"Цепочка сертификатов разбита на {len(output_files)} частей: {', '.join(output_files)}")
        else:
            print("Ошибка: Не удалось разбить цепочку сертификатов.")

    except Exception as e:
        print(f"Ошибка: {e}")

# 6 =======================================================================================
        
def merge_cert_chain():
    """Собирает цепочку сертификатов из отдельных файлов."""
    root_cert = display_files([f for f in find_cert_files() if f.lower().endswith(('.pem', '.crt', '.cer'))])
    if not root_cert:
        return

    certs = [root_cert]
    while True:
        choice = input("Добавить промежуточный сертификат? (1 - Да, 2 - Нет): ")
        if choice == '1':
            intermediate_cert = display_files([f for f in find_cert_files() if f.lower().endswith(('.pem', '.crt', '.cer'))])
            if intermediate_cert:
                certs.append(intermediate_cert)
        else:
            break

    end_cert = display_files([f for f in find_cert_files() if f.lower().endswith(('.pem', '.crt', '.cer'))])
    if end_cert:
        certs.append(end_cert)
    else:
        print("Финальный сертификат не выбран.")
        return

    formats = ['P7B', 'P7C']
    print("Выберите формат для сохранения цепочки сертификатов:")
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt}")

    choice = input("Выберите номер формата: ")
    try:
        output_format = formats[int(choice) - 1]
    except (IndexError, ValueError):
        print("Неверный выбор.")
        return None

    output_file = 'certificate_chain.' + output_format.lower()
    with open(output_file, 'wb') as out_file:
        for cert in certs:
            with open(cert, 'rb') as in_file:
                out_file.write(in_file.read())
    print(f'Цепочка сертификатов собрана и сохранена в {output_file}')

# MENU ====================================================================================
def main():
    print("Конвертор сертификатов и ключей")
    print("1. Разбить контейнер PFX/P12 на 2 части PEM")
    print("2. Преобразовать из одного формата в другой")
    print("3. Собрать 2 части в контейнер PFX/P12")
    print("4. CER/CRT - смена формата PEM/DER")
    print("5. Разбить цепочку сертификатов")
    print("6. Сбор сертификатов в цепочку")
    choice = input("Выберите номер меню: ")

    if choice == '1':
        files = find_cert_files()
        pfx_file = display_files([f for f in files if f.lower().endswith(('.pfx', '.p12'))])
        if pfx_file:
            split_pfx(pfx_file)
    elif choice == '2':
        files = find_cert_files()
        cert_file = display_files(files)
        if cert_file:
            convert_certificate(cert_file)
    elif choice == '3':
        files = find_cert_files()
        cert_file = display_files([f for f in files if f.lower().endswith(('.pem', '.crt', '.cer', '.der'))])
        key_file = display_files([f for f in files if f.lower().endswith(('.key', '.pem', '.rsa', '.pvk', '.ppk', '.ssh', '.openssh', '.p8'))])
        if cert_file and key_file:
            merge_pem_to_pfx(cert_file, key_file)
    elif choice == '4':
        files = find_cert_files()
        cert_file = display_files([f for f in files if f.lower().endswith(('.cer', '.crt'))])
        if cert_file:
            change_cert_format(cert_file)
    elif choice == '5':
        files = find_cert_files()
        chain_file = display_files([f for f in files if f.lower().endswith(('.pem', '.crt', '.cer', '.p7b', '.p7c'))])
        if chain_file:
            split_certificate_chain(chain_file)
    elif choice == '6':
        merge_cert_chain()
    else:
        print("Неверный выбор. Завершение программы.")

if __name__ == "__main__":
    main()
