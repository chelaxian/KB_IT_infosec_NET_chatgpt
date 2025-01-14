import os
import subprocess

# Путь к конфигурационному файлу
CONFIG_FILE = "/opt/ptaf/conf/nginx.conf"

# Функция для чтения конфигурации
def read_config():
    with open(CONFIG_FILE, "r") as file:
        return file.readlines()

# Функция для записи конфигурации
def write_config(lines):
    with open(CONFIG_FILE, "w") as file:
        file.writelines(lines)

# Функция для проверки ответа на согласие/отказ
def is_positive_response(response):
    positive_responses = {"да", "д", "yes", "y"}
    return response.lower() in positive_responses

def is_negative_response(response):
    negative_responses = {"нет", "н", "no", "n"}
    return response.lower() in negative_responses

# Функция для обновления конфигурации
def update_config(upstream_name, server_address, fqdns, enable_ntlm):
    config = read_config()

    # Обновляем блок upstream
    ntlm_directive = "transparent ntlm;" if enable_ntlm else "# transparent ntlm;"
    upstream_block = (
        f"  upstream {upstream_name} {{\n"
        f"    server {server_address} weight=1 max_fails=1;\n"
        f"    keepalive_timeout 60s;\n"
        f"    keepalive 32;\n"
        f"    {ntlm_directive}\n"
        f"  }}\n"
    )

    if upstream_block.strip() not in "".join(config):
        for i, line in enumerate(config):
            if "# (Конец) Защищаемые серверы" in line:
                config.insert(i, upstream_block)
                break

    # Обновляем блоки server_name и location для каждого FQDN
    for fqdn in fqdns:
        fqdn_block = f"        {fqdn}\n"
        for i, line in enumerate(config):
            if "server_name" in line and "ssl" in config[i - 1]:
                if fqdn_block.strip() not in "".join(config[i:]):
                    config.insert(i + 1, fqdn_block)
                break

        location_block = f"\t\tif ($host = \"{fqdn}\") {{ set $upstream_name {upstream_name}; }}\n"
        for i, line in enumerate(config):
            if "location / {" in line:
                # Найден блок location, теперь ищем строку set $upstream_name "";
                for j in range(i, len(config)):
                    if "set $upstream_name \"\";" in config[j]:
                        # Вставляем блок location сразу после этой строки
                        if location_block.strip() not in "".join(config[j + 1:]):
                            config.insert(j + 1, location_block)
                        break
                break

    write_config(config)

# Основная функция
def main():
    if not os.path.exists(CONFIG_FILE):
        print(f"Конфигурационный файл {CONFIG_FILE} не найден.")
        return

    upstream_name = input("Введите имя upstream (например, Service-Desk): ").strip()
    server_address = input("Введите адрес и порт (например, 10.0.128.6:32034): ").strip()
    fqdns_input = input("Введите FQDN (можно несколько через пробел, запятую или точку с запятой): ").strip()
    fqdns = [fqdn.strip() for fqdn in fqdns_input.replace(",", " ").replace(";", " ").split()]

    while True:
        enable_ntlm_input = input("Включить директиву transparent NTLM? (да/нет): ").strip().lower()
        if is_positive_response(enable_ntlm_input):
            enable_ntlm = True
            break
        elif is_negative_response(enable_ntlm_input):
            enable_ntlm = False
            break
        else:
            print("Пожалуйста, введите да/нет, yes/no, д/н или y/n.")

    update_config(upstream_name, server_address, fqdns, enable_ntlm)
    print(f"Конфигурационный файл {CONFIG_FILE} успешно обновлен.")

    # Проверка конфигурации
    try:
        subprocess.run(["ptaf-nginx", "-t"], check=True)
        print("Конфигурация nginx успешно проверена.")
    except subprocess.CalledProcessError:
        print("Ошибка проверки конфигурации nginx.")
        return

    # Перезапуск сервиса
    try:
        subprocess.run(["sudo", "systemctl", "restart", "ptaf-nginx"], check=True)
        print("Сервис nginx успешно перезапущен.")
    except subprocess.CalledProcessError:
        print("Ошибка перезапуска сервиса nginx.")

if __name__ == "__main__":
    main()
