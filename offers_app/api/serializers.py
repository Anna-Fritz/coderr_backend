from rest_framework import serializers
from ..models import Offer, OfferDetail
from rest_framework.reverse import reverse
from django.db.models import Min
import os


class OfferDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = "{:.2f}".format(instance.price)
        return data


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['price'] = "{:.2f}".format(instance.price)
        return data


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        details_data = validated_data.pop('details', None)
        offer = Offer.objects.create(**validated_data)

        if details_data:
            OfferDetail.objects.bulk_create([
                OfferDetail(offer=offer, **detail) for detail in details_data
            ])
        return offer

    def validate_image(self, value):
        """
        Validates that the uploaded image has an allowed extension (.jpg, .jpeg, .png).
        """
        if not value:
            return value
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value


class OfferUpdateSerializer(serializers.ModelSerializer):   # PUT / PATCH
    details = OfferDetailUpdateSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_image(self, value):
        """
        Validates that the uploaded image has an allowed extension (.jpg, .jpeg, .png).
        """
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value

    def validate_details(self, value):
        """Ensure that the details reference valid OfferDetail instances."""
        for detail in value:
            detail_id = detail.get('id')
            if detail_id:
                if not OfferDetail.objects.filter(id=detail_id).exists():
                    raise serializers.ValidationError(f"OfferDetail with id {detail_id} does not exist.")
            else:
                raise serializers.ValidationError("ID for OfferDetail must be provided.")
        return value

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image:
            instance.image = image
            instance.save()

        if details_data:
            for detail_data in details_data:
                detail_id = detail_data.get('id', None)
                if detail_id:
                    try:
                        detail_instance = OfferDetail.objects.get(id=detail_id)
                        detail_instance.title = detail_data.get('title')
                        detail_instance.revisions = detail_data.get('revisions')
                        detail_instance.delivery_time_in_days = detail_data.get('delivery_time_in_days')
                        detail_instance.price = detail_data.get('price')
                        detail_instance.features = detail_data.get('features')
                        detail_instance.save()
                    except OfferDetail.DoesNotExist:
                        raise serializers.ValidationError(f"OfferDetail with id {detail_id} does not exist.")
                else:
                    raise serializers.ValidationError("ID for OfferDetail must be provided.")
        return instance


class OfferDetailViewSerializer(serializers.ModelSerializer):   # GET Retrieve
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    def get_details(self, obj):
        request = self.context.get('request')
        return [
            {
                "id": detail.id,
                "url": request.build_absolute_uri(reverse("offerdetails-detail", args=[detail.id]))
            }
            for detail in obj.details.all()
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(Min("delivery_time_in_days"))["delivery_time_in_days__min"]


class OfferListSerializer(OfferDetailViewSerializer):  # GET List
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        extra_kwargs = {
            'user': {'read_only': True},
        }

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }
