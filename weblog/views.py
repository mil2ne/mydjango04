from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect, get_object_or_404

from vanilla import FormView

# from django.views.generic import FormView

from weblog.forms import PostForm
from weblog.models import Post


class PostCreateView(FormView):
    form_class = PostForm
    template_name = "weblog/post_form.html"
    success_url = "/"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.ip = self.request.META["REMOTE_ADDR"]
        post.save()
        form.save_m2m()
        return super().form_valid(form)


post_new = PostCreateView.as_view()


class PostUpdateView(FormView):
    form_class = PostForm
    template_name = "weblog/post_form.html"
    success_url = "/"

    # def get_form_kwargs(self):
    #     post_pk = self.kwargs["pk"]
    #     instance = get_object_or_404(Post, pk=post_pk)
    #
    #     form_kwargs = super().get_form_kwargs()
    #     form_kwargs["instance"] = instance
    #     return form_kwargs

    def get_form(self, data=None, files=None, **kwargs):
        post_pk = self.kwargs["pk"]
        instance = get_object_or_404(Post, pk=post_pk)
        kwargs["instance"] = instance
        return super().get_form(data=data, files=files, **kwargs)

    def form_valid(self, form):
        form.save(commit=True)
        return super().form_valid(form)


post_edit = PostUpdateView.as_view()
