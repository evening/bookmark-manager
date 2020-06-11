# Generated by Django 3.0.3 on 2020-06-11 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20200608_1749'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Archive',
            new_name='Snapshot',
        ),
        migrations.RemoveField(
            model_name='post',
            name='archive',
        ),
        migrations.AddField(
            model_name='post',
            name='snapshot',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='website_snapshot', to='website.Snapshot'),
        ),
    ]
