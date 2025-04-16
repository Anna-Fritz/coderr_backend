from rest_framework import viewsets
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


from ..models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewerOrBusinessUserOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Review objects. Supports listing, retrieving, creating,
    updating, and deleting reviews. Includes filtering by business_user and reviewer,
    as well as ordering by updated date or rating.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrBusinessUserOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def update(self, request, *args, **kwargs):
        """
        Handle partial or full updates of a review.
        Only the reviewer can update their own review, and only the rating and
        description fields are allowed to be modified.
        """
        partial = kwargs.pop('partial', False)  # check if request is PATCH
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
