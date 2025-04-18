from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from ..models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for handling the creation and update of orders.
    It handles validation, creation, and update logic for the order model.
    """
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all(), write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Custom validation to ensure only allowed fields are present when creating an order.
        During POST requests, only 'offer_detail_id' is allowed in the request data.
        """
        request = self.context['request']
        if request and request.method == 'POST':
            allowed_fields = {'offer_detail_id'}
            unexpected_fields = set(self.initial_data.keys()) - allowed_fields
            if unexpected_fields:
                raise serializers.ValidationError({
                    "non_field_errors": [f"Only 'offer_detail_id' is allowed. Got extra fields: {', '.join(unexpected_fields)}."]
                })
        return attrs

    def create(self, validated_data):
        """
        Creates a new order based on the provided validated data.
        """
        request_user = self.context['request'].user
        if not request_user.is_authenticated:
            raise serializers.ValidationError({"user": "Authentication is required."})

        customer_user = get_object_or_404(get_user_model(), id=request_user.id)
        offer_detail_id = validated_data.pop('offer_detail_id')
        business_user = get_object_or_404(get_user_model(), id=offer_detail_id.offer.user.id)

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail_id.title,
            revisions=offer_detail_id.revisions,
            delivery_time_in_days=offer_detail_id.delivery_time_in_days,
            price=offer_detail_id.price,
            features=offer_detail_id.features,
            offer_type=offer_detail_id.offer_type,
            status="in_progress"
        )
        return order

    def update(self, instance, validated_data):
        """
        Override the update method to allow only the 'status' field to be updated.
        If other fields are provided, a validation error is raised.
        """
        if set(validated_data.keys()) != {"status"}:
            raise serializers.ValidationError("Only the 'status' field is allowed to be updated.")
        status = validated_data.pop('status', None)
        instance = super().update(instance, validated_data)
        if status:
            instance.status = status
            instance.save()
        return instance
