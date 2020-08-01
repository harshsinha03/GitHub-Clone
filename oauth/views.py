from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import OAuth, Uri, Token, Access_Code
from main.views import random_str
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def authorize(request):
    if request.method == "POST":
        client_id = request.POST["client_id"]
        redirect_uri = request.POST["redirect_uri"]

        app = OAuth.objects.get(client_id=client_id)

        if request.POST["for"] == "auth":
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, "oauth/auth.html", {
                    "name": app.name,
                    "client_id": client_id,
                    "redirect_uri": redirect_uri
                })
            return "wrong creds"

        access_code = random_str(40)
        t = Access_Code(access_code=access_code, user_id=request.user.id)
        t.save()

        return HttpResponseRedirect(redirect_uri + "?code=" + access_code)

    else:
        client_id = request.GET["client_id"]
        redirect_uri = request.GET["redirect_uri"]

        try:
            app = OAuth.objects.get(client_id=client_id)
        except:
            return HttpResponse("404")

        try:
            Uri.objects.get(client_id=client_id, redirect_uri=redirect_uri)
        except:
            return JsonResponse({"error": "invalid redirect uri"})

        if request.user.id is not None:
            return render(request, "oauth/auth.html", {
                "name": app.name,
                "client_id": client_id,
                "redirect_uri": redirect_uri
            })
        return render(request, "oauth/index.html", {
            "client_id": client_id,
            "redirect_uri": redirect_uri
        })


@csrf_exempt
def get_token(request):
    if request.method == "POST":
        client_id = request.POST["client_id"]
        client_secret = request.POST["client_secret"]
        code = request.POST["code"]

        try:
            o = OAuth.objects.get(client_id=client_id, client_secret=client_secret)
        except:
            return HttpResponse("404")

        try:
            a = Access_Code.objects.get(access_code=code)
        except:
            return JsonResponse({"error": "invalid access code"})

        token = random_str(60)
        t = Token(client_id=o.client_id, token=token, user_id=a.user_id)
        t.save()

        return JsonResponse({"token": token})


# def example(request):
#     try:
#         token = Token.objects.get(token=request.META["HTTP_AUTHORIZATION"].split("token ")[1])
#     except:
#         return JsonResponse({"error": "invalid token"})

#     return JsonResponse({"guesswhat": "success!"})