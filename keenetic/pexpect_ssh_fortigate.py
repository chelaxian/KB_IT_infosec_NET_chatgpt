import time
import subprocess
import platform
import pexpect

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

def is_host_reachable(ip):
    """Проверяет доступность хоста через ping."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(["ping", param, "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def ssh_execute_command(host, user, password, command):
    """Выполняет SSH-команду с вводом пароля через `pexpect`, обрабатывая разные вариации запросов."""
    try:
        print(f"Отправка команды на FortiGate: {command}")
        child = pexpect.spawn(f"ssh {user}@{host} {command}", timeout=10)

        # Ждем один из возможных вариантов запроса пароля
        index = child.expect([
            "password:", 
            f"{user}@{host}'s password:", 
            pexpect.TIMEOUT, 
            pexpect.EOF
        ], timeout=5)

        if index in [0, 1]:  # Если запрашивается пароль
            child.sendline(password)
            child.expect(pexpect.EOF, timeout=10)

        output = child.before.decode()
        print(output)

    except pexpect.TIMEOUT:
        print("❌ Ошибка: SSH-соединение зависло (TIMEOUT).")
    except Exception as e:
        print(f"❌ Ошибка SSH: {e}")

def monitor_and_react():
    """Мониторинг туннелей и автоматическое переключение при потере связи."""
    print("🔄 Включаем оба туннеля перед стартом мониторинга...")
    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_ENABLE_BOTH)

    print("⏳ Ждем 2 секунды перед началом мониторинга...")
    time.sleep(2)

    last_script = None
    failed_pings = 0

    while True:
        if is_host_reachable(MONITOR_IP):
            print(f"✅ {MONITOR_IP} доступен, продолжаем мониторинг...")
            failed_pings = 0
            time.sleep(PING_INTERVAL)
            continue

        failed_pings += 1
        print(f"⚠️ {MONITOR_IP} недоступен ({failed_pings}/{PING_FAIL_LIMIT})")

        if failed_pings < PING_FAIL_LIMIT:
            time.sleep(PING_INTERVAL)
            continue

        print(f"🚨 Связь с {MONITOR_IP} отсутствует. Переключаем туннели...")

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
            print(f"⏳ Ожидание восстановления связи с {MONITOR_IP} ({retry_pings}/{PING_FAIL_LIMIT})...")
            if retry_pings >= PING_FAIL_LIMIT:
                print(f"🔁 Связь не восстановилась, переключаем туннели обратно!")
                if last_script == "Tun1-Enable-Tun2-Disable":
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN2)
                    last_script = "Tun2-Enable-Tun1-Disable"
                else:
                    ssh_execute_command(FORTIGATE_IP, FORTIGATE_USER, FORTIGATE_PASSWORD, FORTIGATE_CMD_TUN1)
                    last_script = "Tun1-Enable-Tun2-Disable"
                retry_pings = 0
                break

            time.sleep(PING_INTERVAL)

        print(f"✅ Связь с {MONITOR_IP} восстановлена, продолжаем мониторинг...")
        failed_p
