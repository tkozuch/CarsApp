import requests
from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.views import View

from .models import Car, Rate


class CarsView(View):
    VALIDATING_API = "https://vpic.nhtsa.dot.gov/api/"

    def get(self, request):
        cars_with_avg_rating = Car.objects.annotate(
            avg_rating=Avg("rate__rating")
        ).values("id", "make", "model", "avg_rating")

        # TODO: Check if JSON Response does have appropriate Content-type header by default
        return JsonResponse(list(cars_with_avg_rating), safe=False)

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
        cars_with_rates_number = Car.objects.annotate(rates_number=Count("rate")).values(
            "id", "make", "model", "rates_number"
        )

        return JsonResponse(
            sorted(cars_with_rates_number, key=lambda car: car["rates_number"], reverse=True),
            # From ECMA script 5 it shall be again safe to serialize and output
            # List objects this way.
            safe=False,
        )
