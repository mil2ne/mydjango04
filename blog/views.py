from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.db.models import Q
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from vanilla import CreateView, ListView, DetailView, UpdateView, FormView

from blog.forms import ReviewForm, DemoForm, MemoForm
from blog.models import Post, Review, Memo


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


review_list = ListView.as_view(
    model=Review,
)

review_new = CreateView.as_view(model=Review, form_class=ReviewForm)

review_detail = DetailView.as_view(
    model=Review,
)

review_edit = UpdateView.as_view(
    model=Review,
    form_class=ReviewForm,
)

demo_form = FormView.as_view(form_class=DemoForm, template_name="blog/demo_form.html")


@login_required
def momo_new(request):
    MemoFormSet = modelformset_factory(
        # parent_model=User,
        # parent_model=get_user_model(),
        model=Memo,
        form=MemoForm,
        extra=3,
        can_delete=True,
    )

    # instance = request.user

    queryset = Memo.objects.filter(author=request.user)
    if request.method == "GET":
        formset = MemoFormSet(queryset=queryset)
    else:
        formset = MemoFormSet(data=request.POST, files=request.FILES, queryset=queryset)
        if formset.is_valid():
            # objs = formset.save()

            objs = formset.save(commit=False)
            for memo in objs:
                memo.author = request.user
                memo.save()
            formset.save_m2m()

            if objs:
                messages.success(request, f"메모 {len(objs)}개를 저장했습니다.")

            if formset.deleted_objects:
                pk_list = [memo.pk for memo in formset.deleted_objects]
                Memo.objects.filter(pk__in=pk_list).delete()
                messages.success(
                    request, f"메모 {len(formset.deleted_objects)}개를 삭제했습니다."
                )
            return redirect("blog:memo_new")

    return render(request, "blog/momo_form.html", {"formset": formset})
