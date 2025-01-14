```
chown root:root /etc/sudo.conf /usr/bin/sudo
chmod 644 /etc/sudo.conf
chmod 4755 /usr/bin/sudo

chown root:root /usr/libexec/sudo/sudoers.so
chmod 644 /usr/libexec/sudo/sudoers.so

chown root:root /etc/sudoers
chmod 440 /etc/sudoers

chown root:root /etc/sudoers.d/90-incus /etc/sudoers.d/README
chmod 644 /etc/sudoers.d/90-incus /etc/sudoers.d/README

chown root:root /etc/sudoers.d
chmod 755 /etc/sudoers.d
```
