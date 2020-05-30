from django.db import models
import requests
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from django.contrib.auth.models import AbstractUser
import subprocess


class Account(AbstractUser):
    username = models.CharField(db_index=True, max_length=30, unique=True, blank=False)
    email = models.EmailField(db_index=True, unique=True, blank=False)
    first_name = None
    last_name = None


class Archive(models.Model):
    date = models.DateTimeField(auto_now=True)
    content = models.TextField(blank=True)


class Post(models.Model):
    title = models.CharField(max_length=100, blank=True, default="")
    url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    fav = models.BooleanField(default=False)
    archive = models.OneToOneField(Archive, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.title:
            try:
                if not urlparse(self.url).scheme:
                    self.url = "http://" + self.url
                self.title = BeautifulSoup(requests.get(self.url).text).title.text
            except:
                pass
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.url}"

    def download_site(self, *args, **kwargs):
        # https://github.com/Y2Z/monolith
        out = subprocess.check_output(f"monolith {self.url} -j")
        self.archive = Archive.objects.create(content=out.decode("utf-8"))
        super(Post, self).save(*args, **kwargs)
