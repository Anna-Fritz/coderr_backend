from rest_framework import serializers
from ..models import Offer, OfferDetail


class OfferSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    details = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name="offerdetails-detail")

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'user_details']
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

    def create(self, validated_data):
        user = self.context['request'].user  # Holt den aktuell eingeloggten Benutzer
        validated_data['user'] = user

        details_data = validated_data.pop('details')  # Holt die Details-Daten
        offer = Offer.objects.create(**validated_data)  # Erstellt das Angebot
        for detail in details_data:
            # Erstellt für jedes Detail einen OfferDetail-Eintrag
            OfferDetail.objects.create(offer=offer, **detail)
        # return offer

        return super().create(validated_data)

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details')  # Holt die Details-Daten
        instance = super().update(instance, validated_data)
        
        # Löscht alte OfferDetail und erstellt sie erneut
        instance.details.all().delete()
        for detail in details_data:
            OfferDetail.objects.create(offer=instance, **detail)
        
        return instance


class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']