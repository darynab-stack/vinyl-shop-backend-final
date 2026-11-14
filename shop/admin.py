from django.contrib import admin

from .models import Album, Artist, Genre, Wishlist


class AlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "genre", "price", "in_stock")


admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Wishlist)
