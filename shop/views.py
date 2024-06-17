from django.http import HttpResponse


def current_travel_edit(request):

    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    src = request.GET.get("src")
    dest = request.GET.get("dest")

    message = f"{request.user}의 여행지를 {src}/{dest}로 변경했습니다."
    print(message)

    return HttpResponse(message)
