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
    """
    ViewSet for managing orders. Supports CRUD operations for authenticated users.
    Customers and business users can interact with their respective orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerOrBusinessUserOrAdmin]

    def get_queryset(self):
        """
        Override the default queryset to filter orders based on the authenticated user.
        Returns orders related to the user, either as a customer or a business user.
        """
        queryset = super().get_queryset()

        if self.request.method == "GET":
            queryset = queryset.filter(
                Q(customer_user=self.request.user) | Q(business_user=self.request.user)
            )
        return queryset

    def update(self, request, *args, **kwargs):
        """
        Override the update method to handle partial updates (PATCH requests) for an order.
        This ensures that only valid fields (like `status`, `revisions`, etc.) can be updated.
        """
        partial = kwargs.pop('partial', False)  # check if request is PATCH
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class OrderCountView(APIView):
    """
    API View to get the count of orders in 'in_progress' status for a given business user.
    """
    def get(self, request, business_user_id):
        """
        Retrieve the count of orders that are 'in_progress' for a specific business user.
        The business user is identified by the `business_user_id` parameter.
        """
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
    """
    API View to get the count of completed orders for a given business user.
    """
    def get(self, request, business_user_id):
        """
        Retrieve the count of orders that are 'completed' for a specific business user.
        The business user is identified by the `business_user_id` parameter.
        """
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
