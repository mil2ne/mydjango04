from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.db.models import Q
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
    query = request.GET.get("query", "").strip()
    post_qs = Post.objects.all()

    if query:
        post_qs = post_qs.filter(
            Q(tag_set__name__in=[query]) | Q(title__icontains=query)
        )

    post_qs = post_qs.select_related("author")
    post_qs = post_qs.prefetch_related("tag_set")
    return render(
        request, "blog/post_list.html", {"query": query, "post_list": post_qs}
    )


def search(request):
    query = request.GET.get("query", "").strip()
    return render(
        request,
        "blog/search.html",
        {
            "query": query,
        },
    )


def post_new(request):
    # 요청 데이터에서 값을 추출하고,
    # 입력값에 대한 유효성 검사를 필히 수행해야만 합니다.
    message: str = request.POST.get("message", "")
    photo: File = request.FILES.get("photo", "")
    errors = {
        "message": [],
        "photo": [],
    }

    # 요청 데이터에서 값을 추출하고,
    # 입력값에 대한 유효성 검사를 필히 수행해야만 합니다.
    # 장고에서는 이러한 유효성 검사를 Form이나 Serializer에 위임해서 처리합니다.
    if not message:
        errors["message"].append("message 필드는 필수 필드입니다.")
    if len(message) < 10:
        errors["message"].append("message 필드를 10글자 이상이어야 합니다.")
    if not photo:
        errors["photo"].append("photo 필드는 필수 필드입니다.")
    if photo and not photo.name.lower().endswith((".jpg", ".jpeg")):
        errors["photo"].append("jpg 파일만 업로드할 수 있습니다.")

    return render(
        request=request,
        template_name="blog/post_new.html",
        context={
            "message": message,
            "photo": photo,
            "errors": errors,
        },
    )
