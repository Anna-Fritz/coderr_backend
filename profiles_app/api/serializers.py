from rest_framework import serializers
from ..models import CustomerProfile, BusinessProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.CharField(source='user.email')
    type = serializers.CharField(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        if 'email' in user_data:
            instance.user.email = user_data['email']

        instance.user.save()

        return super().update(instance, validated_data)

    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError({'detail': '"Datei ist zu groß. Maximal 5 MB erlaubt.'})
        return value


class BusinessProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.CharField(source='user.email')

    type = serializers.CharField(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type']
        extra_kwargs = {
            'file': {'required': False},
            'uploaded_at': {'required': False},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            instance.user.last_name = user_data['last_name']
        if 'email' in user_data:
            instance.user.email = user_data['email']

        instance.user.save()

        return super().update(instance, validated_data)

    def validate_file(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError({'detail': '"Datei ist zu groß. Maximal 5 MB erlaubt.'})
        return value

