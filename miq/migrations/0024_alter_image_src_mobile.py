# Generated by Django 4.0.1 on 2022-01-16 02:44

from django.db import migrations, models
import miq.models.image_mod


class Migration(migrations.Migration):

    dependencies = [
        ('miq', '0023_alter_image_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='src_mobile',
            field=models.ImageField(blank=True, help_text='Select an image file', max_length=500, null=True, upload_to=miq.models.image_mod.upload_thumb_to, verbose_name='Source mobile'),
        ),
    ]