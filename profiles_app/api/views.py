from rest_framework import generics


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    pass


class BusinessProfileListView(generics.ListAPIView):
    pass


class CustomerProfileListView(generics.ListAPIView):
    pass
