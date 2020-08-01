from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import os
import GitHubClone.settings as settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.admin import User
from .models import Repository, File, Directory, Profile, Follows
from oauth.models import OAuth, Uri, Token

import cloudinary
import cloudinary.uploader
import cloudinary.api

import requests
import random
import string
from termcolor import colored

cloudinary.config(
    cloud_name = "boyuan12",
    api_key = "893778436618783",
    api_secret = "X4LufXPHxvv4hROS3VZWYyR3tIE"
)

def random_words(n=3):
    word_site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
    response = requests.get(word_site)
    WORDS = response.content.splitlines()
    words = ""
    for i in range(n):
        word = random.choice(WORDS).decode("utf-8")
        words += word.capitalize()
    return words


def random_str(n):
    s = ""
    for i in range(n):
        s += random.choice(string.ascii_letters + string.digits)
    return s

def validate_url(url):
    # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        repos = Repository.objects.filter(user_id=request.user.id)
        return render(request, "main/index.html", {
            "repos": repos
        })
    else:
        return render(request, "main/home.html")


@login_required(login_url='/auth/login/')
def new(request):
    if request.method == "POST":

        status = None
        if request.POST["status"] == "public":
            status = 0
        else:
            status = 1

        r = Repository(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status)
        r.save()

        d = Directory(repo_id=Repository.objects.get(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status).id, name="/", dir_id=0, path="/")
        d.save()

        return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['name']}/")

    else:
        return render(request, "main/new.html")


def profile(request, username):

    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse("user doesn't exist")

    tab = ""

    try:
        if request.GET["tab"] == "repo":
            tab = "repo"
    except:
        tab = "overview"

    repos = Repository.objects.filter(user_id=user.id)

    try:
        p = Profile.objects.get(user_id=user.id)
    except:
        p = []

    following = (Follows.objects.filter(following=user.id))
    follows = (Follows.objects.filter(user_id=user.id))
    followed = False

    for i in following:
        if i.following == user.id:
            followed = True

    return render(request, "main/user.html", {
        "username": username,
        "tab": tab,
        "repos": repos,
        "user": user,
        "p": p,
        "follows": follows,
        "following": following,
        "followed": followed
    })


@login_required(login_url='/auth/login/')
def edit_profile(request):
    if request.method == "POST":
        try:
            r = cloudinary.uploader.upload(request.FILES['file'])
            img_url = r["secure_url"]
        except:
            pass

        try:
            p = Profile.objects.get(user_id=request.user.id)
            p.description = request.POST["desc"]
            p.organization = request.POST["org"]
            p.location = request.POST["loc"]
            p.website = request.POST["web"]
            try:
                p.avatar = img_url
                request.session["img"] = img_url
            except:
                pass
            p.save()
        except:
            try:
                p = Profile(user_id=request.user.id, description=request.POST["desc"], organization=request.POST["org"], location=request.POST["loc"], website=request.POST["web"], avatar=img_url)
            except:
                p = Profile(user_id=request.user.id, description=request.POST["desc"], organization=request.POST["org"], location=request.POST["loc"], website=request.POST["web"], avatar="https://iupac.org/wp-content/uploads/2018/05/default-avatar.png")
            p.save()

        return HttpResponseRedirect("/profile/")

    else:
        try:
            p = Profile.objects.get(user_id=request.user.id)
        except:
            p = []

        try:
            oauth = OAuth.objects.filter(user_id=request.user.id)
        except:
            oauth = []

        uris = {}
        for o in oauth:
            uris[o.client_id] = Uri.objects.filter(client_id=o.client_id)

        return render(request, "main/profile.html", {
            "p": p,
            "oauth": oauth,
            "uris": uris,
        })


@login_required(login_url='/auth/login/')
def follow_user(request):
    user = User.objects.get(username=request.GET["username"])
    f = Follows(user_id=request.user.id, following=user.id)
    f.save()

    print(f)

    return JsonResponse({"message": "success"})


@login_required(login_url='/auth/login/')
def unfollow_user(request):
    user = User.objects.get(username=request.GET["username"])
    print(request.user.id, user.id)
    Follows.objects.filter(user_id=request.user.id, following=user.id).delete()
    return JsonResponse({"message": "success"})


@login_required(login_url='/auth/login/')
def create_oauth_app(request):
    # app = OAuth(user_id=request.user.id, client_id=)
    if request.method == "POST":
        client_id = random_str(20)
        try:
            while True:
                OAuth.objects.get(client_id=client_id)
                client_id = random_str(20)
        except:
            pass

        app = OAuth(user_id=request.user.id, name=request.POST["name"], client_id=client_id,    client_secret=random_str(50))
        app.save()

        uris = request.POST["redirect_uri"].split(",")
        for i in uris:
            if validate_url(i):
                u = Uri(client_id=client_id, redirect_uri=i)
                u.save()

        return HttpResponseRedirect("/profile/")