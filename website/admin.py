from django.contrib import admin

from .models import Archive, Post, Account, Tag

# Register your models here.

admin.site.register(Post)
admin.site.register(Archive)
admin.site.register(Account)
admin.site.register(Tag)
