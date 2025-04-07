from rest_framework.views import APIView
from django.db.models import Count, Q, Avg
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from reviews_app.models import Review
from user_auth_app.models import CustomUser
from offers_app.models import Offer


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.aggregate(review_count=Count("id"))['review_count']
        average_rating = Review.objects.aggregate(average_rating=Avg('rating'))['average_rating']
        average_rating = "{:.1f}".format(average_rating or 0.0)
        print(average_rating)
        business_profile_count = CustomUser.objects.aggregate(business_profile_count=Count("id", filter=Q(type="business")))['business_profile_count']
        offer_count = Offer.objects.aggregate(offer_count=Count("id"))['offer_count']

        return Response({
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        })
