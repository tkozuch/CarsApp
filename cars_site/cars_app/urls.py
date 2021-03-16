from django.urls import path

from . import views

# TODO: Make sure slashes will be correct with the task requirements
urlpatterns = [
    path('cars/', views.Cars.as_view()),
    path('cars/<int:id>', views.CarsDelete.as_view()),
    path('rate/', views.Rate.as_view()),
    path('popular/', views.Popular.as_view())
]
