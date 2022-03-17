# README
- Copy `backend.prod.env.example` and `database.prod.env.example` to `backend.prod.env` and `database.prod.env` and fill in appropriate values
- Run `./deploy.sh` (uses Docker) and visit `http://localhost:8000/`


## Docker
### Development
- Build images and run containers
`docker-compose -f docker-compose.dev.yml up --build`
- Start previously built containers in background
`docker-compose start`
- Apply migrations
`docker exec backend python3 manage.py migrate`
- Collect static files
`docker exec backend python3 manage.py collectstatic`
- Load test data:
`docker exec backend python3 manage.py loaddata fixture.json`

File changes in python files trigger an auto-reload of the server.
Migrations have to be executed with `docker exec backend python3 manage.py migrate`.

After changes to the Docker configuration, you have to restart and build the containers with `docker-compose -f docker-compose.dev.yml up --build`.

In order to run pre-commit checks every time, please run `pre-commit install` once in the repository. Pay attention when using `git commit -a`, because then the automatic code formatting will be added irreversably to your changes. The recommended workflow would be to use `git add` first, resulting in staged changes and unstaged codeformatting that you can double-check if you wish. You can of course always run `pre-commit run` to manually check all staged files before attempting a commit.

### Production

## Reverse Proxy

We recommend running the gunicorn server behind a reverse proxy to provide ssl and possibly run multiple services on one server.
The default configuration will make the docker container reachable on port 8000 only on 127.0.0.1.

A sample nginx configuration can be found at ./tools/nginx-sample-site.

## Setup
Set `SECRET_KEY`, `SENDGRID_API_KEY` and `MAPBOX_TOKEN`in `backend.prod.env` for Django
`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`  inside `database.prod.env` for postgres on your host machine.
Also add a `SLACK_LOG_WEBHOOK` to enable slack logging.

To run a container in production and in a new environment execute the `deploy.sh` script which builds the containers, runs all configurations and starts the web service.

If you want to deploy manually follow these steps closly:

1. Build the containers
(Run `export CURRENT_UID=$(id -u):$(id -g)` if you want to run the backend as non-root)
`docker-compose -f docker-compose.dev.yml -f docker-compose.prod.yml up -d --build`
2. Make messages
`docker exec --env PYTHONPATH="/match4crisis-backend:$PYTHONPATH" backend django-admin makemessages --no-location`
3. Compile messages
`docker exec --env PYTHONPATH="/match4crisis-backend:$PYTHONPATH" backend django-admin compilemessages`
4. Collect static
`docker exec backend python3 manage.py collectstatic --no-input`
5. Migrate
`docker exec backend python3 manage.py migrate`
5. Check if all the variables are correct
`docker exec backend python3 manage.py check`
6. Restart the backend container (important, whitenoise does not reload static files after it has started)
`docker-compose -f docker-compose.dev.yml -f docker-compose.prod.yml down && docker-compose -f docker-compose.dev.yml -f docker-compose.prod.yml up -d`

## Local
- create migration after model change:
`python3 manage.py makemigrations`

- migrate to current version:
`python3 manage.py migrate`

- dump current database into fixture file (override fixture file):
`python3 manage.py dumpdata > fixture.json`

- load test data:
`python3 manage.py loaddata fixture.json`

- create superuser (to access staff page)
`python3 manage.py createsuperuser`

## Translation
- Add translatable strings in python with `_("Welcome to my site.")` and import `from django.utils.translation import gettext as _` ([Documentation](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-python-code))
- Add translatable strings in templates with `{% blocktrans %}This string will have {{ value }} inside.{% endblocktrans %}` or alternatively with the `trans` block and include `{% load i18n %}` at the top ([Documentation](https://docs.djangoproject.com/en/3.0/topics/i18n/translation/#internationalization-in-template-code))
- Update the translation file
`django-admin makemessages -l en --no-location`
- Edit translations in `backend/locale/en/LC_MESSAGES/django.po`

## Testing

For executing the tests use `python3 manage.py test`.

In case you add more required environment variables for productions, please check for their existance in `backend/apps/checks.py`.

## Logging

Logging should always use the following pattern if possible:

```
import logging
logger = logging.getLogger(__name__)
logger.info('message',extra={ 'request': request })
```

If the request is not logged as an extra parameter, the log entry will **NOT** be messaged to slack!

Adding the request as extra parameter will automatically extract logged on user information as well as POST variables and take care of removing sensitive information from
the logs, respecting the @method_decorator(sensitive_post_parameters()). For example in user sign in, this will prevent logging of passwords.

**Warning:** Special care must be taken to avoid errors from circular references. The extra parameters are written to the log file and serialized as JSON. Circular references will cause
logging failure. One example would be adding the student to the extra dict:

Student has an attribute for the user, user has an attribute for the student, ...

These circular references will prevent the log entry from being written.
Including request is always safe, because the logging formatter contains dedicated code for request logging.

## Creating fake data
You can create and delete random fake students and hospitals using `manage.py createfakeusers --add-students 1000 --add-hospitals 50`. Use the `--help` flag to check out all the options. For creating a staff user, please use the builtin `createsuperuser` command.

## Forks
Thanks for forking our repository. Pay attention that Travis CI doesn't test your code with sendgrid.
If you want to use sendgrid for your tests, add your repository name to the list in the if statement for NOT_FORK in `backend/match4crisis/settings/production.py` and specify the `SENDGRID_API_KEY` environment variable in the Travis run settings.
