from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from CuratorBackend.serializers import UserSerializer
from curator.models import User


class UserSignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registration for users
        """
        try:
            user = User.objects.create_user(**request.data)
            access = AccessToken.for_user(user)
            refresh = RefreshToken.for_user(user)
            return Response(data=(dict(UserSerializer(user).data) | {'access': str(access),
                                                                     'refresh': str(refresh)
                                                                     }))
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
