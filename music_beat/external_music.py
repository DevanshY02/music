import requests


ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
ITUNES_LOOKUP_URL = "https://itunes.apple.com/lookup"


def search_itunes(query, limit=12):
    response = requests.get(
        ITUNES_SEARCH_URL,
        params={
            "term": query,
            "media": "music",
            "entity": "song",
            "limit": limit,
        },
        timeout=12,
    )
    response.raise_for_status()
    return [normalize_itunes_track(result) for result in response.json().get("results", [])]


def lookup_itunes_track(track_id):
    response = requests.get(
        ITUNES_LOOKUP_URL,
        params={"id": track_id, "entity": "song"},
        timeout=12,
    )
    response.raise_for_status()
    results = response.json().get("results", [])

    for result in results:
        if result.get("wrapperType") == "track":
            return normalize_itunes_track(result)

    return None


def normalize_itunes_track(result):
    artwork_url = result.get("artworkUrl100", "")

    return {
        "track_id": str(result.get("trackId", "")),
        "name": result.get("trackName", ""),
        "artist": result.get("artistName", ""),
        "album": result.get("collectionName", ""),
        "genre": result.get("primaryGenreName", ""),
        "artwork_url": upgrade_artwork_url(artwork_url),
        "preview_url": result.get("previewUrl", ""),
        "source_url": result.get("trackViewUrl", ""),
    }


def upgrade_artwork_url(url):
    if not url:
        return ""

    return url.replace("100x100bb", "600x600bb")
