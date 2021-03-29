# Cars API

## Usage:

For testing, the deployed version of app is available here on Heroku: https://ng-cars.herokuapp.com/
Example endpoint: https://ng-cars.herokuapp.com/cars/


### Endpoints:

create new car:
<br>
```
POST /cars: 

form-data:

{
  "make" : "Volkswagen",
  "model" : "Golf",
}
```

delete car:
<br>

`DELETE /cars/{id}`

rate car:
<br>

```
POST /rate

form-data:
{
  "car_id" : 1,
  "rating" : 5,
}
```

get all created cars:
<br>
`GET /cars`

get top popular cars present in the DB (based on number of rates):
<br>
`GET /popular`

### Postman:
The postman collection can be fetched from the link:
https://www.getpostman.com/collections/bf016d91c7f468bc69ea

(Postman: Import -> Import from link)

## Getting started:

clone project:
`git clone https://github.com/tkozuch/CarsApp.git` 
go to project folder:

`cd ./CarsApp`

## a) Getting started with Docker:

`cp .env.sample .env`

`docker-compose build`

`docker-compose up`

(CTR+C to stop and exit)

### Check if works:

In browser type:

http://127.0.0.1:8000/cars

This should return empty brackets in your top left corner directory: `[]`


### To run tests:

(From another terminal when the project is running) Run:

`docker-compose exec web python manage.py test`


## b) Getting started by hand:

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

### Set environment variables:
(example values can be found in .env.sample file)

If working from Windows command prompt, then run:
`SET SECRET_KEY=<your secret key>`

Bash based command prompts:
`EXPORT SECRET_KEY=<your secret key>`

Secret key is any string of your choice. It will be used for security matters, so it's better to
 choose secure one and keep it private.

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

From the outer `cars_site` directory run: 

<br> `python manage.py test`
