from rest_framework import serializers
from django.contrib.auth.models import User
from profiles_app.models import BusinessProfile, CustomerProfile


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, data):
        pw = data['password']
        repeated_pw = data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'password': 'Passwörter stimmen nicht überein.'})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Ungültiger Username.'})

        return data

    def create(self, validated_data):
        type = validated_data['type']
        validated_data.pop('repeated_password')
        validated_data.pop('type')
        user = User.objects.create_user(**validated_data)

        if type == 'customer':
            CustomerProfile.objects.create(user=user)
        elif type == 'business':
            BusinessProfile.objects.create(user=user)

        return user

