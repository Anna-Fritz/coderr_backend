from django.urls import path, include
from .views import OfferDetailDetailView, OfferViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')

urlpatterns = [
    path('', include(router.urls)),
    path('offerdetails/<int:pk>/', OfferDetailDetailView.as_view(), name='offerdetails-detail'),
]
