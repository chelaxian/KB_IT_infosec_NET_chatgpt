если такая ошибка:
```
root@:~# passwd
New password:
Retype new password:
passwd: Authentication token manipulation error
passwd: password unchanged
```

чиним так:
```
chown 0:0 /usr/bin/passwd
chmod 4755 /usr/bin/passwd

chown 0:42 /usr/sbin/unix_chkpwd
chmod 2755 /usr/sbin/unix_chkpwd

chown root:shadow /usr/sbin/unix_chkpwd
chmod 2755 /usr/sbin/unix_chkpwd
```

и вот результат
```
root@:~# passwd
New password:
Retype new password:
passwd: password updated successfully
```
