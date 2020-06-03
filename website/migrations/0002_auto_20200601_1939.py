# Generated by Django 3.0.3 on 2020-06-01 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("website", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="archive",
            name="content_type",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="archive",
            name="content",
            field=models.FileField(upload_to="archives"),
        ),
    ]