from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from ..models import UserProfile
from .serializers import BusinessProfileSerializer, CustomerProfileSerializer


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    lookup_field = 'pk'

    def get_object(self):

        try:
            return UserProfile.objects.get(user_id=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise Response({'error': 'Der Benutzer wurde nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)

    def get_serializer_class(self):

        user_profile = self.get_object()

        if user_profile.type == 'business':
            return BusinessProfileSerializer
        return CustomerProfileSerializer


class BusinessProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = BusinessProfileSerializer


class CustomerProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = CustomerProfileSerializer
