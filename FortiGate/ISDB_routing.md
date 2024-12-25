я ISDB использую как маршруты, работает

![image](https://github.com/user-attachments/assets/8bde5373-9f9b-42a1-9b01-91c4de71b8cf)
![image](https://github.com/user-attachments/assets/3829ab44-9951-46fc-9529-cbb6928785d6)
![image](https://github.com/user-attachments/assets/eb37a0b2-4522-47c2-9e47-bab24cc17573)
![image](https://github.com/user-attachments/assets/2ab1f1f3-91dc-4f27-94db-a36b3e926a10)

только без маршрутов по умолчанию не будет работать. нужно создать дубли дефолтроута для всех своих ВПН шлюзов с такой же АД и меньшим приоритетом, тогда заработает

https://community.fortinet.com/t5/FortiGate/Technical-Tip-ISDB-on-Policy-route/ta-p/295717

https://community.fortinet.com/t5/FortiGate/Technical-Tip-Creating-a-static-route-for-Predefined-Internet/ta-p/198756

![image](https://github.com/user-attachments/assets/2b12e2fe-d2e7-4d98-beba-bff9667fabbc)

Единственное они не будут отображаться в таблице маршрутизации и в трассировке не будет хопа в впн почему-то, будет выглядеть будто напрямую идет при трассировке. Но по факту все заработает и пойдет через впн.



