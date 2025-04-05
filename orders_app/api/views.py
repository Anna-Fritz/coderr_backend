from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q


from user_auth_app.models import CustomUser
from ..models import Order
from .serializers import OrderSerializer
from .permissions import IsUserTypeOrAdminOrReadOnly


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsUserTypeOrAdminOrReadOnly]

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
            user = CustomUser.objects.get(id=business_user_id, type="business")
        except CustomUser.DoesNotExist:
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
            user = CustomUser.objects.get(id=business_user_id, type="business")
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "A business user with the provided ID could not be found."},
                status=status.HTTP_404_NOT_FOUND
            )
        completed_order_count = Order.objects.aggregate(
            completed_order_count=Count("id", filter=Q(business_user=user.id, status="completed"))
        )

        return Response(completed_order_count)
