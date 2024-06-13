from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post


# Create your views here.


@login_required
@permission_required("blog.view_post", raise_exception=False)
def post_detail(request, slug):
    # slug 는 url 에만 사용할뿐, 조회에는 사용하지 않음
    post = get_object_or_404(Post, slug=slug)

    return HttpResponse(f"{post.pk} 번 글의 {post.slug}")


@login_required
@permission_required("blog.view_premium_post", login_url="blog:premium_user_guide")
def post_premium_detail(request, slug):
    return HttpResponse(f"프리미엄 컨텐츠 페이지 : {slug}")


def premium_user_guide(request):
    return HttpResponse("프리미엄 유저 가이드 페이지")


def post_list(request):
    post_qs = Post.objects.all()
    post_qs = post_qs.select_related("author")
    post_qs = post_qs.prefetch_related("tag_set", "comment_set", "comment_set__author")
    return render(request, "blog/post_list.html", {"post_list": post_qs})
