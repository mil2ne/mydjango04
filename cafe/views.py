from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def coffee_stamp(request):
    if request.method == "GET":
        response = HttpResponse(
            """
            <form method="POST">
                <input type="text" name="phone" placeholder="적립을 위해 휴대폰 번호를 입력하세요" />
            </form>
            """
        )
    else:
        phone = request.POST["phone"]
        request.session["phone"] = phone

        order_count = request.session.get("order_count", 0)
        order_count += 1
        request.session["order_count"] = order_count

        response = HttpResponse(
            f"""
            {phone}님, 적립횟수 : {order_count}<br/>
            10회 이상 스탬프를 찍으셧다면<br/>
            <a href="/cafe/free-coffee/">무료 커피를 신청하세요.</a>
            """
        )

    return response


def coffee_free(request):

    phone = request.session.get("phone", "")
    if not phone:
        return redirect("coffee:coffee_stamp")

    order_count = request.session.get("order_count", 0)

    if order_count < 10:
        response = HttpResponse(
            f"{phone}님 . 스템프 {order_count}번 찍었습니다.{10-order_count}번 찍으면 무료쿠폰"
        )
    else:
        response = HttpResponse(f"{phone}님. 무료쿠폰을 사용하겠습니까?")

    return response
