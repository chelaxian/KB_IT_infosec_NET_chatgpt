Чтобы удалить все данные в Docker — включая все контейнеры, образы, сети и другие объекты — вам нужно выполнить несколько команд. Я приведу команды для каждой категории Docker-объектов.

### Удаление всех контейнеров

Сначала остановим и удалим все контейнеры:

1. Остановить все контейнеры:

```sh
docker stop $(docker ps -aq)
```

2. Удалить все контейнеры:

```sh
docker rm $(docker ps -aq)
```

### Удаление всех образов

Удалим все Docker-образы:

```sh
docker rmi $(docker images -q)
```

### Удаление всех сетей

Удалим все пользовательские Docker-сети (по умолчанию `bridge`, `host`, `none` не удаляются):

```sh
docker network rm $(docker network ls -q)
```

### Удаление всех объемов (volumes)

Удалим все Docker-тома:

```sh
docker volume rm $(docker volume ls -q)
```

### Полное удаление всех данных Docker

Вместо выполнения всех этих команд по отдельности можно использовать команду `docker system prune`, которая удалит все неиспользуемые объекты Docker. Чтобы полностью очистить все данные, включая остановленные контейнеры, образы, тома и сети, используйте:

```sh
docker system prune -a --volumes
```

- `-a` — удаляет все образы, включая неиспользуемые.
- `--volumes` — удаляет все тома.

### Примечание

Эти команды **безвозвратно** удалят все данные в Docker. Убедитесь, что у вас есть резервные копии или что вам действительно не нужны текущие данные перед выполнением этих команд.