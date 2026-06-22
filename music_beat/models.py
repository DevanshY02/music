from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Song(models.Model,):
    song_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=2000)
    singer=models.CharField(max_length=2000)
    tags=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images', blank=True)
    song=models.FileField(upload_to='images', blank=True)
    singer=models.CharField(max_length=1000, default="")
    external_image_url=models.URLField(max_length=2000, blank=True)
    external_audio_url=models.URLField(max_length=2000, blank=True)
    external_source_url=models.URLField(max_length=2000, blank=True)
    lyrics_text=models.TextField(blank=True)
    source_label=models.CharField(max_length=100, blank=True)

    @property
    def image_url(self):
        if self.external_image_url:
            return self.external_image_url

        if self.image:
            return self.image.url

        return ""

    @property
    def audio_url(self):
        if self.external_audio_url:
            return self.external_audio_url

        if self.song:
            return self.song.url

        return ""

    @property
    def can_download(self):
        return bool(self.song and not self.external_audio_url)

    def __str__(self):
        return self.name

class Watchlater(models.Model):
    watch_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    video_id=models.CharField(max_length=100000, default="")

class History(models.Model):
    hist_id=models.AutoField(primary_key=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    music_id=models.CharField(max_length=100000, default="")


