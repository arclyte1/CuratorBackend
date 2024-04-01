from django.contrib import admin

from curator.models import User, Group, Student, Event

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(Event)
