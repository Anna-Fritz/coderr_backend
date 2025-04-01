from rest_framework import viewsets, generics
from ..models import Offer, OfferDetail
from .serializers import OfferUpdateSerializer, OfferDetailSerializer, OfferListSerializer, OfferDetailViewSerializer, OfferCreateSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import LargeResultsSetPagination
from .filters import OfferFilter
from django.db.models import Min, Max


class OfferViewSet(viewsets.ModelViewSet):
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at']
    pagination_class = LargeResultsSetPagination
    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer

    def get_queryset(self):
        """
        Returns the filtered and annotated queryset for listing objects.
        Annotates the queryset with the minimum price and maximum delivery time.
        Applies filtering, searching, and ordering only for GET requests in the 'list' action.
        """
        queryset = super().get_queryset().annotate(min_price=Min("details__price"), max_delivery_time=Max("details__delivery_time_in_days"))
        if self.request.method == "GET" and self.action == 'list':
            filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
            for backend in filter_backends:
                queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OfferListSerializer  # GET /offers/
        if self.action == "retrieve":
            return OfferDetailViewSerializer  # GET /offers/{id}/
        if self.action == 'create':
            return OfferCreateSerializer  # POST /offers/
        return OfferUpdateSerializer  # PUT, PATCH  /offers/{id}/

    def create(self, request, *args, **kwargs):
        """
        Creates a new offer associated with the authenticated user.
        Validates request data, saves the offer, and returns the serialized response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save(user_id=request.user.id)
        response_serializer = OfferCreateSerializer(offer, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # check if request is PATCH
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class OfferDetailDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]
