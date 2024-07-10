from django.contrib import admin
from .models import CustomUser, Post, Like, Tag

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Tag)