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

---

Если вы хотите вернуть второй сетевой адаптер с DHCP (то есть использовать SDN для автоматической выдачи IP), то необходимо правильно настроить SDN-зону в Proxmox. Сейчас при наличии второго адаптера с bridge=DHCP система пытается получить от dnsmasq через DBus сервис с именем «uk.org.thekelleys.dnsmasq.DHCP», но такой сервис не зарегистрирован, потому что для этой зоны не создана корректная конфигурация.

Чтобы исправить ситуацию и вернуть адаптер с DHCP, выполните следующие шаги:

1. **Создайте или отредактируйте SDN-конфигурацию**  
   На узле Proxmox все настройки SDN хранятся в каталоге `/etc/pve/sdn/`. Откройте (или создайте) файл, например, `subnets.cfg` и добавьте в него описание SDN-подсети для вашего DHCP-адаптера. Пример:

   ```ini
   subnet: DHCP
       vnet DHCP
       dhcp-range start-address=10.10.10.11,end-address=10.10.10.149
       dhcp-dns-server 10.10.10.110
       gateway 10.10.10.1
       domain=example.local
       snat 1
   ```

   Здесь:
   - `subnet: DHCP` – имя подсети, оно должно совпадать с именем моста, указанного в конфигурации сетевого адаптера контейнера (bridge=DHCP).
   - Остальные параметры задают диапазон выдачи IP, шлюз, DNS-сервер и доменное имя.

2. **Проверьте настройки SDN в веб-интерфейсе**  
   Перейдите в раздел SDN и убедитесь, что зона (подсеть) с именем «DHCP» видна и активна, а опция DHCP включена для неё.

3. **Проверьте статус dnsmasq для SDN**  
   После создания конфигурации убедитесь, что для SDN-зоны запускается соответствующий сервис. Обычно имя сервиса выглядит так:
   
   ```bash
   systemctl status dnsmasq@DHCP.service
   ```
   
   Если сервис не запущен или завершается с ошибкой, попробуйте перезапустить его:
   
   ```bash
   systemctl restart dnsmasq@DHCP.service
   ```

4. **Настройте контейнер**  
   В конфигурационном файле контейнера (например, `/etc/pve/lxc/103.conf`) оставьте строку для второго адаптера, которая уже у вас выглядит примерно так:

   ```ini
   net1: name=dhcp,bridge=DHCP,firewall=1,hwaddr=BC:24:11:19:D5:6D,ip=dhcp,ip6=dhcp,type=veth
   ```

   Это позволит контейнеру при старте обратиться к SDN-зоне «DHCP».

5. **Перезапустите контейнер**  
   После внесения всех изменений попробуйте запустить контейнер:
   
   ```bash
   pct start 103 --debug
   ```

Если после этих шагов контейнер успешно запустится – значит, проблема заключалась в отсутствии корректно настроенной SDN-зоны и соответствующего dnsmasq-сервиса. Если же ошибка сохраняется, проверьте логи сервиса dnsmasq@DHCP и убедитесь, что настройки в файле `/etc/pve/sdn/subnets.cfg` корректны и совпадают с именем моста в конфигурации контейнера.

Таким образом, для восстановления второго адаптера с DHCP необходимо правильно настроить SDN-зону (подсеть) в Proxmox и убедиться, что dnsmasq для этой зоны работает корректно.

---

Ошибка "failed to bind DHCP server socket: Address already in use" означает, что dnsmasq@DHCP пытается занять порт (обычно 67 для DHCP), но этот порт уже используется другим процессом.

В случае использования SDN в Proxmox часто возникает конфликт между стандартным (глобальным) dnsmasq и экземпляром для SDN‑DHCP. Обычно Proxmox запускает стандартный dnsmasq, если в настройках не отключён DHCP на уровне узла.

Чтобы решить проблему и вернуть второй адаптер с DHCP, попробуйте следующие шаги:

1. **Проверьте, какой процесс занимает нужный порт (67 для DHCP)**  
   Выполните команду:  
   ```bash
   ss -ulpn | grep ':67'
   ```  
   Это покажет, какой процесс уже слушает этот порт.

2. **Остановите стандартный экземпляр dnsmasq (если он запущен)**  
   Если в выводе вы видите, что dnsmasq запущен как стандартная служба (например, dnsmasq.service), то его нужно остановить и отключить автозапуск:  
   ```bash
   systemctl stop dnsmasq.service
   systemctl disable dnsmasq.service
   ```  
   Это освободит порт, чтобы экземпляр для SDN (dnsmasq@DHCP.service) мог корректно запуститься.

3. **Перезапустите службу SDN DHCP**  
   После остановки конфликтующей службы выполните:  
   ```bash
   systemctl restart dnsmasq@DHCP.service
   ```  
   Проверьте статус:  
   ```bash
   systemctl status dnsmasq@DHCP.service
   ```  
   Если теперь служба запустилась успешно, ошибка должна исчезнуть.

4. **Проверьте конфигурацию SDN**  
   Убедитесь, что в файле `/etc/pve/sdn/subnets.cfg` для зоны, например, "DHCP", указаны корректные параметры (диапазон выдачи IP, шлюз, DNS‑сервер, домен) и IP-адреса не конфликтуют с другими интерфейсами узла.

5. **Перезапустите контейнер**  
   После того как dnsmasq@DHCP успешно запустился, попробуйте снова запустить контейнер:  
   ```bash
   pct start 103 --debug
   ```

Если после этих шагов dnsmasq@DHCP продолжает выдавать ошибку, проверьте вывод команды `ss -ulpn` ещё раз и убедитесь, что на нужном IP/порту больше не занят процессом. Возможно, потребуется проверить и изменить настройки в SDN-конфигурации, чтобы избежать конфликта с другими службами.

Попробуйте описанные действия и сообщите, если потребуется дополнительная помощь.
