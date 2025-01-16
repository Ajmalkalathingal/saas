from django.urls import path,include
from authuser.views import login_view



urlpatterns = [
    path('login', login_view),
]
