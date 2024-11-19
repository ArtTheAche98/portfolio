from django.contrib import admin
from .models import User, Listing, Bid, Comment, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request)

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category)