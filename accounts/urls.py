from django.urls import path

from .views import LoginView, LogoutView, profile, register

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("me/", profile, name="profile"),
]


