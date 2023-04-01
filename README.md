# backend-services

Scripts used to power the Mumble public infrastructure backend (e.g. public server list)


## Development

Enter the Django project folder ``mumble_backend``. Call ``source setup``
to create a new venv which automatically installs Django and activates it.

Create the database tables with:
```
python manage.py migrate
```

Start the development server with:
```
python manage.py runserver
```

Run tests with:
```
python manage.py test
```

Create an admin account for the admin interface with:
```
python manage.py createsuperuser
```

Auto format code with:
```
black .
```

## Production

TBD