# Музыкальный каталог

### Для установки проекта:

#### Если Docker не установлен, перейдите на [официальный сайт ](https://www.docker.com/products/docker-desktop) и скачайте установочный файл Docker Desktop для вашей операционной системы

### Клонируйте репрозиторий:
```
git@github.com:M4rk-er/music_catalog_test_task.git
``` 

### После клонирования репрозитория:

- Перейдите в директорию infra
``` 
cd music_service/infra 
```
- Создайте файл ``` .env ``` с данными:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432 
```
- Выполните команду для сборки и запуска контейнеров:
``` 
docker-compose up -d --build 
```

- Выполните миграции в контейнере:
``` 
docker-compose exec web python manage.py migrate 
```

- Собирите staticfiles:
``` 
docker-compose exec web python3 manage.py collectstatic --noinput 
```

### После запуска проект будет доступен по адресу localhost[localhost], [swagger](localhost/api/swagger), [API](localhost/api/)

### Основные функции приложения:
- Создание исполнителей:
``` (POST) /api/performers/ ```
```
{
    "name": "artist_1"
}
```
- Создание трека:
``` (POST) /api/tracks/ ```
```
{
    "title": "track_1",
    "author": {"id": 1},
    "album": {"id": 1}*
}
```
*-Album является не обязательным полем, при его указании трек сразу добавится в указанный альбом.

- Создание альбома
``` (POST) /api/albums/ ```
```
{
    "title": "album_1",
    "year_of_release": "2023-01-01",
    "tracks": [
        {"id": 1}
    ]
}
```

- Добавление треков в альбом
``` (POST) /api/albums/{id}/add_tracks/ ```
```
{
    "tracks": [
        1
    ]
}
```


