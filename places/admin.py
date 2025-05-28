from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline

from .models import Place, ContactMessage, LikeDislike, Post

admin.site.register(Place)
admin.site.register(ContactMessage)

class LikeInlineModel(StackedInline):
    model = LikeDislike
    extra = 0

class PostAdminModel(ModelAdmin):
    inlines = [
        LikeInlineModel
    ]

admin.site.register(Post, PostAdminModel)