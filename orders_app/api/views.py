from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import Order
from .serializers import OrderSerializer
from .permissions import IsCustomerOrAdminOrReadOnly


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerOrAdminOrReadOnly]
