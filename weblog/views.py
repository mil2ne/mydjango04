from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect

from weblog.forms import PostForm
from weblog.models import Post


def post_new(request):
    if request.method == "GET":
        form = PostForm()
    else:
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            print("form.cleand_data : ", form.cleaned_data)

            post = Post()
            post.title = form.cleaned_data["title"]
            post.content = form.cleaned_data["content"]
            post.status = form.cleaned_data["status"]

            photo_file: UploadedFile = form.cleaned_data["photo"]
            if photo_file is not None:
                post.photo.save(photo_file.name, photo_file, save=False)
            post.save()

            return redirect("/")
        else:
            pass

    return render(request, "weblog/post_form.html", {"form": form})
