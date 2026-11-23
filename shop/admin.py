from django.contrib import admin

from notifications.services import notify_subscribers

from .models import Album, Artist, Genre, Wishlist


class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "genre", "price", "in_stock")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change and "in_stock" in form.changed_data and obj.in_stock:
            notify_subscribers(obj)


admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Wishlist)
