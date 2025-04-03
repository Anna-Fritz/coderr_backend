from rest_framework import serializers

from ..models import Order
from offers_app.models import OfferDetail
from profiles_app.models import UserProfile


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        customer_profile = UserProfile.objects.get(user_id=user.id)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError({"user": "Authentication is required."})
        if not customer_profile:
            raise serializers.ValidationError({"user": "UserProfile does not exist"})

        offer_detail_id = validated_data.pop('offer_detail_id', None)
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({"offer_detail_id": "OfferDetail with this ID does not exist."})
        business_user = offer_detail.offer.user
        business_user_profile = UserProfile.objects.get(user_id=business_user.id)

        order = Order.objects.create(
            customer_user=customer_profile,
            business_user=business_user_profile,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status="in_progress"
        )

        return order
