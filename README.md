# Music Player App 

Music player is a Django-based music web app where users can browse songs, search and filter the catalog, view song details, play uploaded audio, save songs to watch later, and track listening history.

## Features

- Home page with available songs
- Song listing with search, tag filters, and sorting
- Song detail page with audio playback
- Lyrics lookup for song pages
- User signup, login, and logout
- Watch Later list for logged-in users
- Listening history
- Django admin panel for managing songs
- Media upload support for song files and cover images

## Tech Stack

- Python
- Django 5
- SQLite
- Django templates
- HTML, CSS, and static assets

## Project Structure

```text
music/
|-- manage.py
|-- requirements.txt
|-- db.sqlite3
|-- music/
|   |-- settings.py
|   |-- urls.py
|   |-- views.py
|   `-- wsgi.py
|-- music_beat/
|   |-- models.py
|   |-- views.py
|   |-- urls.py
|   |-- templates/
|   `-- static/
|-- media/
`-- images/
```

## How To Run Locally

Clone the repository:

```bash
git clone https://github.com/DevanshY02/music.git
cd music
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Open the app:

```text
http://127.0.0.1:8000
```

## Main Routes

- `/` - Home page
- `/music_beat/songs/` - Song list
- `/music_beat/songs/<id>` - Song detail page
- `/music_beat/search` - Search page
- `/music_beat/signup` - Signup page
- `/music_beat/login` - Login page
- `/music_beat/watchlater` - Watch Later page
- `/music_beat/history` - Listening history
- `/admin/` - Django admin panel

## Managing Songs

Use the Django admin panel to add or update songs:

```text
http://127.0.0.1:8000/admin/
```

Each song can include:

- Name
- Singer
- Tags
- Cover image
- Audio file

## Notes For Deployment

This repository includes Render-ready deployment files:

- `render.yaml`
- `build.sh`
- `requirements-render.txt`

To deploy on Render:

1. Open [Render](https://render.com) and sign in.
2. Click **New** > **Blueprint**.
3. Connect `https://github.com/DevanshY02/music`.
4. Apply the blueprint.
5. Wait for the build to finish.

Render will create a public `.onrender.com` URL for the app.

The demo deployment serves committed files from `media/` so existing song thumbnails and audio can load on Render. New files uploaded from the deployed admin can disappear after a redeploy or restart unless you add persistent disk or external storage.

Optional environment variables:

- `GENIUS_API_KEY` - enables lyrics lookup.
- `ALLOWED_HOSTS` - comma-separated extra hostnames.
- `CSRF_TRUSTED_ORIGINS` - comma-separated trusted HTTPS origins.

Before deploying publicly, also review:

- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Move `SECRET_KEY` and API keys into environment variables
- Use a production database instead of local SQLite when needed
- Configure durable media file hosting for production uploads

The included Render setup uses SQLite for a simple demo deployment. For a real production app, use PostgreSQL and persistent media storage.

## License

This project is for learning and portfolio use. Add a license file if you want to define reuse permissions.
