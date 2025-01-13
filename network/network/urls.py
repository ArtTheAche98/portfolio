from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("index", views.index, name="index"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("user/<str:username>/", views.profile_page, name="profile"),
    path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("edit-post/<int:post_id>/", views.edit, name='edit'),
    path("following/",views.following,name='following'),
]
