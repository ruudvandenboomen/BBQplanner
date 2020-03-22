# BBQplanner
A Django webapp which makes it possible to organize BBQs with your friends!

## RUN
```sh
$ docker-compose up -d
# After the build finished run these commands to create database tables for your models
$ docker-compose run bbq-planner python manage.py makemigrations
$ docker-compose run bbq-planner python manage.py migrate
```

## TEST
```sh
$ docker-compose up -d
$ docker-compose run bbq-planner pytest
```