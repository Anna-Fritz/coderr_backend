from rest_framework import serializers
from ..models import UserProfile
import os


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'created_at', 'type', 'location', 'tel', 'description', 'working_hours', 'email']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.file:
            file_url = instance.file.url
            representation['file'] = file_url.replace("http://127.0.0.1:8000/", "media/")
        return representation

    def validate_file(self, value):
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.file = validated_data.get('file', instance.file)
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()

        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        return instance


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type', 'email', 'created_at']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.file:
            file_url = instance.file.url
            representation['file'] = file_url.replace("http://127.0.0.1:8000/", "media/")
        return representation

    def validate_file(self, value):
        valid_extensions = ['.jpg', '.jpeg', '.png']
        extension = os.path.splitext(value.name)[1].lower()
        if extension not in valid_extensions:
            raise serializers.ValidationError(f"Invalid file extension. Allowed extensions are {', '.join(valid_extensions)}.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.file = validated_data.get('file', instance.file)
        instance.save()

        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        return instance
