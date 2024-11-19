from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  
    path("login/", views.login_view, name="login"),  
    path("logout/", views.logout_view, name="logout"),  
    path("register/", views.register, name="register"), 
    path("create_listing/", views.create_listing, name="create_listing"),  
    path("auctions/<int:auction_id>/", views.auction_detail, name="auction_detail"), 
    path("auctions/<int:auction_id>/place_bid/", views.place_bid, name="place_bid"), 
    path("auctions/<int:auction_id>/add_comment/", views.add_comment, name="add_comment"),  
    path("watchlist/", views.watchlist, name="watchlist"),  
    path("watchlist/add/<int:auction_id>/", views.add_to_watchlist, name="add_to_watchlist"), 
    path('watchlist/remove/<int:auction_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path("auctions/active/", views.active_listings, name='active_listings'), 
    path("categories/", views.categories, name="categories"), 
    path(" categories/<int:category_id>/", views.category_listings, name="category_listings"),
]