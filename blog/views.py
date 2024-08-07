from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files import File
from django.db.models import Q
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import trigger_client_event
from vanilla import CreateView, ListView, DetailView, UpdateView, FormView

from blog.forms import ReviewForm, DemoForm, MemoForm, TagForm
from blog.models import Post, Review, Memo, MemoGroup, Tag
from core.decorators import login_required_hx


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
def momo_form(request, group_pk):
    MemoFormSet = inlineformset_factory(
        parent_model=MemoGroup,
        # parent_model=get_user_model(),
        model=Memo,
        form=MemoForm,
        extra=3,
        can_delete=True,
    )

    memo_group = get_object_or_404(MemoGroup, pk=group_pk)

    queryset = None
    if request.method == "GET":
        formset = MemoFormSet(instance=memo_group, queryset=queryset)
    else:
        formset = MemoFormSet(
            data=request.POST,
            files=request.FILES,
            instance=memo_group,
            queryset=queryset,
        )
        if formset.is_valid():
            objs = formset.save()

            if objs:
                messages.success(request, f"메모 {len(objs)}개를 저장했습니다.")

            if formset.deleted_objects:
                messages.success(
                    request, f"메모 {len(formset.deleted_objects)}개를 삭제했습니다."
                )
            return redirect("blog:memo_form", group_pk)

    return render(
        request, "blog/momo_form.html", {"memo_group": memo_group, "formset": formset}
    )


# def tag_list(request):
#     tag_qs = Tag.objects.all()
#
#     query = request.GET.get("query", "")
#     if query:
#         tag_qs = tag_qs.filter(name__icontains=query)
#
#     # is_htmx = request.META.get("HTTP_HX_REQUEST") == "true"
#     if request.htmx:
#         template_name = "blog/_tag_list.html"
#     else:
#         template_name = "blog/tag_list.html"
#
#     return render(request, template_name, {"tag_list": tag_qs})


class TagListView(ListView):
    model = Tag
    queryset = Tag.objects.all()
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get("query", "")
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            template_name = "blog/_tag_list.html"
        else:
            template_name = "blog/tag_list.html"
        return [template_name]


tag_list = TagListView.as_view()


@login_required_hx
def tag_new(request, pk=None):
    if pk:
        instance = get_object_or_404(Tag, pk=pk)
    else:
        instance = None

    if request.method == "GET":
        form = TagForm(instance=instance)
    else:
        form = TagForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "태그를 저장했습니다.")
            response = render(request, "core/_messages_as_event.html")
            response = trigger_client_event(response, "refresh-tag-list")
            return response

    return render(
        request,
        "blog/_tag_form.html",
        {
            "form": form,
        },
    )


def tag_edit(request, pk):
    return tag_new(request, pk)


def tag_list_item(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    return render(request, "blog/_tag_list_item.html", {"tag": tag})


@require_http_methods(["DELETE"])
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    return HttpResponse("")


def test(request):
    return render(request, "blog/test.html")
