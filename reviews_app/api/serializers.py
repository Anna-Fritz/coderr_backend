from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Handles creation and update of reviews, ensuring uniqueness and restricting
    updates to allowed fields only.
    """
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer']

    def validate(self, data):
        """
        Validates that a user cannot create multiple reviews for the same business user.
        Skips the check during updates.
        """
        user = self.context['request'].user
        business_user = data.get('business_user')
        if self.instance:
            return data
        if Review.objects.filter(business_user=business_user, reviewer=user).exists():
            raise serializers.ValidationError("You have already reviewed this business user.")
        return data

    def create(self, validated_data):
        """
        Creates a new Review instance using the authenticated user as the reviewer.
        """
        request_user = self.context['request'].user
        business_user = validated_data.pop('business_user')
        rating = validated_data.pop('rating')
        description = validated_data.pop('description')

        review = Review.objects.create(
            business_user=business_user,
            reviewer=request_user,
            rating=rating,
            description=description,
        )
        return review

    def update(self, instance, validated_data):
        """
        Updates the rating and/or description of a Review.
        Raises a ValidationError if any other fields are included in the update.
        """
        allowed_fields = {'rating', 'description'}
        invalid_fields = set(validated_data.keys()) - allowed_fields
        if invalid_fields:
            raise ValidationError(
                {"detail": f"Only 'rating' and 'description' can be updated. Invalid fields: {', '.join(invalid_fields)}"}
            )
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        return instance
