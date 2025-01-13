from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json

from .models import User, Post, Profile


def index(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "network/index.html", {
        "post": posts
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

@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if not content:
            return HttpResponseBadRequest("Content cannot be empty")

        created_at = request.POST.get("created_at", "")
        user = request.user
        image_url = request.POST.get("image_url", "").strip()
        if image_url and not image_url.startswith(("http://", "https://")):
            return HttpResponseBadRequest("Invalid image URL.")

        post = Post(created_at=created_at, content=content, author=user, image_url=image_url)
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect("invalid request method")

@login_required
def like_post(request, post_id):
    try:
        if request.method == "POST":
            post = get_object_or_404(Post, post_id=post_id)
            user = request.user

            if user in post.likes.all():
                post.likes.remove(user)
                liked=False
            else:
                post.likes.add(user)
                liked=True
        return JsonResponse({
            "success": True,
            "liked": liked,
            "likes_count": post.likes.count()
        })
    except Post.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Invalid request method."
        }, status=400)


@login_required
def all_posts(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/all_posts.html", {
        "page_obj": page_obj
    })

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@login_required
def profile_page(request, username):
    profile_user=get_object_or_404(User, username=username)
    profile=get_object_or_404(Profile, user=profile_user)
    is_following=request.user.profile in profile.followers.all()

    posts = Post.objects.filter(author=profile_user).order_by("-created_at")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "follow":
            profile.followers.add(request.user.profile)
        elif action == "unfollow":
            profile.followers.remove(request.user.profile)
        return JsonResponse({"success": True, "followers_count": profile.followers.count()})

    return render(request, "network/profile.html",{
        "profile_user": profile_user,
        "profile": profile,
        "is_following": is_following,
        "followers_count": profile.followers.count(),
        "following_count": profile.following.count(),
        "posts": page_obj
    })


@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile

    current_profile = request.user.profile

    if request.user == target_user:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)

    if target_profile in current_profile.following.all():
        current_profile.following.remove(target_profile)
        target_profile.followers.remove(current_profile)
        following = False
    else:
        current_profile.following.add(target_profile)
        target_profile.followers.add(current_profile)
        following = True

    return JsonResponse({
        'success': True,
        'following': following,
        'followers_count': target_profile.followers.count()
    })

@login_required
def edit(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()

            post = Post.objects.get(pk=post_id)
            if post.author != request.user:
                return JsonResponse({'success': False, 'error': 'Permission denied.'}, status=403)

            post.content = content
            post.save()

            return JsonResponse({'success': True})
        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def following(request):
    following_users = request.user.profile.following.values_list("user", flat=True)
    posts = Post.objects.filter(author__id__in=following_users).order_by("-created_at")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })