# library/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, Author, Genre, Book, Lending, Favorite, Purchase
)


# Inline for UserProfile to attach it directly to the User admin page
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    # Use a raw ID field for the user to prevent large dropdown menus
    # raw_id_fields = ('user',)


# Custom User Admin to include the UserProfile inline
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_bio', 'get_profile_picture')

    def get_bio(self, obj):
        return obj.userprofile.bio

    get_bio.short_description = 'Bio'

    def get_profile_picture(self, obj):
        return obj.userprofile.profile_picture

    get_profile_picture.short_description = 'Profile Picture'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# --- Custom Admin for Library Models ---

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'is_available', 'is_sold')
    list_filter = ('author', 'genre', 'is_available', 'is_sold')
    search_fields = ('title', 'author__first_name', 'author__last_name', 'isbn')
    # Use a raw ID field for the author to prevent large dropdown menus
    raw_id_fields = ('author',)


@admin.register(Lending)
class LendingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrowed_on', 'due_date', 'returned')
    list_filter = ('returned', 'borrowed_on')
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'book')
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'purchased_on')
    list_filter = ('purchased_on',)
    search_fields = ('user__username', 'book__title')
    raw_id_fields = ('user', 'book')
