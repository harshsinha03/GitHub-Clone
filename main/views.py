from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
import GitHubClone.settings as settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.admin import User
from .models import Repository, File, Directory, Profile

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name = "boyuan12",
    api_key = "893778436618783",
    api_secret = "X4LufXPHxvv4hROS3VZWYyR3tIE"
)

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

    return render(request, "main/user.html", {
        "username": username,
        "tab": tab,
        "repos": repos,
        "user": user,
        "p": p
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
        return render(request, "main/profile.html", {
            "p": p
        })
