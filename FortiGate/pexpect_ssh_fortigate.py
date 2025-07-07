import time
import subprocess
import platform
import pexpect
from datetime import datetime, timedelta

# Настройки SSH для FortiGate
FORTIGATE_IP = "192.168.1.99"
FORTIGATE_USER = "admin"
FORTIGATE_PASSWORD = "password"

# Команды для FortiGate
FORTIGATE_CMD_ENABLE_BOTH = "execute auto-script start Enable-Both-Tunnels"
FORTIGATE_CMD_TUN1 = "execute auto-script start Tun1-Enable-Tun2-Disable"
FORTIGATE_CMD_TUN2 = "execute auto-script start Tun2-Enable-Tun1-Disable"

# Мониторинг IP-адреса
MONITOR_IP = "10.0.0.2"
PING_INTERVAL = 1
PING_FAIL_LIMIT = 2

# Логирование
LOG_FILE = "/tmp/mnt/EXT/home/ping_vpn_fgt.log"
LOG_CLEAR_INTERVAL = timedelta(days=1)  # Интервал очистки лога
last_log_clear_time = datetime.now()  # Время последней очистки лога

def log_message(message):
    """Записывает сообщение в лог-файл и на экран."""
    global last_log_clear_time
    current_time = datetime.now()

    # Очистка лога раз в сутки
    if current_time - last_log_clear_time >= LOG_CLEAR_INTERVAL:
        with open(LOG_FILE, "w") as log_file:
            log_file.write(f"{current_time} — Лог очищен.\n")
        last_log_clear_time = current_time

    # Запись в лог
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{current_time} — {message}\n")
    print(message)  # Для ручного запуска

def is_host_reachable(ip):
    """Проверяет доступность хоста через ping."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(["ping", param, "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def ssh_execute_command(host, user, password, command):
    """Выполняет SSH-команду с вводом пароля через `pexpect`."""
    try:
        log_message(f"Отправка команды на FortiGate: {command}")
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null {user}@{host} {command}"
        child = pexpect.spawn(ssh_cmd, timeout=30)
        child.expect("password:")
        child.sendline(password)
        child.expect(pexpect.EOF)
        output = child.before.decode(errors="ignore")
        log_message(output)
    except Exception as e:
        log_message(f"Ошибка SSH-подключения: {e}")


def monitor_and_react():
    """Мониторинг туннелей и автоматическое переключение при потере связи."""
    log_message("🔄 Включаем оба туннеля перед стартом мониторинга...")
    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_ENABLE_BOTH)

    log_message("⏳ Ждем 2 секунды перед началом мониторинга...")
    time.sleep(2)

    last_script = None
    failed_pings = 0

    while True:
        if is_host_reachable(MONITOR_IP):
            log_message(f"✅ {MONITOR_IP} доступен, продолжаем мониторинг...")
            failed_pings = 0
            time.sleep(PING_INTERVAL)
            continue

        failed_pings += 1
        log_message(f"⚠️ {MONITOR_IP} недоступен ({failed_pings}/{PING_FAIL_LIMIT})")

        if failed_pings < PING_FAIL_LIMIT:
            time.sleep(PING_INTERVAL)
            continue

        log_message(f"🚨 Связь с {MONITOR_IP} отсутствует. Переключаем туннели...")

        if last_script == "Tun1-Enable-Tun2-Disable":
            ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN2)
            last_script = "Tun2-Enable-Tun1-Disable"
        else:
            ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN1)
            last_script = "Tun1-Enable-Tun2-Disable"

        failed_pings = 0

        retry_pings = 0
        while not is_host_reachable(MONITOR_IP):
            retry_pings += 1
            log_message(f"⏳ Ожидание восстановления связи с {MONITOR_IP} ({retry_pings}/{PING_FAIL_LIMIT})...")
            if retry_pings >= PING_FAIL_LIMIT:
                log_message(f"🔁 Связь не восстановилась, переключаем туннели обратно!")
                if last_script == "Tun1-Enable-Tun2-Disable":
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN2)
                    last_script = "Tun2-Enable-Tun1-Disable"
                else:
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN1)
                retry_pings = 0
                break

            time.sleep(PING_INTERVAL)

        log_message(f"✅ Связь с {MONITOR_IP} восстановлена, продолжаем мониторинг...")
        failed_pings = 0

if __name__ == "__main__":
    monitor_and_react()
