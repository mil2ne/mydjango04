from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect, get_object_or_404

from weblog.forms import PostForm
from weblog.models import Post


def post_new(request):
    if request.method == "GET":
        form = PostForm()
    else:
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            print("form.cleand_data : ", form.cleaned_data)

            post = form.save(commit=False)
            post.ip = request.META["REMOTE_ADDR"]
            post.save()
            form.save_m2m()

            return redirect("/")
        else:
            pass

    return render(request, "weblog/post_form.html", {"form": form})


def post_edit(request, pk):
    instance = get_object_or_404(Post, pk=pk)

    if request.method == "GET":
        form = PostForm(instance=instance)
    else:
        form = PostForm(data=request.POST, files=request.FILES, instance=instance)
        if form.is_valid():
            print("form.cleand_data : ", form.cleaned_data)

            post = form.save(commit=False)

            post.ip = request.META["REMOTE_ADDR"]
            post.save()
            form.save_m2m()

            return redirect("/")

    return render(request, "weblog/post_form.html", {"form": form})
