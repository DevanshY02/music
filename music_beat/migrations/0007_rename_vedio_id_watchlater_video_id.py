# Generated by Django 5.1.6 on 2025-03-26 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music_beat', '0006_watchlater'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watchlater',
            old_name='vedio_id',
            new_name='video_id',
        ),
    ]
