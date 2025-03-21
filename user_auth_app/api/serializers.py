from rest_framework import serializers
from profiles_app.models import BusinessProfile, CustomerProfile, CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }

    def validate(self, data):
        pw = data['password']
        repeated_pw = data['repeated_password']

        if pw != repeated_pw:
            raise serializers.ValidationError({'password': 'Passwörter stimmen nicht überein.'})

        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Ungültiger Username.'})

        return data

    def create(self, validated_data):
        print(validated_data)
        type = validated_data['type']
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)

        self.create_user_profile(user, type)

        return user

    def create_user_profile(self, user, type):
        if type == 'customer':
            return CustomerProfile.objects.create(user=user)
        elif type == 'business':
            return BusinessProfile.objects.create(user=user)
        else:
            raise serializers.ValidationError({'detail': 'Ungültiger Benutzertyp.'})
