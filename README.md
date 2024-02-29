## AERC Project Commands

- Updating model graph: `python manage.py graph_models -g aerc_website -o model.png`

## Setup

`pip install -r requirements.txt`
or
`python3.11 -m pip install -r requirements.txt`

## Change Admin Password

`python manage.py changepassword admin`

## Run Server

If you changed `models.py` file, run `python manage.py makemigrations` and `python manage.py migrate`.

`python manage.py runserver`

## Directory Description

- Frontend staff like `.html` files in `templates` folder.
- Any static references like `.css`, `.jpg`, `.js` files in `static` folder.
- View controllers in `views.py` file. Use `request` parameter to know request header and params. Use `render` function to respond browser a web view that save in the `templates` folder.
- Route config in `urls.py` file. Map the route path to view controllers.

## Management

- Development environment password `aerc_admin$2024`

## Help Links

- https://www.w3schools.com/django/index.php
