from django.test import TestCase, Client


# Create your tests here.
class TestCarsView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = Client()

    def test_post_request(self):
        data = {
          "make": "Volkswagen",
          "model": "Golf",
        }
        self.client.post(
            'cars/', data=data
        )
