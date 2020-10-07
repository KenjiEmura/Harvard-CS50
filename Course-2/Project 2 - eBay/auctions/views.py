from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import *
from .forms import *


def auction(request, product_id, product_name):
    from django.db.models import Avg, Max, Min, Sum, Count
    from django.forms import modelform_factory
    import math

    # Get the product and the respective bids infromation
    product = Auction.objects.annotate(max_bid=Max('product_bids__bid')).get(pk=product_id)
    count_bid = Bid.objects.filter(product=product_id).count()
    cur_max_bid = product.max_bid

    # Function to calculate the step of the modelform (bid_form)
    def step(price): 
        i = 0
        while price/10 > 10:
            price /= 10
            i += 1
        return 10**(i-1)

    # Check if the product has already a bid, if not, the max bid is going to be the initial price of the auction
    if cur_max_bid is None:
        cur_max_bid = product.price

    # Prepopulate the MakeBid form
    step = math.ceil(step(cur_max_bid))
    bid_form = modelform_factory(Bid, form=MakeBid, widgets = {'bid': NumberInput(attrs={'min':cur_max_bid + step, 'class':'form-field bid','step':step})})

    if request.method == "GET":
        return render(request, "auctions/product.html", {
            "product": product,
            "makebid": bid_form,
            "count_bid": count_bid
        })
    elif request.method == "POST":
        form = MakeBid(request.POST)
        def success(form, product_id, posted_bid):
            messages.success(request, 'Your bid was successfuly received!')
            new_bid = form.save(commit=False)
            new_bid.product = Auction.objects.get(pk=product_id)
            new_bid.user = request.user
            new_bid.save()
            product.price = posted_bid
            product.save()
        if form.is_valid():
            from django.contrib import messages
            posted_bid = form.cleaned_data['bid']
            if posted_bid <= cur_max_bid:
                messages.error(request, f'Your bid has to be greater than ¥{cur_max_bid:,}')
                return HttpResponseRedirect(reverse('auctions:products', args=[ product_id, product_name ]))
            else:
                success(form, product_id, posted_bid)
                return HttpResponseRedirect(reverse('auctions:products', args=[ product_id, product_name ]))
        else:
            messages.error(request, 'An error posting the information occured!')
        return HttpResponseRedirect(reverse('auctions:products', args=[ product_id, product_name ]))


def create(request):
    if request.method == "POST":
        form = CreateProduct(request.POST)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.author = request.user
            new_product.save()
            return HttpResponseRedirect(reverse('auctions:products', args=[ new_product.id, new_product.name ]))
    elif request.method == "GET":
        return render(request, "auctions/create-listing.html", {
            "create_product": CreateProduct()
        })


def index(request):
    from django.db.models import Avg, Max, Min, Sum, Count

    return render(request, "auctions/index.html", {
        "auctions": Auction.objects.annotate(
            max_bid=Max('product_bids__bid'),
            bid_count=Count('product_bids'))
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
