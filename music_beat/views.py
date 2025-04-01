from django.shortcuts import render
from music_beat.models import Song, Watchlater, History
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.db.models import Case, When
import requests
from bs4 import BeautifulSoup


GENIUS_API_KEY = "n23ewu6_IQyMVBqkGp00FdTH0D-BpKnzjNo_a7Vl2gMFFM1_2kCQpm6NZem92Ep7"

def get_lyrics(song_name, artist):
    if not GENIUS_API_KEY:
        return "Genius API key is missing."

    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"{song_name} {artist}"}

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        json_data = response.json()
        hits = json_data.get("response", {}).get("hits", [])
        
        if hits:
            song_url = hits[0]["result"]["url"]
            return scrape_lyrics(song_url)
        return "Lyrics not found."
    else:
        return f"Error fetching lyrics. Status: {response.status_code}"

def scrape_lyrics(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        lyrics_divs = soup.find_all("div", class_="Lyrics__Container-sc-1ynbvzw-6")

        if lyrics_divs:
            return "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
        return "Lyrics not available."
    return "Error fetching lyrics page."
def search(request):
    search_query = request.GET.get("search", "").strip()
    tag_filter = request.GET.get("tag", "").strip()
    sort_by = request.GET.get("sort", "name")  # Default sorting by name

    # Base Queryset
    songs = Song.objects.all()

    # Apply search filter if search_query is not empty
    if search_query:
        songs = songs.filter(name__icontains=search_query)

    # Apply tag filter if tag_filter is not empty
    if tag_filter:
        songs = songs.filter(tags__icontains=tag_filter)

    # Sorting
    if sort_by in ["name", "singer", "tag"]:
        songs = songs.order_by(sort_by)

    return render(request, "music_beat/search.html", {
        "songs": songs,
        "search_query": search_query,
        "tag_filter": tag_filter,
        "sort_by": sort_by,
        "all_tags": Song.objects.values_list("tags", flat=True).distinct(),
    })


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

from django.contrib.auth.decorators import login_required

@login_required(login_url="/music_beat/login")
def watchlater(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST['video_id']

        watch = Watchlater.objects.filter(user=user)

        for i in watch:
            if video_id == i.video_id:
                message = "Your song is already added"
                break
        else:
            watchlater = Watchlater(user=user, video_id=video_id)
            watchlater.save()
            message = "Your song has been added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(request, "music_beat/songtemplate.html", {'song': song, "message": message})
    
    wl = Watchlater.objects.filter(user=request.user)
    l1 = [i.video_id for i in wl]
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(l1)])
    song = Song.objects.filter(song_id__in=l1).order_by(preserved)

    return render(request, "music_beat/watchlater.html", {'song': song})


def logout_user(request):
    logout(request)
    return redirect('/')

def index(request):
    song = Song.objects.all()
    return render(request,'music_beat/index.html',{'song': song})

def songs(request):
    song_list = Song.objects.all().order_by('name')  # Default sorting by name

    # Get filter, search, and sort parameters from request
    search_query = request.GET.get('search', '')
    tag_filter = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', '')

    # Filtering by tag
    if tag_filter:
        song_list = song_list.filter(tags__icontains=tag_filter)

    # Searching by song name
    if search_query:
        song_list = song_list.filter(name__icontains=search_query)

    # Sorting logic
    if sort_by == 'name':
        song_list = song_list.order_by('name')
    elif sort_by == 'singer':
        song_list = song_list.order_by('singer')
    elif sort_by == 'tag':
        song_list = song_list.order_by('tags')

    # Get unique tags for filtering dropdown
    all_tags = set(Song.objects.values_list('tags', flat=True))

    return render(request, 'music_beat/songs.html', {
        'song': song_list,
        'all_tags': all_tags,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'sort_by': sort_by,
    })


# def songtemplate(request, id):
#     song = Song.objects.filter(song_id=id).first()
#     return render(request, 'music_beat/songtemplate.html',{'song': song})
def songtemplate(request, id):
    song = Song.objects.filter(song_id=id).first()
    lyrics = get_lyrics(song.name, song.singer)

    return render(request, 'music_beat/songtemplate.html', {'song': song, 'lyrics': lyrics})

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