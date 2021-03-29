import logging

import requests
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views import View

from .models import Car, Rate

log = logging.getLogger(__file__)


class CarsView(View):
    VALIDATING_API = "https://vpic.nhtsa.dot.gov/api/"

    def get(self, request):
        cars_with_avg_rating = Car.objects.annotate(
            avg_rating=Avg("rate__rating")
        ).values("id", "make", "model", "avg_rating")

        return JsonResponse(list(cars_with_avg_rating), safe=False)

    def post(self, request):
        make = request.POST["make"]
        model = request.POST["model"]
        if not self._check_car_exists(make, model):
            return HttpResponse(
                "The provided parameters do not match any real life cars.", status=422
            )

        else:
            _, created = Car.objects.get_or_create(make=make, model=model)
            if created:
                return HttpResponse(status=201)
            else:
                return HttpResponse(
                    "Car with this parameters already exists.",
                    status=409,
                )

    def _check_car_exists(self, make, model):
        try:
            response = requests.get(
                f"{self.VALIDATING_API}/vehicles/GetModelsForMake/{make}",
                params={"format": "json"},
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            log.exception(
                "External API signaled a problem. Check status code for further "
                "information. Aborting."
            )
        except requests.exceptions.RequestException:
            log.exception(
                "An exception occurred while making request to external API: {}. Aborting.".format(
                    self.VALIDATING_API
                )
            )
        else:
            all_make_models = response.json()[
                "Results"
            ]  # If the make does not exist we will get an empty list.

            make_exists = all_make_models != []
            model_exists = any(
                [result["Model_Name"] == model for result in all_make_models]
            )
            return make_exists and model_exists


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


class Popular(View):
    def get(self, request):
        cars_with_rates_number = Car.objects.annotate(rates_number=Count("rate")).values(
            "id", "make", "model", "rates_number"
        )

        return JsonResponse(
            sorted(
                cars_with_rates_number, key=lambda car: car["rates_number"], reverse=True
            ),
            safe=False,
        )
