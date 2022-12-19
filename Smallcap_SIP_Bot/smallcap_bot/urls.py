from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register),
    path('update/', update_user_preference),
    path('login/',login),
    path('forgot-password/',password_reset),
    path('change-password/',change_password),
    path('latest-relative-value/',latest_relative_value),
    path('relative-values/',get_relative_values)
]