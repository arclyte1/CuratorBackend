from rest_framework import serializers

from curator.models import User, Event, Group, Student


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name']


class GroupSerializer(serializers.ModelSerializer):
    students = StudentSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ['id', 'title', 'students']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'type', 'date', 'start_time', 'end_time', 'location', 'cloud_url', 'groups',
                  'present_students']
