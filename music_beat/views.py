from django.shortcuts import render
from music_beat.models import Song, Watchlater, History
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db.models import Case, When

def search(request):
    getter=request.GET.get("getter")
    song=Song.objects.all()
    qs=song.filter(name__icontains=getter)

    return render(request, 'music_beat/search.html',{'songs': qs})

def history(request):
    if request.method == "POST":
        user=request.user
        music_id=request.POST['music_id']
        history=History(user=user, music_id=music_id)
        history.save()
        return redirect(f"/music_beat/songs/{music_id}")
    
    history=History.objects.filter(user=request.user)
    h1=[]
    for i in history:
        h1.append(i.music_id)
    
    preserved= Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(h1)])
    song = Song.objects.filter(song_id__in=h1).order_by(preserved)

    return render(request, 'music_beat/history.html',{'history': song})

def watchlater(request):
    if request.method == "POST":
        user=request.user
        video_id=request.POST['video_id']

        watch= Watchlater.objects.filter(user=user)

        for i in watch:
            if video_id==i.video_id:
                message="Your song Is Already Added"
                break
        else:
           watchlater=Watchlater(user=user, video_id=video_id)
           watchlater.save()
           message="your song added"

        song=Song.objects.filter(song_id=video_id).first()
        return render(request, f"music_beat/songtemplate.html", {'song': song, "message": message})
    
    wl=Watchlater.objects.filter(user=request.user)
    l1=[]
    for i in wl:
        l1.append(i.video_id)
    
    preserved= Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(l1)])
    song = Song.objects.filter(song_id__in=l1).order_by(preserved)

    return render(request, 'music_beat/watchlater.html', {'song': song})

def logout_user(request):
    logout(request)
    return redirect('/')

def index(request):
    song = Song.objects.all()
    return render(request,'index.html',{'song': song})

def songs(request):
    song = Song.objects.all()
    return render(request, 'music_beat/songs.html',{'song': song})

def songtemplate(request, id):
    song = Song.objects.filter(song_id=id).first()
    return render(request, 'music_beat/songtemplate.html',{'song': song})

def login(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']    
        user=authenticate(username=username, password= password)
        auth_login(request, user)
        return redirect('/')

    return render(request, 'music_beat/login.html')

def signup(request):
    if request.method == "POST":
        email=request.POST['email']
        username=request.POST['username']
        first_name=request.POST['firstname']
        pass1=request.POST['pass1']

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name=first_name
        myuser.save()
        user=authenticate(username=username, password= pass1)
        auth_login(request, user)

        return redirect('/')
    return render(request, 'music_beat/signup.html')