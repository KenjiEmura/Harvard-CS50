from django.urls import path
from . import views

app_name = "stocks"
urlpatterns = [

    # Regular URLs
    path("", views.index, name="index"),

    # API Routes

]