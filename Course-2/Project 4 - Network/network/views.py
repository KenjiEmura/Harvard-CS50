from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.http import JsonResponse
import json

from network.models import *
from network.forms import *


def index(request):
    posts = Post.objects.annotate(num_likes=Count('likes')).all().order_by('-timestamp')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    # If you want to manage the data and build a custom pagination module, send the total number of pages and the current page in a separate hidden input tag and handle that with JavaScript

    return render(request, "network/index.html", {
        "newPost": NewPost(),
        "page": page,
        "num_posts": paginator.count,
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
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


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
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


def new_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    form = NewPost(request.POST)
    if form.is_valid() and form.cleaned_data['post'] != '':
        form.cleaned_data['post']
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        messages.success(request, 'Your post was sent to the world!')
        return HttpResponseRedirect(reverse('network:index'))
    else:
        messages.error(request, "Your post was empty!")
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
    profile_user = User.objects.get(username=profile_name)
    posts = Post.objects.filter(author=profile_user).annotate(num_likes=Count('likes')).all().order_by('-timestamp')
    num_posts = posts.count()
    cur_user = User.objects.get(pk=request.user.id)
    if profile_user in cur_user.following.all():
        followed = True
    else:
        followed = False
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        'following': profile_user.following.count(),
        'followers': profile_user.follower.all().count(),
        'page': page,
        'num_posts': num_posts,
        'profile_name': profile_name,
        'followed': followed,
    })


# Follow/Unfollow functionality
def follow(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    data = json.loads(request.body)
    profile_user = User.objects.get(username=data['profile_name'])
    cur_user = User.objects.get(pk=request.user.id)
    if profile_user in cur_user.following.all():
        follow = False
        cur_user.following.remove(profile_user)
    else:
        follow = True
        cur_user.following.add(profile_user)
    return JsonResponse({"following": follow}, status=200)


# Render all the posts from people that user is following
@login_required(login_url='network:login')
def following(request):

    posts = Post.objects.filter(author__in=request.user.following.all()).annotate(num_likes=Count('likes')).all().order_by('-timestamp')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page": page,
        "num_posts": paginator.count,
    })

@login_required(login_url='network:login')
def edit_post(request, post_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=400)
    post = Post.objects.get(pk=post_id)
    if ( request.user == post.author):
        data = json.loads(request.body)
        post.post = data['post_content']
        post.save()
    else:
        return JsonResponse({"error": "The logged in user doesn't match the author of the post"}, status=403)
    return JsonResponse({"new_post_content": post.post}, status=200)