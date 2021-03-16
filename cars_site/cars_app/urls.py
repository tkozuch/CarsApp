from django.urls import path

from . import views

# TODO: Make sure slashes will be correct with the task requirements
urlpatterns = [
    path('cars/', views.CarsView.as_view()),
    path('cars/<int:id>', views.CarsDeleteView.as_view()),
    path('rate/', views.RateView.as_view()),
    path('popular/', views.Popular.as_view())
]
