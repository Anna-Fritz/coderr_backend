from .serializers import RegistrationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken


class LoginView(ObtainAuthToken):
    """
    The view validates the provided credentials and generates an authentication token if the login is successful.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles user authentication and token generation.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationView(APIView):
    """
    The view validates the input data, creates a new user and associated user profile, and returns a token 
    for the newly created user upon successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                saved_account = serializer.save()
                token, _ = Token.objects.get_or_create(user=saved_account.user)
                return Response({
                    'token': token.key,
                    'username': saved_account.user.username,
                    'email': saved_account.user.email,
                    'user_id': saved_account.user.id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
