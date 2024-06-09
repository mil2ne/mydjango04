from django.contrib import admin
from django.utils.html import format_html

from hottrack.filter import ReleaseDateFilter
from hottrack.models import Song
from hottrack.utils.melon import get_likes_dict


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    search_fields = ["name", "artist_name", "album_name"]
    list_display = [
        "cover_image_tag",
        "name",
        "artist_name",
        "album_name",
        "genre",
        "like_count",
        "release_date",
    ]
    list_filter = ["genre", ReleaseDateFilter]
    actions = ["update_like_count"]

    # def has_add_permission(self, request):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False
    #
    # #
    # def has_delete_permission(self, request, obj=None):
    #     return False

    #
    # def has_view_permission(self, request, obj=None):
    #     pass

    def update_like_count(self, request, queryset):
        melon_uid_list = queryset.values_list("melon_uid", flat=True)
        likes_dict = get_likes_dict(melon_uid_list)

        changed_count = 0
        for song in queryset:
            if song.like_count != likes_dict.get(song.melon_uid):
                song.like_count = likes_dict.get(song.melon_uid)
                changed_count += 1

        Song.objects.bulk_update(
            queryset,
            fields=["like_count"],
        )

        self.message_user(request, f"{changed_count} 곡의 좋아요 갱신 완료")
