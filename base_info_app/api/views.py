from rest_framework.views import APIView
from django.db.models import Count, Q, Avg
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from reviews_app.models import Review
from offers_app.models import Offer


class BaseInfoView(APIView):
    """
    View that provides basic business statistics such as review count, 
    average rating, business profile count, and offer count.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Returns the aggregated business statistics data.
        """
        review_count = Review.objects.aggregate(review_count=Count("id"))['review_count']
        average_rating = Review.objects.aggregate(average_rating=Avg('rating'))['average_rating']
        average_rating = "{:.1f}".format(average_rating or 0.0)
        business_profile_count = get_user_model().objects.aggregate(business_profile_count=Count("id", filter=Q(type="business")))['business_profile_count']
        offer_count = Offer.objects.aggregate(offer_count=Count("id"))['offer_count']

        return Response({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        })
