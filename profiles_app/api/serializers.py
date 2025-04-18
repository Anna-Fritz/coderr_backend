from rest_framework import serializers
from ..models import UserProfile
import os
from user_auth_app.api.serializers import CustomUserSerializer


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
    Handles validation, representation, and updating of business-related profile information.
    """
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'created_at', 'type', 'location', 'tel', 'description', 'working_hours', 'email']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def to_representation(self, instance):
        """
        Customizes the representation of the profile to provide a file URL without the base URL.
        """
        representation = super().to_representation(instance)

        if instance.file:
            file_url = instance.file.url
            representation['file'] = file_url.replace("http://127.0.0.1:8000/", "media/")
        return representation

    def validate_file(self, value):
        """
        Validates that the uploaded file has an allowed extension (.jpg, .jpeg, .png).
        """
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value

    def update(self, instance, validated_data):
        """
        Updates the UserProfile instance with the validated data and updates the associated User instance.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.file = validated_data.get('file', instance.file)
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()
        return instance


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """
    Handles validation, representation, and updating of business-related profile information.
    """
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'created_at', 'type', 'location', 'tel', 'description', 'working_hours', 'email']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Handles validation, representation, and updating of customer-related profile information.
    """
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type', 'email', 'created_at']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def to_representation(self, instance):
        """
        Customizes the representation of the profile to provide a file URL without the base URL.
        """
        representation = super().to_representation(instance)

        if instance.file:
            file_url = instance.file.url
            representation['file'] = file_url.replace("http://127.0.0.1:8000", "media/")
        return representation

    def validate_file(self, value):
        """
        Validates that the uploaded file has an allowed extension (.jpg, .jpeg, .png).
        """
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value

    def update(self, instance, validated_data):
        """
        Updates the UserProfile instance with the validated data and updates the associated User instance.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.file = validated_data.get('file', instance.file)
        instance.save()
        return instance


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """
    Handles validation, representation, and updating of customer-related profile information.
    """
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type', 'email', 'created_at']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }
