from django.urls import path
from .views import LoginView, RegistrationView

urlpatterns = [
    path('registration/', LoginView.as_view(), name='registration'),
    path('login/', RegistrationView.as_view(), name='login')
]
