# BBQplanner
A Django webapp which makes it possible to organize BBQs with your friends!

## RUN
```sh
$ docker-compose up
# After the build finished run
$ docker-compose run bbq-planner python manage.py makemigrations
$ docker-compose run bbq-planner python manage.py migrate
```
