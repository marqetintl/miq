# Generated by Django 4.0.2 on 2022-07-06 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0003_hit_url_alter_searchterm_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='hit',
            name='app',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='hit',
            name='model',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
