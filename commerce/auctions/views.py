from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .models import User, Listing, Bid, Comment, Watchlist, Category


def index(request):
    auctions = Listing.objects.filter(is_active=True, current_price__isnull=False)
    return render(request, "auctions/index.html", {
        'listings': auctions
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
    
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories})


def category_listings(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    listings = Listing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category_listings.html", {
        'category': category,
        'listings': listings
    })

@login_required
def create_listing(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_price = request.POST["starting_price"]
        image_url = request.POST.get("image_url", "")
        category_id = request.POST.get("category")

        if not title or not description or not starting_price or not category_id:
            return render(request, "auctions/create_listing.html", {
                'categories': categories,
                'error': "Please fill in all required fields."
            })
        
        category = get_object_or_404(Category, id=category_id)

        item = Listing(
            title=title,
            description=description,
            starting_price = starting_price,
            current_price = starting_price,
            image_url=image_url,
            category=category,
            user=request.user,
        )
        item.save()
        return redirect("index")
    
    return render(request, "auctions/create_listing.html", {
        'categories': categories
    })

def auction_detail(request, auction_id):
    auction = get_object_or_404(Listing, id=auction_id)
    comments = auction.comment_set.all()
    highest_bid = auction.bid_set.order_by('-bid').first()

    if request.method == "POST" and request.user == auction.user and auction.is_active:
        auction.is_active = False
        auction.winner = highest_bid.user if highest_bid else None
        auction.save()

    return render(request, "auctions/auction_detail.html", {
        'auction': auction,
        'comments': comments,
        'hightst_bid': highest_bid,
        'is_winner': request.user == auction.winner if auction.winner else False
    })

@login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Listing, id=auction_id)
    if request.method == "POST":
        bid = float(request.POST["bid"])
        if bid > auction.current_price or auction.current_price is None:
            auction.current_price = bid
            auction.save()
            Bid.objects.create(user=request.user, listing=auction, bid=bid)
            return redirect("auction_detail", auction_id=auction_id)
        else:
            return render(request, "auctions/auction_detail.html", {
                "auction": auction,
                "error": "Your bid must be higher than the current price."
                })
    return redirect("auction_detail", auction_id=auction_id)

@login_required
def add_comment(request, auction_id):
    auction = get_object_or_404(Listing, id=auction_id)
    if request.method == "POST":
        comment = request.POST["comment"]
        comment = Comment(
            comment=comment,
            user=request.user,
            listing=auction,
            )
        comment.save()
        return redirect("auction_detail", auction_id=auction_id)
    return redirect("auction_detail", auction_id=auction_id)

@login_required
def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

@login_required
def add_to_watchlist(request, auction_id):
    auction = get_object_or_404(Listing, id=auction_id)
    watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, listing=auction)
    if created:
         messages.success(request, "Added to watchlist.")
    else:
        messages.info(request, "Already in watchlist.")
    return redirect("auction_detail", auction_id=auction_id)

@login_required
def remove_from_watchlist(request, auction_id):
    auction = get_object_or_404(Listing, id=auction_id)
    try:
        watchlist_item = Watchlist.objects.get(user=request.user, listing=auction)
        watchlist_item.delete()
        messages.success(request, "Removed from watchlist.")
    except Watchlist.DoesNotExist:
        messages.info(request, "Not in watchlist.")
    return redirect("auction_detail", auction_id=auction_id)


def active_listings(request):
    auctions = Listing.objects.all()
    return render(request, 'auctions/active_listings.html', {
        'auctions': auctions
        })