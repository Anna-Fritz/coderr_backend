from rest_framework import serializers
from ..models import UserProfile


class BusinessProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'created_at', 'type', 'location', 'tel', 'description', 'working_hours', 'email']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
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

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        return instance
