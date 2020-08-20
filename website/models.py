import io
import subprocess
import sys
import threading
import uuid
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import AbstractUser
from django.db import models


def upload_to(instance, filename):
    return f"archives/{instance.website_snapshot.author.id}/{filename}"


class Account(AbstractUser):
    username = models.CharField(db_index=True, max_length=30, unique=True, blank=False)
    email = models.EmailField(db_index=True, unique=True, blank=False)
    first_name = None
    last_name = None
    public = models.BooleanField(default=False)


class Tag(models.Model):
    name = models.CharField(db_index=True, max_length=30, unique=True, blank=False)

    def __str__(self):
        return f"<Tag: {self.name}>"


class Snapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField(auto_now=True)
    content = models.FileField(upload_to=upload_to)
    content_type = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"{self.date} | {self.website_snapshot}"

    def delete(self, *args, **kwargs):
        self.content.delete()
        super(Snapshot, self).delete(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    fav = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="post_tag")
    snapshot = models.OneToOneField(
        Snapshot, on_delete=models.CASCADE, null=True, related_name="website_snapshot"
    )

    def delete(self, *args, **kwargs):
        if self.snapshot:
            self.snapshot.delete()
        super(Post, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.title:
            try:
                if not urlparse(self.url).scheme:
                    self.url = "http://" + self.url
                self.title = BeautifulSoup(requests.get(self.url).text).title.text
            except:
                self.title = self.url

        if Post.objects.filter(
            title=self.title,
            url=self.url
        ).count():
            return
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.url}"

    def queue_download(self, *args, **kwargs):
        self.snapshot = Snapshot.objects.create()
        self.save()
        t = threading.Thread(target=self.download_site, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()

    def download_site(self, *args, **kwargs):
        # https://github.com/Y2Z/monolith
        res = requests.get(self.url)
        if sys.getsizeof(res.content) > 25_000_000:  # don't continue if file too large
            self.snapshot.delete()
            self.snapshot = None
            return self.save()
        content_type = res.headers["content-type"]
        if "text/html" in content_type:  # if it's a website, include css in html file
            out = subprocess.check_output(f"monolith {self.url} -j --silent",shell=True)
            if sys.getsizeof(out) > 25_000_000:  # in case too large with css/images
                self.snapshot.delete()
                self.snapshot = None
                return self.save()
        else:
            out = res.content
        self.snapshot.content_type = content_type
        self.snapshot.content.save(str(self.snapshot.id), io.BytesIO(out))
        super(Post, self).save(*args, **kwargs)
