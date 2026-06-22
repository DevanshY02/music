from django.shortcuts import render
from music_beat.models import Song, Watchlater, History
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Case, When
import os
import requests
from bs4 import BeautifulSoup
from music_beat.external_music import lookup_itunes_track, search_itunes


GENIUS_API_KEY = os.environ.get("GENIUS_API_KEY", "")
GENIUS_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_lyrics(song_name, artist):
    fallback_lyrics = get_lrclib_lyrics(song_name, artist)

    if not GENIUS_API_KEY:
        return fallback_lyrics

    headers = {**GENIUS_HEADERS, "Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": f"{song_name} {artist}"}

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=12)
    except requests.RequestException:
        return fallback_lyrics

    if response.status_code == 200:
        json_data = response.json()
        hits = json_data.get("response", {}).get("hits", [])
        
        if hits:
            song_url = hits[0]["result"]["url"]
            genius_lyrics = scrape_lyrics(song_url)

            if is_usable_lyrics(genius_lyrics):
                return genius_lyrics

        return fallback_lyrics

    return fallback_lyrics

def get_lrclib_lyrics(song_name, artist):
    artist_candidates = [
        artist,
        artist.split(",")[0],
        artist.split("|")[0],
    ]

    for artist_name in artist_candidates:
        artist_name = artist_name.strip()

        if not artist_name:
            continue

        try:
            response = requests.get(
                "https://lrclib.net/api/search",
                params={"track_name": song_name, "artist_name": artist_name},
                headers={"User-Agent": "DevanshY02 music app (https://github.com/DevanshY02/music)"},
                timeout=12,
            )
        except requests.RequestException:
            continue

        if response.status_code != 200:
            continue

        for result in response.json():
            lyrics = result.get("plainLyrics") or result.get("syncedLyrics")

            if lyrics:
                return clean_lyrics(lyrics)

    return "Lyrics not found."

def is_usable_lyrics(lyrics):
    if not lyrics:
        return False

    unavailable_messages = (
        "Error fetching lyrics",
        "Lyrics could not",
        "Lyrics not available",
        "Lyrics not found",
    )

    return not lyrics.startswith(unavailable_messages)

def clean_lyrics(lyrics):
    lines = []

    for line in lyrics.splitlines():
        stripped = line.strip()

        if stripped:
            lines.append(stripped)

    return "\n".join(lines)

def scrape_lyrics(url):
    try:
        response = requests.get(url, headers=GENIUS_HEADERS, timeout=12)
    except requests.RequestException:
        return "Lyrics could not be loaded right now."

    if response.status_code != 200:
        return f"Error fetching lyrics page. Status: {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_divs = soup.select('div[data-lyrics-container="true"]')

    if not lyrics_divs:
        lyrics_divs = soup.select('div[class^="Lyrics__Container"], div[class*=" Lyrics__Container"]')

    lines = []

    for lyrics_div in lyrics_divs:
        text = lyrics_div.get_text(separator="\n")
        lines.extend(line.strip() for line in text.splitlines() if line.strip())

    if lines:
        return clean_lyrics("\n".join(lines))

    return "Lyrics not available."
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
    lyrics = song.lyrics_text or get_lyrics(song.name, song.singer)

    return render(request, 'music_beat/songtemplate.html', {'song': song, 'lyrics': lyrics})

@staff_member_required(login_url="/admin/login/")
def import_song(request):
    query = request.GET.get("q", "").strip()
    results = []

    if request.method == "POST":
        track_id = request.POST.get("track_id", "").strip()
        track = lookup_itunes_track(track_id)

        if not track:
            messages.error(request, "Could not import that song. Try another result.")
            return redirect("/music_beat/import-song")

        lyrics = get_lrclib_lyrics(track["name"], track["artist"])
        lyrics_text = "" if lyrics == "Lyrics not found." else lyrics

        song = Song.objects.create(
            name=track["name"],
            singer=track["artist"],
            tags=track["genre"] or "Imported",
            external_image_url=track["artwork_url"],
            external_audio_url=track["preview_url"],
            external_source_url=track["source_url"],
            lyrics_text=lyrics_text,
            source_label="iTunes Preview",
        )

        messages.success(request, f"Imported {song.name}.")
        return redirect(f"/music_beat/songs/{song.song_id}")

    if query:
        try:
            results = search_itunes(query)
        except requests.RequestException:
            messages.error(request, "Could not reach iTunes right now. Try again in a moment.")

    return render(request, "music_beat/import_song.html", {"query": query, "results": results})

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
