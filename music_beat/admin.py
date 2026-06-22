from django.contrib import admin
from .models import Song, Watchlater, History
# Register your models here.

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ("name", "singer", "tags", "source_label")
    search_fields = ("name", "singer", "tags")
    list_filter = ("source_label", "tags")

admin.site.register(Watchlater)
admin.site.register(History)
