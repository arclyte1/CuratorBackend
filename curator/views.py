from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from curator.email_confirmation import send_code, verify_code
from curator.models import User, Event, Group, Request
from curator.serializers import UserSerializer, EventSerializer, GroupSerializer, RequestSerializer


class UserSendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if 'email' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        res = send_code(request.data['email'])
        if res:
            return Response(res, status=status.HTTP_200_OK)
        else:
            return Response(res, status=status.HTTP_202_ACCEPTED)


class UserVerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registration for users
        """
        try:
            res = verify_code(request.data["email"], request.data["code"])
            if res:
                if User.objects.filter(email=request.data["email"]).exists():
                    user = User.objects.get(email=request.data["email"])
                else:
                    user = User.objects.create_user(email=request.data["email"])
                access = AccessToken.for_user(user)
                refresh = RefreshToken.for_user(user)
                return Response(data=(dict(UserSerializer(user).data) | {'access': str(access),
                                                                         'refresh': str(refresh)
                                                                         }))
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
    def get(self, request):
        data = GroupSerializer(request.user.groups.all(), many=True).data
        return Response(data=data)


class EventView(APIView):
    def get(self, request):
        data = EventSerializer(Event.objects.filter(groups__curators=request.user).distinct(), many=True).data
        return Response(data=data)

    def post(self, request):
        if ('title' not in request.data or 'groups' not in request.data or
                any(not isinstance(g, int) for g in request.data['groups'])
                or not request.data['groups']):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request.data['groups'] = list(set(request.data['groups']))

        if not request.user.groups.filter(id__in=request.data['groups']).count() == len(request.data['groups']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            event_data = {
                'title': request.data['title'],
                'type': request.data.get('type'),
                'date': request.data.get('date'),
                'start_time': request.data.get('start_time'),
                'end_time': request.data.get('end_time'),
                'location': request.data.get('location'),
                'cloud_url': request.data.get('cloud_url')
            }

            event = Event.objects.create(**event_data)
            event.groups.set(Group.objects.filter(id__in=request.data['groups']))
            data = EventSerializer(event).data
            return Response(data=data)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class EventDetailsView(APIView):
    def get(self, request, event_id):
        try:
            data = EventSerializer(
                Event.objects.filter(groups__curators=request.user, id=event_id).distinct().get()).data
            return Response(data=data)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, event_id):
        if ('title' not in request.data or 'groups' not in request.data or
                any(not isinstance(g, int) for g in request.data['groups'])
                or not request.data['groups']):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        request.data['groups'] = list(set(request.data['groups']))

        if not request.user.groups.filter(id__in=request.data['groups']).count() == len(request.data['groups']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            event_data = {
                'title': request.data['title'],
                'type': request.data.get('type'),
                'date': request.data.get('date'),
                'start_time': request.data.get('start_time'),
                'end_time': request.data.get('end_time'),
                'location': request.data.get('location'),
                'cloud_url': request.data.get('cloud_url')
            }
            event_query = Event.objects.filter(groups__curators=request.user, id=event_id).distinct()
            event_query.update(**event_data)
            event = event_query.get()
            event.groups.set(Group.objects.filter(id__in=request.data['groups']))
            data = EventSerializer(event).data
            return Response(data=data)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        event_query = Event.objects.filter(groups__curators=request.user, id=event_id)
        if not event_query.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        event_query.delete()
        return Response()

class RequestsView(APIView):
    def get(self, request):
        try:
            data = RequestSerializer(request.user.requests, many=True).data
            return Response(data=data)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if ('title' not in request.data or 'description' not in request.data or
            'status' not in request.data):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            request_data = {
                'title': request.data['title'],
                'description': request.data['description'],
                'status': request.data['status'],
                'user': request.user
            }
            request_entity = Request.objects.create(**request_data)
            data = RequestSerializer(request_entity).data
            return Response(data=data)
        except Exception as e:
            return Response(data={'error': type(e).__name__, 'message': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
