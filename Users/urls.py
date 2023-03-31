from django.urls import path
from .views import login_request, logout_request

urlpatterns = [
    path('login/', login_request),
    path('logout/', logout_request)
]