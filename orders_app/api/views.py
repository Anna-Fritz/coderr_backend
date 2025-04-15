from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.contrib.auth import get_user_model

from ..models import Order
from .serializers import OrderSerializer
from .permissions import IsCustomerOrBusinessUserOrAdmin


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerOrBusinessUserOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.method == "GET":
            queryset = queryset.filter(
                Q(customer_user=self.request.user) | Q(business_user=self.request.user)
            )
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # check if request is PATCH
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class OrderCountView(APIView):
    def get(self, request, business_user_id):
        try:
            user = get_user_model().objects.get(id=business_user_id, type="business")
        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "A business user with the provided ID could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )

        order_count = Order.objects.aggregate(
            order_count=Count("id", filter=Q(business_user=user.id, status="in_progress"))
        )
        return Response(order_count)


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        try:
            user = get_user_model().objects.get(id=business_user_id, type="business")
        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "A business user with the provided ID could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )
        completed_order_count = Order.objects.aggregate(
            completed_order_count=Count("id", filter=Q(business_user=user.id, status="completed"))
        )

        return Response(completed_order_count)
