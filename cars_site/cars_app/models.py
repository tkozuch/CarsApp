from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Car(models.Model):
    make = models.CharField(max_length=30)
    model = models.CharField(max_length=30)


class Rate(models.Model):
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
