from rest_framework import serializers
from profiles_app.models import UserProfile
from ..models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=[('customer', 'Customer'), ('business', 'Business')])

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
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)

        type = validated_data.get('type')  # Beispielweise aus den Request-Daten holen
        if type not in ['customer', 'business']:
            raise serializers.ValidationError({'type': 'Ungültiger Benutzertyp.'})

        profile = UserProfile.objects.create(user=user, type=type)

        return profile
