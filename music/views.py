from django.shortcuts import render
from music_beat.models import Song
def index(request):
    song = Song.objects.all()
    return render(request,'music_beat/index.html',{'song': song})