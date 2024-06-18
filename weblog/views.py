from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect

from weblog.forms import PostForm


def post_new(request):
    if request.method == "GET":
        form = PostForm()
    else:
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            print("form.cleand_data : ", form.cleaned_data)

            form.save()

            return redirect("/")
        else:
            pass

    return render(request, "weblog/post_form.html", {"form": form})
