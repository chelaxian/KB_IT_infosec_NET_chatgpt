```conf
config system auto-script

edit "Tun1-Enable-Tun2-Disable"
set script "config router policy
edit 10
set status disable
next
edit 11
set status enable
end"

next

edit "Tun2-Enable-Tun1-Disable"
set script "config router policy
edit 10
set status enable
next
edit 11
set status disable
end"

next

edit "Enable-Both-Tunnels"
set script "config router policy
edit 10
set status enable
next
edit 11
set status enable
end"

next

end
```
