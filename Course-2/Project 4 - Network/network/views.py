from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.http import JsonResponse
import json

from .models import *
from .forms import *


def index(request):
    posts = Post.objects.annotate(num_likes=Count('likes')).all().order_by('-timestamp')
    
    return render(request, "network/index.html", {
        "newPost": NewPost(),
        "posts": posts,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url='network:login')
def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    form = NewPost(request.POST)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        messages.success(request, 'Your post was sent to the world!')
        return HttpResponseRedirect(reverse('network:index'))

def like(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    postData = json.loads(request.body)
    post = Post.objects.get(pk=postData['id'])
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        post.save()
    else:
        post.likes.add(request.user)
        post.save()
    return JsonResponse({"response": "Success"}, status=200)

def profile(request, profile_name):
    user_info = User.objects.get(username=profile_name)
    posts = Post.objects.filter(author=user_info).annotate(num_likes=Count('likes')).all().order_by('-timestamp')
    num_posts = posts.count()
    return render(request, "network/profile.html", {
        'following': user_info.following.count(),
        'followers': user_info.follower.all().count(),
        'posts': posts,
        'num_posts': num_posts,
        'profile_name': profile_name,
    })