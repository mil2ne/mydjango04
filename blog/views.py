from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post


# Create your views here.


def post_detail(request, pk, slug=None):
    # slug 는 url 에만 사용할뿐, 조회에는 사용하지 않음
    post = get_object_or_404(Post, pk=pk)

    # 조회된 포스팅의 slug 와 주어진 slug 가 다르면 주어진 slug를 redirect
    if post.slug and (slug is None or post.slug != slug):
        return redirect("blog:post_detail", pk=pk, slug=post.slug, permanent=True)

    return HttpResponse(f"{post.pk} 번 글의 {post.slug}")
