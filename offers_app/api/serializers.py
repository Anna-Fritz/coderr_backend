from rest_framework import serializers
from ..models import Offer, OfferDetail
from rest_framework.reverse import reverse
from django.db.models import Min


class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferSerializer(serializers.ModelSerializer):   # POST / PUT
    # user_details = serializers.SerializerMethodField()
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user

        details_data = validated_data.pop('details', None)  # Holt die Details-Daten
        offer = Offer.objects.create(**validated_data)  # Erstellt das Angebot
        for detail in details_data:
            # Erstellt für jedes Detail einen OfferDetail-Eintrag
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

        # return super().create(validated_data)

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details')  # Holt die Details-Daten
        instance = super().update(instance, validated_data)

        # Löscht alte OfferDetail und erstellt sie erneut
        instance.details.all().delete()
        for detail in details_data:
            OfferDetail.objects.create(offer=instance, **detail)

        return instance


class OfferListSerializer(serializers.ModelSerializer):  # GET List
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

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

