from rest_framework import generics
from ..models import BusinessProfile, CustomerProfile
from .serializers import CustomerProfileSerializer, BusinessProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BusinessProfile.objects.all()
    lookup_field = 'pk'

    def get_object(self):

        try:
            return BusinessProfile.objects.get(pk=self.kwargs['pk'])
        except BusinessProfile.DoesNotExist:
            return CustomerProfile.objects.get(pk=self.kwargs['pk'])

    def get_serializer_class(self):
        profile = self.get_object()

        if profile.type == 'business':
            return BusinessProfileSerializer
        return CustomerProfileSerializer


class BusinessProfileListView(generics.ListAPIView):
    queryset = BusinessProfile.objects.select_related('user').all()
    serializer_class = BusinessProfileSerializer


class CustomerProfileListView(generics.ListAPIView):
    queryset = CustomerProfile.objects.select_related('user').all()
    serializer_class = CustomerProfileSerializer
