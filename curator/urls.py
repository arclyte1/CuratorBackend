from django.urls import path

from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)


urlpatterns = [
    path('send-code', views.UserSendCodeView.as_view()),
    path('verify-code', views.UserVerifyCodeView.as_view(), name='token_obtain_pair'),
    path('refresh-token', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-token', TokenVerifyView.as_view(), name='token_verify'),
    path('events', views.EventView.as_view()),
    path('events/<int:event_id>', views.EventDetailsView.as_view()),
    path('groups', views.GroupView.as_view()),
    path('requests', views.RequestsView.as_view()),
]
