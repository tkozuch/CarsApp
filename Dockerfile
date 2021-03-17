FROM python:3.7

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/
WORKDIR /code/cars_site
RUN python manage.py migrate
