from django.urls import path
from . import views

app_name = "stocks"
urlpatterns = [

    # Regular URLs
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("users", views.users, name="users"),

    
    # API Routes
    path("API/set_sell_stock_price", views.set_sell_stock_price, name="set_stock_price"),

]