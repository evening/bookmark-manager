from django.contrib import admin

from .models import Archive, Post, Account

# Register your models here.

admin.site.register(Post)
admin.site.register(Archive)
admin.site.register(Account)
