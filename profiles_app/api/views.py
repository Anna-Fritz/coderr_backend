from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework import status
from ..models import UserProfile
from .serializers import BusinessProfileSerializer, CustomerProfileSerializer, BusinessProfileListSerializer, CustomerProfileListSerializer
from .permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete user profiles. Only the profile owner or an admin can update or delete the profile."""

    queryset = UserProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'pk'

    def get_object(self):
        """
        Retrieve the UserProfile object based on the user ID in the URL.
        Raises NotFound error if the profile does not exist.
        """
        obj = get_object_or_404(UserProfile, user_id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        """
        Return the appropriate serializer based on the user profile's type.
        """
        user_profile = self.get_object()
        if user_profile.type == 'business':
            return BusinessProfileSerializer
        return CustomerProfileSerializer


class BusinessProfileListView(generics.ListAPIView):
    """Retrieve a list of all user profiles with 'business' type."""

    queryset = UserProfile.objects.filter(type='business')
    serializer_class = BusinessProfileListSerializer


class CustomerProfileListView(generics.ListAPIView):
    """Retrieve a list of all user profiles with 'customer' type."""

    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = CustomerProfileListSerializer
