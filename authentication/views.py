from django.shortcuts import render
from .helpers import error_response, success_response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import Profile
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return success_response(data={"username": user.username}, success_message="User registered successfully", status=status.HTTP_200_OK)
            return error_response(errors=serializer.errors, error_message="User registration failed", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(error_message=str(e))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            if not username or not password:
                return error_response(error_message="username and password required", status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)
            if user is None:
                return error_response(error_message="Invalid credentials", status=status.HTTP_401_UNAUTHORIZED)
            
            user_roles = Profile.objects.get(user=user).user_type
            
            refresh = RefreshToken.for_user(user)
            return success_response(data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_roles": user_roles
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return error_response(error_message=str(e))