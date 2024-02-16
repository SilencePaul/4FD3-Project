## AERC Project Commands

- Updating model graph: `python manage.py graph_models -g aerc_website -o model.png`

## Setup

`pip install -r requirements.txt`

## Run Server

`python manage.py runserver`

## Directory Description

- Frontend staff like `.html` files in `templates` folder.
- Any static references like `.css`, `.jpg`, `.js` files in `static` folder.
- View controllers in `views.py` file. Use `request` parameter to know request header and params. Use `render` function to respond browser a web view that save in the `templates` folder.
- Route config in `urls.py` file. Map the route path to view controllers.

## Help Links

- https://www.w3schools.com/django/index.php
