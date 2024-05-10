from django.contrib import admin

from curator.models import User, Group, Student, Event, Request

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Event)
admin.site.register(Request)
