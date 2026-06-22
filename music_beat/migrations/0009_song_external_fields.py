from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_beat', '0008_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='image',
            field=models.ImageField(blank=True, upload_to='images'),
        ),
        migrations.AlterField(
            model_name='song',
            name='song',
            field=models.FileField(blank=True, upload_to='images'),
        ),
        migrations.AddField(
            model_name='song',
            name='external_image_url',
            field=models.URLField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='song',
            name='external_audio_url',
            field=models.URLField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='song',
            name='external_source_url',
            field=models.URLField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='song',
            name='lyrics_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='song',
            name='source_label',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
