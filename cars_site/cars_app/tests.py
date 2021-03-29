from typing import Dict
from unittest.mock import patch

from django.test import Client, TestCase

from .models import Car, Rate


class TestCarsViewPost(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_returns_error_if_car_model_does_not_exist(self):
        data = {
            "make": "Volkswagen",
            "model": "XXX-non-existing-model",
        }
        with patch("cars_app.views.requests.get") as make_models_get:
            make_models_get.return_value.json.return_value = {
                "Results": [{"Model_Name": "Golf"}, {"Model_Name": "Passat"}]
            }

            response = self.client.post(
                "/cars/",
                data=data,
                headers={"Content-Type": "application/json;charset=UTF-8"},
            )

            self.assertEqual(response.status_code, 422)

    def test_returns_error_if_car_make_does_not_exist(self):
        data = {
            "make": "non-existing-make-name",
            "model": "Golf",
        }
        with patch("cars_app.views.requests.get") as make_models_get:
            make_models_get.return_value.json.return_value = {"Results": []}

            response = self.client.post(
                "/cars/",
                data=data,
                headers={"Content-Type": "application/json;charset=UTF-8"},
            )

            self.assertEqual(response.status_code, 422)

    def test_creates_car_when_it_exists(self):
        data = {
            "make": "Volkswagen",
            "model": "Golf",
        }
        with patch("cars_app.views.requests.get") as make_models_get:
            make_models_get.return_value.json.return_value = {
                "Results": [{"Model_Name": "Golf"}, {"Model_Name": "Passat"}]
            }
            cars = Car.objects.all()
            self.assertEqual(len(cars), 0)

            response = self.client.post(
                "/cars/",
                data=data,
                headers={"Content-Type": "application/json;charset=UTF-8"},
            )

            cars = Car.objects.all()
            self.assertEqual(len(cars), 1)

            car = cars[0]
            self.assertEqual(car.make, data["make"])
            self.assertEqual(car.model, data["model"])

            self.assertEqual(response.status_code, 201)

    def test_doesnt_create_second_car_if_it_was_already_created(self):
        data = {
            "make": "Volkswagen",
            "model": "Golf",
        }
        with patch("cars_app.views.requests.get") as make_models_get:
            Car.objects.create(make=data["make"], model=data["model"])

            make_models_get.return_value.json.return_value = {
                "Results": [{"Model_Name": "Golf"}, {"Model_Name": "Passat"}]
            }
            cars = Car.objects.all()
            self.assertEqual(len(cars), 1)

            response = self.client.post(
                "/cars/",
                data=data,
                headers={"Content-Type": "application/json;charset=UTF-8"},
            )

            cars = Car.objects.all()
            self.assertEqual(len(cars), 1)

            self.assertEqual(response.status_code, 409)


class TestCarsViewGet(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_returns_list_of_cars_if_they_were_created(self):
        Car.objects.bulk_create(
            [
                Car(make="Volvo", model="volvo-model-1"),
                Car(make="Volvo", model="volvo-model-2"),
                Car(make="Volvo", model="volvo-model-3"),
            ]
        )

        cars = Car.objects.all()

        Rate.objects.bulk_create(
            [
                Rate(car=cars[0], rating=2),
                Rate(car=cars[0], rating=4),
                Rate(car=cars[0], rating=3),
                Rate(car=cars[1], rating=1),
                Rate(car=cars[1], rating=1),
                Rate(car=cars[2], rating=5),
            ]
        )

        response = self.client.get(
            "/cars/", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        self.assertEqual(
            [
                {
                    "id": cars[0].id,
                    "make": "Volvo",
                    "model": "volvo-model-1",
                    "avg_rating": 3,
                },
                {
                    "id": cars[1].id,
                    "make": "Volvo",
                    "model": "volvo-model-2",
                    "avg_rating": 1,
                },
                {
                    "id": cars[2].id,
                    "make": "Volvo",
                    "model": "volvo-model-3",
                    "avg_rating": 5,
                },
            ],
            response.json(),
        )

    def test_returns_empty_list_if_no_cars_created(self):
        response = self.client.get(
            "/cars/", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        self.assertEqual([], response.json())


class TestCarsDeleteView(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_deletes_car_with_id_from_database(self):
        Car.objects.bulk_create(
            [Car(make="Volkswagen", model="Golf"), Car(make="Porshe", model="Cayenne")]
        )
        golf = Car.objects.get(model="Golf")

        response = self.client.delete(
            f"/cars/{golf.id}", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        cars = Car.objects.all()
        self.assertEqual(1, len(cars))

        the_only_existing_car = cars[0]
        self.assertEqual("Porshe", the_only_existing_car.make)
        self.assertEqual("Cayenne", the_only_existing_car.model)

        self.assertEqual(204, response.status_code)

    def test_returns_error_when_car_does_not_exist(self):
        Car.objects.bulk_create(
            [Car(make="Volkswagen", model="Golf"), Car(make="Porshe", model="Cayenne")]
        )
        non_existing_id = 999999999

        response = self.client.delete(
            f"/cars/{non_existing_id}",
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        cars = Car.objects.all()
        self.assertEqual(2, len(cars))

        self.assertEqual(404, response.status_code)


class TestRateView(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_creates_rate_object(self):
        car = Car.objects.create(make="Volkswagen", model="Golf")

        response = self.client.post(
            "/rate/",
            data={"car_id": car.id, "rating": 5},
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        rates = Rate.objects.all()
        self.assertEqual(1, len(rates))

        rate = rates[0]
        self.assertEqual(5, rate.rating)

        self.assertEqual(201, response.status_code)

    def test_returns_error_when_rate_bigger_then_5(self):
        car = Car.objects.create(make="Volkswagen", model="Golf")

        response = self.client.post(
            "/rate/",
            data={"car_id": car.id, "rating": 6},
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        self.assertEqual(422, response.status_code)

    def test_rate_not_created_when_rate_bigger_then_5(self):
        car = Car.objects.create(make="Volkswagen", model="Golf")

        self.client.post(
            "/rate/",
            data={"car_id": car.id, "rating": 6},
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        self.assertEqual(0, len(Rate.objects.all()))

    def test_returns_error_when_rate_smaller_then_1(self):
        car = Car.objects.create(make="Volkswagen", model="Golf")

        response = self.client.post(
            "/rate/",
            data={"car_id": car.id, "rating": 0},
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        self.assertEqual(422, response.status_code)

    def test_rate_not_created_when_rate_smaller_then_1(self):
        car = Car.objects.create(make="Volkswagen", model="Golf")

        self.client.post(
            "/rate/",
            data={"car_id": car.id, "rating": 0},
            headers={"Content-Type": "application/json;charset=UTF-8"},
        )

        self.assertEqual(0, len(Rate.objects.all()))


class TestPopularView(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_returns_items_sorted_by_rates_number(self):
        Car.objects.bulk_create(
            [
                Car(make="Volvo", model="volvo-model-1"),
                Car(make="Volvo", model="volvo-model-2"),
                Car(make="Volvo", model="volvo-model-3"),
                Car(make="Volvo", model="volvo-model-4"),
                Car(make="Honda", model="honda-model-1"),
                Car(make="Honda", model="honda-model-2"),
                Car(make="Honda", model="honda-model-3"),
                Car(make="Honda", model="honda-model-4"),
            ]
        )

        # Need to be fetched here to be retrieved with IDs.
        cars = Car.objects.all()

        number_of_rates = {
            cars[0].id: 10,
            cars[1].id: 2,
            cars[2].id: 0,
            cars[3].id: 100,
            cars[4].id: 100,
            cars[5].id: 6,
            cars[6].id: 99,
            cars[7].id: 12,
        }
        self._rate_cars(number_of_rates)

        response = self.client.get(
            "/popular/", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        self.assertEqual(
            [
                {
                    "id": cars[3].id,
                    "make": cars[3].make,
                    "model": cars[3].model,
                    "rates_number": 100,
                },
                {
                    "id": cars[4].id,
                    "make": cars[4].make,
                    "model": cars[4].model,
                    "rates_number": 100,
                },
                {
                    "id": cars[6].id,
                    "make": cars[6].make,
                    "model": cars[6].model,
                    "rates_number": 99,
                },
                {
                    "id": cars[7].id,
                    "make": cars[7].make,
                    "model": cars[7].model,
                    "rates_number": 12,
                },
                {
                    "id": cars[0].id,
                    "make": cars[0].make,
                    "model": cars[0].model,
                    "rates_number": 10,
                },
                {
                    "id": cars[5].id,
                    "make": cars[5].make,
                    "model": cars[5].model,
                    "rates_number": 6,
                },
                {
                    "id": cars[1].id,
                    "make": cars[1].make,
                    "model": cars[1].model,
                    "rates_number": 2,
                },
                {
                    "id": cars[2].id,
                    "make": cars[2].make,
                    "model": cars[2].model,
                    "rates_number": 0,
                },
            ],
            response.json(),
        )

    def test_returns_empty_list_if_no_cars_were_created(self):
        response = self.client.get(
            "/popular/", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        self.assertEqual([], response.json())

    def test_returns_list_with_empty_rates_numbers_if_no_rates_were_posted(self):
        Car.objects.bulk_create(
            [
                Car(make="Volvo", model="volvo-model-1"),
                Car(make="Volvo", model="volvo-model-2"),
                Car(make="Volvo", model="volvo-model-3"),
            ]
        )

        cars = Car.objects.all()

        response = self.client.get(
            "/popular/", headers={"Content-Type": "application/json;charset=UTF-8"}
        )

        self.assertEqual(
            [
                {
                    "id": cars[0].id,
                    "make": cars[0].make,
                    "model": cars[0].model,
                    "rates_number": 0,
                },
                {
                    "id": cars[1].id,
                    "make": cars[1].make,
                    "model": cars[1].model,
                    "rates_number": 0,
                },
                {
                    "id": cars[2].id,
                    "make": cars[2].make,
                    "model": cars[2].model,
                    "rates_number": 0,
                },
            ],
            response.json(),
        )

    @staticmethod
    def _rate_cars(number_of_rates: Dict[int, int]):
        for car_id, rates_count in number_of_rates.items():
            # Create this number of rates for the given Car.
            for _ in range(rates_count):
                Rate.objects.create(car_id=car_id, rating=5)


class TestCarsPostGetDeleteIntegration(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_all_operations_integrate_well_with_one_another(self):
        get_response_1 = self.client.get("/cars/")

        self.assertEqual(200, get_response_1.status_code)
        self.assertEqual([], get_response_1.json())

        post_response_1 = self.client.post(
            "/cars/",
            data={
                "make": "Volkswagen",
                "model": "Golf",
            }
        )
        post_response_2 = self.client.post(
            "/cars/",
            data={
                "make": "Volkswagen",
                "model": "Passat",
            }
        )
        self.assertEqual(201, post_response_1.status_code)
        self.assertEqual(201, post_response_2.status_code)

        get_response_2 = self.client.get("/cars/")
        self.assertEqual(200, get_response_2.status_code)
        self.assertEqual(2, len(get_response_2.json()))

        car = get_response_2.json()[0]

        self.client.delete(
            f"/cars/{car['id']}"
        )

        get_response_3 = self.client.get("/cars/")
        self.assertEqual(1, len(get_response_3.json()))


# More integrations tests could be done.
