[![Foodgram-app Actions Status](https://github.com/vlad397/foodgram-project-react/workflows/Foodgram-app/badge.svg)](https://github.com/vlad397/foodgram-project-react/actions)

# FOODGRAM - продуктовый помощник

### Описание

Проект, который позволяет пользователям:

- `создавать` собственные рецепты, `просматривать` рецепты других пользователей;
- добавлять понравившиеся рецепты в `Избранное`;
- добавлять рецепты в `Список Покупок`;
- скачивать `PDF-файл` с необходимыми ингредиентами и их количеством;
- `просматривать` профили пользователей и `подписываться` на них;
- `фильтровать` рецепты по тегам.
### Запуск проекта
После клонирования репозитария перейдите в папку /backend/ и создайте там .env файл

Заполните его следующими данными:

- SECRET_KEY=любой секретный ключ на ваш выбор
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=пароль к базе данных на ваш выбор
- DB_HOST=bd
- DB_PORT=5432

Для установки Docker используйте команду `sudo apt install docker docker-compose`

Перейдите в папку /infra/ и выполните там следующие команды:

`sudo docker-compose up -d --build` *Для запуска сборки контейнеров*
`sudo docker-compose exec backend python manage.py makemigrations` *Для создания миграций*
`sudo docker-compose exec backend python manage.py migrate` *Для применения миграций*
`sudo docker-compose exec backend python manage.py load_data` *Для запуска заранее подготовленного скрипта по загрузке ингредиентов в базу*
`sudo docker-compose exec backend python manage.py createsuperuser` *Для создания суперпользователя*
`sudo docker-compose exec backend python manage.py collectstatic --no-input` *Для сбора статики*

### Информация об авторе и проекте

Проект выполнен студентом Яндекс Практикума в рамках обучения по программе:

Python-разработчик https://practicum.yandex.ru/backend-developer/

Для связи с автором: **v.butirsky@gmail.com**

Документация к проекту доступна по адресу http://84.252.138.253/api/docs/

Сам проект доступен по адресу http://84.252.138.253

Админка доступна по адресу http://84.252.138.253/admin/

Данные для админки: admin admin
