from django.contrib import admin

from .models import Snapshot, Post, Account, Tag

# Register your models here.

admin.site.register(Post)
admin.site.register(Snapshot)
admin.site.register(Account)
admin.site.register(Tag)
