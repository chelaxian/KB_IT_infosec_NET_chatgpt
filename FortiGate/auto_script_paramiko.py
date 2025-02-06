import paramiko
import time
import subprocess
import platform

# Настройки SSH для FortiGate
FORTIGATE_IP = "192.168.1.1"  # IP FortiGate
FORTIGATE_USER = "admin"
FORTIGATE_PASSWORD = "password"

# Команды для запуска скриптов
FORTIGATE_CMD_ENABLE_BOTH = "execute auto-script start Enable-Both-Tunnels"
FORTIGATE_CMD_TUN1 = "execute auto-script start Tun1-Enable-Tun2-Disable"
FORTIGATE_CMD_TUN2 = "execute auto-script start Tun2-Enable-Tun1-Disable"

# Мониторинг IP-адреса
MONITOR_IP = "10.0.0.2"
PING_INTERVAL = 1  # Интервал проверки (примерно как в Windows)
PING_FAIL_LIMIT = 2  # Количество неуспешных пингов перед переключением

def is_host_reachable(ip):
    """Проверяет доступность хоста через ping с локальной машины."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(["ping", param, "1", "-w", "1000", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception as e:
        print(f"Ошибка выполнения ping: {e}")
        return False

def ssh_execute_command(host, user, password, command):
    """Подключается по SSH и выполняет команду."""
    try:
        print(f"Отправка команды на FortiGate: {command}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=user, password=password, timeout=5)

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        client.close()
        if error:
            print(f"Ошибка выполнения команды: {error}")
        else:
            print(f"Выполнена команда: {command}")
            print(output)
    except Exception as e:
        print(f"Ошибка SSH подключения: {e}")

def monitor_and_react():
    """Сначала включает оба туннеля, затем ждет 2 секунды и начинает мониторинг."""
    print("🔄 Включаем оба туннеля перед стартом мониторинга...")
    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_ENABLE_BOTH)

    print("⏳ Ждем 2 секунды перед началом мониторинга...")
    time.sleep(2)  # Задержка перед мониторингом

    last_script = None  # Какой скрипт запускался последним
    failed_pings = 0  # Счетчик неудачных пингов

    while True:
        if is_host_reachable(MONITOR_IP):
            print(f"✅ {MONITOR_IP} доступен, продолжаем мониторинг...")
            failed_pings = 0  # Сбрасываем счетчик
            time.sleep(PING_INTERVAL)  # Интервал проверки (1 сек)
            continue

        failed_pings += 1
        print(f"⚠️ {MONITOR_IP} недоступен ({failed_pings}/{PING_FAIL_LIMIT})")

        if failed_pings < PING_FAIL_LIMIT:
            time.sleep(PING_INTERVAL)
            continue  # Даем еще шанс восстановиться

        print(f"🚨 Связь с {MONITOR_IP} отсутствует. Переключаем туннели...")

        if last_script == "Tun1-Enable-Tun2-Disable":
            ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN2)
            last_script = "Tun2-Enable-Tun1-Disable"
        else:
            ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN1)
            last_script = "Tun1-Enable-Tun2-Disable"

        failed_pings = 0  # Сбрасываем счетчик

        # Ожидание восстановления связи
        retry_pings = 0
        while not is_host_reachable(MONITOR_IP):
            retry_pings += 1
            print(f"⏳ Ожидание восстановления связи с {MONITOR_IP} ({retry_pings}/{PING_FAIL_LIMIT})...")
            if retry_pings >= PING_FAIL_LIMIT:
                print(f"🔁 Связь не восстановилась, переключаем туннели обратно!")
                if last_script == "Tun1-Enable-Tun2-Disable":
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN2)
                    last_script = "Tun2-Enable-Tun1-Disable"
                else:
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN1)
                    last_script = "Tun1-Enable-Tun2-Disable"
                retry_pings = 0  # Сбрасываем счетчик
                break  # Возвращаемся к мониторингу

            time.sleep(PING_INTERVAL)

        print(f"✅ Связь с {MONITOR_IP} восстановлена, продолжаем мониторинг...")
        failed_pings = 0  # Сбрасываем счетчик

if __name__ == "__main__":
    monitor_and_react()
