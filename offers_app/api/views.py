from rest_framework import viewsets, generics
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer, OfferListSerializer, OfferDetailViewSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    # serializer_class = OfferSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OfferListSerializer  # GET /offers/
        if self.action == "retrieve":
            return OfferDetailViewSerializer  # GET /offers/{id}/
        return OfferSerializer  # POST, PUT, PATCH

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Erstellt ein neues Offer und gibt eine benutzerdefinierte Response zurück.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save(user=request.user)

        # Falls du eine detailliertere Response zurückgeben möchtest
        response_serializer = OfferSerializer(offer, context={"request": request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # Prüft, ob es ein PATCH ist
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class OfferDetailDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]
