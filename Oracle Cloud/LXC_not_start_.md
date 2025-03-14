```proxmox
explicitly configured lxc.apparmor.profile overrides the following settings: features:nesting
run_buffer: 571 Script exited with status 11
lxc_init: 845 Failed to run lxc.hook.pre-start for container "103"
__lxc_start: 2034 Failed to initialize container "103"
TASK ERROR: startup for container '103' failed
```
---

```bash
root@deb320:~# pct start 103 --debug
explicitly configured lxc.apparmor.profile overrides the following settings: features:nesting
run_buffer: 571 Script exited with status 11
lxc_init: 845 Failed to run lxc.hook.pre-start for container "103"
__lxc_start: 2034 Failed to initialize container "103"
rt-hook" for container "103", config section "lxc"
DEBUG    utils - ../src/lxc/utils.c:run_buffer:560 - Script exec /usr/share/lxc/hooks/lxc-pve-prestart-hook 103 lxc pre-start produced output: org.freedesktop.DBus.Error.ServiceUnknown: The name uk.org.thekelleys.dnsmasq.DHCP was not provided by any .service files

ERROR    utils - ../src/lxc/utils.c:run_buffer:571 - Script exited with status 11
ERROR    start - ../src/lxc/start.c:lxc_init:845 - Failed to run lxc.hook.pre-start for container "103"
ERROR    start - ../src/lxc/start.c:__lxc_start:2034 - Failed to initialize container "103"
INFO     utils - ../src/lxc/utils.c:run_script_argv:587 - Executing script "/usr/share/lxc/hooks/lxc-pve-poststop-hook" for container "103", config section "lxc"
startup for container '103' failed
```

---

ПРОБЛЕМА С SDN (DHCP) - УДАЛИТЬ 2-ОЙ СЕТЕВОЙ АДАПТЕР С DHCP

---

Ошибка возникает в хуке предварительного запуска контейнера, когда Proxmox пытается обратиться к DBus-сервису, который должен быть предоставлен dnsmasq (имя сервиса – "uk.org.thekelleys.dnsmasq.DHCP"). DBus сообщает, что такого сервиса нет, то есть отсутствует соответствующая конфигурация, разрешающая dnsmasq владеть данным именем.

Чтобы исправить проблему, можно создать для dnsmasq специальный конфигурационный файл для DBus. Например, выполните следующие шаги:

1. На хосте Proxmox (если dnsmasq уже установлен) создайте файл  
   **/etc/dbus-1/system.d/dnsmasq.conf**  
   со следующим содержимым (это пример, который разрешает пользователю root и пользователю dnsmasq владеть именем сервиса):

   ```xml
   <!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
   <busconfig>
       <policy user="root">
           <allow own="uk.org.thekelleys.dnsmasq.DHCP"/>
           <allow send_destination="uk.org.thekelleys.dnsmasq.DHCP"/>
       </policy>
       <policy user="dnsmasq">
           <allow own="uk.org.thekelleys.dnsmasq.DHCP"/>
           <allow send_destination="uk.org.thekelleys.dnsmasq.DHCP"/>
       </policy>
       <policy context="default">
           <deny own="uk.org.thekelleys.dnsmasq.DHCP"/>
           <deny send_destination="uk.org.thekelleys.dnsmasq.DHCP"/>
       </policy>
   </busconfig>
   ```

2. После сохранения файла перезапустите демон DBus (или перезагрузите сервер), чтобы он прочитал новую конфигурацию:
   
   ```bash
   systemctl restart dbus
   ```

После этого Proxmox должен увидеть, что нужное имя сервиса зарегистрировано, и хук предварительного запуска контейнера завершится успешно.

Если вы не используете DHCP для контейнеров или функция не нужна, можно рассмотреть вариант отключения соответствующего функционала (например, убрать настройку, которая вызывает обращение к dnsmasq через DBus), но в большинстве случаев правильнее настроить DBus-конфигурацию.

Проверьте также, установлен ли dnsmasq (или dnsmasq-base) на вашем Proxmox‑хосте, так как он должен запускаться для поддержки DHCP (если используется).

Попробуйте этот метод – он уже помог пользователям в аналогичных случаях. Если после внесения изменений проблема останется, предоставьте дополнительные логи и детали конфигурации, чтобы можно было рассмотреть вариант более детально.

---

Ошибка указывает на то, что при запуске контейнера Proxmox пытается выполнить хук (lxc-pve-prestart-hook), который обращается к сервису DBus с именем  
**"uk.org.thekelleys.dnsmasq.DHCP"** – этот сервис должен предоставляться (обычно для работы SDN/DHCP в Proxmox), но его нет.

В вашем случае в конфигурации контейнера заметен второй сетевой интерфейс:

```ini
net1: name=dhcp,bridge=DHCP,firewall=1,hwaddr=BC:24:11:19:D5:6D,ip=dhcp,ip6=dhcp,type=veth
```

Такой интерфейс настроен на получение IP по DHCP через мост с именем «DHCP». Если вы не используете функции SDN (например, автоматический DHCP, который настраивается через dnsmasq с использованием DBus), то наличие такого интерфейса вызывает попытку обращения к несуществующему сервису.

Чтобы исправить ситуацию, попробуйте один из вариантов:

1. **Если функция DHCP через SDN вам не нужна:**
   - Удалите или измените конфигурацию второго сетевого интерфейса (net1). Например, оставьте только интерфейс net0, который подключается к вашему основному мосту (vmbr0) с нужной конфигурацией (либо задайте статический IP, либо настройте его по-другому).

2. **Если же вам нужна функция SDN DHCP:**
   - Проверьте, настроена ли у вас SDN в Proxmox и запущен ли соответствующий dnsmasq-сервис для зоны DHCP. Возможно, в настройках SDN не активирован нужный DHCP-сервис или он настроен неверно.
   - Убедитесь, что в Proxmox SDN настроен и включён dnsmasq для вашей DHCP-зоны (например, проверьте конфигурацию в /etc/pve/sdn).

На практике многие администраторы, не используя SDN, просто исключают из конфигурации контейнера интерфейс, настроенный на мост «DHCP». Если для вашего контейнера достаточно одного сетевого интерфейса (например, net0 с bridge=vmbr0), попробуйте удалить или закомментировать строку с net1.

После внесения изменений сохраните конфигурацию и попробуйте снова запустить контейнер:

```bash
pct start 103 --debug
```

Если контейнер запустится, проблема была именно в попытке обращения к отсутствующему DBus-сервису для DHCP.

Если же вам необходим второй интерфейс с DHCP, необходимо настроить SDN на Proxmox и убедиться, что dnsmasq (с поддержкой DBus) запущен корректно. Для этого можно проверить настройки SDN через веб-интерфейс Proxmox, а также статус соответствующего dnsmasq-сервиса (например, через `systemctl status dnsmasq@<zone>.service`).

Попробуйте предложенные варианты и сообщите, если возникнут дополнительные вопросы.
