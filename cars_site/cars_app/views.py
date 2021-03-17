from statistics import mean

import requests
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views import View
from django.db.models import Avg

from .models import Car, Rate


class CarsView(View):
    VALIDATING_API = "https://vpic.nhtsa.dot.gov/api/"

    def get(self, request):
        cars = Car.objects.all()
        cars_list = []

        # TODO: Check if can be changed to more efficient querying:
        #  https://docs.djangoproject.com/en/3.1/topics/db/aggregation/
        #  https://books.agiliq.com/projects/django-orm-cookbook/en/latest/select_some_fields.html
        for car in cars:
            rates = car.rate_set.all()
            avg_rate = mean(rate.rating for rate in rates)

            cars_list.append(
                {
                    "id": car.id,
                    "make": car.make,
                    "model": car.model,
                    "avg_rating": avg_rate,
                }
            )

        # TODO: Check if JSON Response does have appropriate Content-type header by default
        return JsonResponse(cars_list, safe=False)

    def post(self, request):
        make = request.POST["make"]
        model = request.POST["model"]
        if not self._check_car_exists(make, model):
            return HttpResponse(
                "The provided parameters do not match any real life cars.", status=422
            )

        else:
            Car.objects.create(make=make, model=model)

        return HttpResponse(status=201)

    def _check_car_exists(self, make, model):
        all_make_models = requests.get(
            f"{self.VALIDATING_API}/vehicles/GetModelsForMake/{make}",
            params={"format": "json"},
        ).json()[
            "Results"
        ]  # Even with invalid make, the empty result and response 200 is returned

        car_exists = any([result["Model_Name"] == model for result in all_make_models])
        return car_exists


class CarsDeleteView(View):
    model = Car

    def delete(self, request, id):
        try:
            car = Car.objects.get(id=id)
        except Car.DoesNotExist:
            return HttpResponse(status=404)
        else:
            car.delete()
            return HttpResponse(status=204)


class RateView(View):
    def post(self, request):
        car_id = request.POST["car_id"]
        rating = request.POST["rating"]

        rate = Rate(car_id=car_id, rating=rating)
        try:
            rate.full_clean()
        except ValidationError:
            return HttpResponse(status=422)
        else:
            rate.save()
            return HttpResponse(status=201)


# TODO: How many "TOP" popular cars should be outputed?
class Popular(View):
    def get(self, request):
        # TODO: Change to more efficient querying:
        #  https://docs.djangoproject.com/en/3.1/topics/db/aggregation/
        #  https://books.agiliq.com/projects/django-orm-cookbook/en/latest/select_some_fields.html
        cars = Car.objects.all()

        output = [
            {
                "id": car.id,
                "make": car.make,
                "model": car.model,
                "rates_number": car.rate_set.count(),
            }
            for car in cars
        ]

        return JsonResponse(
            sorted(output, key=lambda car: car["rates_number"], reverse=True),
            # From ECMA script 5 it shall be again safe to serialize and output
            # List objects this way.
            safe=False,
        )
