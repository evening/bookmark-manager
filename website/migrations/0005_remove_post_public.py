# Generated by Django 3.0.3 on 2020-05-23 07:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("website", "0004_remove_post_to_read")]

    operations = [migrations.RemoveField(model_name="post", name="public")]
