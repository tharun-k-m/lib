# library/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# --- User Profile Model ---
class UserProfile(models.Model):
    """
    Extends the Django User model to include a bio and profile picture.
    A one-to-one relationship ensures each User has one UserProfile.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    # Changed from ImageField to CharField to avoid the Pillow dependency
    profile_picture = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username


# --- Book Catalog Models ---
class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Fantasy, etc.)."""
    name = models.CharField(max_length=200, unique=True,
                            help_text="Enter a book genre (e.g. Science Fiction)")

    def __str__(self):
        return self.name

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class Book(models.Model):
    """Model representing a book (not a specific copy)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    description = models.TextField(max_length=1000)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13 Character ISBN number')
    publish_year = models.IntegerField()
    # Changed from ImageField to CharField to avoid the Pillow dependency
    cover_image = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)
    is_sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# --- Book Action Models ---
class Lending(models.Model):
    """
    Model representing a book lending transaction.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_on = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-borrowed_on']
        # Ensure a user can only have one active loan per book at a time
        unique_together = ('user', 'book', 'returned')

    def __str__(self):
        return f'{self.user.username} borrowed {self.book.title}'




class Favorite(models.Model):
    """
    Model for tracking a user's favorite books.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    class Meta:
        # A user can only favorite a book once
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} favorited {self.book.title}'

class Purchase(models.Model):
    """
    Model for tracking a user's book purchases.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchased_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchased_on']
        # A user can only purchase a book once
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} purchased {self.book.title}'



# New Review model to be added
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], # Rating from 1 to 5
        help_text="Rate the book from 1 to 5 stars."
    )
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures a user can only review a specific book once
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
