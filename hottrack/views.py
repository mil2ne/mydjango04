import datetime
import json
from io import BytesIO
from typing import Literal
from urllib.request import urlopen

from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic import DetailView, ListView, YearArchiveView, MonthArchiveView

from hottrack.models import Song

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from hottrack.utils.cover import make_cover_image
from .mixins import SearchQueryMixin

import pandas as pd


class IndexView(SearchQueryMixin, ListView):

    model = Song
    template_name = "hottrack/index.html"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        release_date = self.kwargs.get("release_date")
        if release_date:
            qs = qs.filter(release_date=release_date)

        if self.query:
            qs = qs.filter(
                Q(name__icontains=self.query)
                | Q(artist_name__icontains=self.query)
                | Q(album_name__icontains=self.query)
            )
        return qs


index = IndexView.as_view()

# def index(request: HttpRequest, release_date: datetime.date = None) -> HttpResponse:
#     query = request.GET.get("query", "").strip()
#
#     song_qs: QuerySet[Song] = Song.objects.all()
#
#     if release_date:
#         song_qs = song_qs.filter(release_date=release_date)
#
#     if query:
#         song_qs = song_qs.filter(
#             Q(name__icontains=query)
#             | Q(artist_name__icontains=query)
#             | Q(album_name__icontains=query)
#         )
#
#
#     return render(
#         request=request,
#         template_name="hottrack/index.html",
#         context={"song_list": song_qs, "query": query},
#     )


class SongDetailView(DetailView):
    model = Song

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        melon_uid = self.kwargs.get("melon_uid")
        if melon_uid:
            return get_object_or_404(queryset, melon_uid=melon_uid)
        return super().get_object(queryset)


song_detail = SongDetailView.as_view()


# def export_csv(request: HttpRequest) -> HttpResponse:
#     song_qs = Song.objects.all()
#     df = pd.DataFrame(data=song_qs.values())
#
#     export_file = BytesIO()
#     df.to_csv(export_file, index=False, encoding="utf-8-sig")
#
#     response = HttpResponse(content=export_file.getvalue(), content_type="text/csv")
#     response["Content-Disposition"] = 'attatchment; filename="hottrack.csv"'
#     return response


def export(request: HttpRequest, format: Literal["csv", "xlsx"]) -> HttpResponse:
    song_qs = Song.objects.all()
    df = pd.DataFrame(data=song_qs.values())

    export_file = BytesIO()

    if format == "csv":
        content_type = "text/csv"
        filename = "hottrack.csv"
        df.to_csv(path_or_buf=export_file, index=False, encoding="utf-8-sig")
    elif format == "xlsx":
        content_type = "application/vnd.ms-excel"
        filename = "hottrack.xlsx"
        df.to_excel(excel_writer=export_file, index=False)
    else:
        return HttpResponseBadRequest(f"Invalid format : {format}")

    response = HttpResponse(content=export_file.getvalue(), content_type=content_type)
    response["Content-Disposition"] = f"attatchment; filename={filename}"
    return response


def cover_png(request, pk):
    # 최대값 512, 기본값 256
    canvas_size = min(512, int(request.GET.get("size", 256)))

    song = get_object_or_404(Song, pk=pk)

    cover_image = make_cover_image(
        song.cover_url, song.artist_name, canvas_size=canvas_size
    )

    # param fp : filename (str), pathlib.Path object or file object
    # image.save("image.png")
    response = HttpResponse(content_type="image/png")
    cover_image.save(response, format="png")

    return response


class SongYearArchiveView(YearArchiveView):
    model = Song
    date_field = "release_date"
    make_object_list = True


class SongMonthArchiveView(MonthArchiveView):
    model = Song
    date_field = "release_date"
    month_format = "%m"
