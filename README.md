# Cars API

## Getting started:

clone project:
`git clone https://github.com/tkozuch/NetGuruCars.git`

go to project folder:

`cd ./NetGuruCars`

## a) Getting started with Docker:

`docker-compose build`

`docker-compose up`


### Check if works:

In browser type:

http://127.0.0.1:8000/cars

This should return empty brackets in your top left corner directory: `[]`


### To run tests:

`docker-compose exec web python manage.py test`


## b) Getting started locally:

### (Optional) Make and activate virtual environment:

`python -m venv ./.venv`

Activate on Windows:
<br>`.\.venv\Scripts\activate`
<br>Activate on Linux-Ubuntu:
<br>`source ./bin/activate`

### Install python requirements

Open terminal in project folder and run:

```
pip install -r requirements.txt
```

### Apply migrations:

Go to site folder:
`cd ./cars_site`

Run:
`python manage.py migrate`

### Run application:

`python manage.py runserver`

### Check if works:

In browser type:

http://127.0.0.1:8000/cars

This should return empty brackets in your top left corner directory: `[]`


### To run tests:

From `NetGuruCars/cars_site` directory run: 

<br> `python manage.py test`
