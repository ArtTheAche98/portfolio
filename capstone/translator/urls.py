from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Default index page
    path("translate", views.translate_term, name="translate_term"),  # Page for translating and defining terms
]