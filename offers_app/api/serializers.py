from rest_framework import serializers
from ..models import Offer, OfferDetail
from rest_framework.reverse import reverse
from django.db.models import Min
import os


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for representing an `OfferDetail` instance.
    Converts the model fields into a JSON-compatible format.
    """
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def to_representation(self, instance):
        """
        Customize the representation of the `OfferDetail` instance.
        """
        data = super().to_representation(instance)
        data['price'] = "{:.2f}".format(instance.price)
        return data


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an `OfferDetail` instance. It allows the user to modify the fields 
    of an existing `OfferDetail` object.
    """
    # id = serializers.IntegerField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

    def to_representation(self, instance):
        """
        Customize the representation of the `OfferDetail` instance.
        """
        data = super().to_representation(instance)
        data['price'] = "{:.2f}".format(instance.price)
        return data


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new `Offer` instance, including its associated `OfferDetail` instances.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        """
        Creates a new `Offer` and associated `OfferDetail` instances.
        """
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
    """
    Serializer for updating an existing `Offer` instance, including its associated `OfferDetail` instances.
    """
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
        offer_id = self.instance.id if self.instance else None
        for detail in value:
            detail_offer_type = detail.get('offer_type')
            if detail_offer_type:
                if not OfferDetail.objects.filter(offer=offer_id, offer_type=detail_offer_type).exists():
                    raise serializers.ValidationError({"details": "OfferDetail does not exist."})
            else:
                raise serializers.ValidationError({"details": "Offer_type for OfferDetail must be provided."})
        return value

    def update(self, instance, validated_data):
        """
        Updates an existing `Offer` instance and its associated `OfferDetail` instances.
        """
        details_data = validated_data.pop('details', None)
        image = validated_data.pop('image', None)
        instance = super().update(instance, validated_data)

        if image:
            instance.image = image
            instance.save()

        if details_data:
            for detail_data in details_data:
                detail_offer_type = detail_data.get('offer_type', None)
                if detail_offer_type:
                    try:
                        detail_instance = OfferDetail.objects.get(offer=instance, offer_type=detail_offer_type)
                        detail_instance.title = detail_data.get('title')
                        detail_instance.revisions = detail_data.get('revisions')
                        detail_instance.delivery_time_in_days = detail_data.get('delivery_time_in_days')
                        detail_instance.price = detail_data.get('price')
                        detail_instance.features = detail_data.get('features')
                        detail_instance.save()
                    except OfferDetail.DoesNotExist:
                        raise serializers.ValidationError({"details": "OfferDetail does not exist."})
                else:
                    raise serializers.ValidationError({"details": "Offer_type for OfferDetail must be provided."})
        return instance


class OfferDetailViewSerializer(serializers.ModelSerializer):   # GET Retrieve
    """
    Serializer for representing an `Offer` with its related `OfferDetail` instances for the "retrieve" action.
    Includes additional fields for the minimum price and minimum delivery time across all `OfferDetail` instances.
    """
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    def get_details(self, obj):
        """
        Retrieves the related `OfferDetail` instances for the offer and returns their URLs.
        """
        request = self.context.get('request')
        return [
            {
                "id": detail.id,
                "url": request.build_absolute_uri(reverse("offerdetails-detail", args=[detail.id]))
            }
            for detail in obj.details.all()
        ]

    def get_min_price(self, obj):
        """
        Retrieves the minimum price from the related `OfferDetail` instances.
        """
        return obj.details.aggregate(Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        """
        Retrieves the minimum delivery time from the related `OfferDetail` instances.
        """
        return obj.details.aggregate(Min("delivery_time_in_days"))["delivery_time_in_days__min"]


class OfferListSerializer(OfferDetailViewSerializer):  # GET List
    """
    Serializer for representing a list of `Offer` instances. Inherits from `OfferDetailViewSerializer`
    but includes additional user details for each offer.
    """
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
